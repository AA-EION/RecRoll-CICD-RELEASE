#!/usr/bin/env python3
"""Check release-manifest.json before and after a release is published.

Every public release here MUST carry release-manifest.json, generated in the
product repository by tools/make_release_manifest.py. The plug-in store and
the EION Studios Launcher read only that file to learn which platforms the
release has and each installer's size and SHA-256; a platform it does not list
is shown as not available, and a release whose manifest does not match its
files is rejected by the store.

    # the folder about to be uploaded (run by verify_public_payload.sh)
    python3 scripts/verify_release_manifest.py --dir <release-files-dir> --product PRODUCT [--tag TAG]

    # adding an installer to a published release: the folder holds the new
    # installer and the regenerated manifest only
    python3 scripts/verify_release_manifest.py --dir <folder> --product PRODUCT --adding

    # a release already on GitHub (uses GITHUB_TOKEN when set)
    python3 scripts/verify_release_manifest.py --github TAG --repo OWNER/NAME --product PRODUCT

Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MANIFEST = "release-manifest.json"
PLATFORMS = {"windows", "macos", "linux"}
ARCHES = {"universal", "x64", "arm64"}
KINDS = {"inno", "msi", "dmg", "pkg", "appimage", "deb", "rpm", "tar"}
INSTALLER = re.compile(r"\.(exe|msi|dmg|pkg|appimage|deb|rpm|tar\.gz|tar\.xz)$", re.IGNORECASE)
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


def schema_problems(m: dict, product: str | None, tag: str | None) -> list[str]:
    problems = []
    if m.get("schemaVersion") != 2:
        problems.append(f"schemaVersion is {m.get('schemaVersion')!r}; it must be 2 (regenerate with tools/make_release_manifest.py)")
        return problems
    if product and m.get("product") != product:
        problems.append(f"product is {m.get('product')!r}, this repository publishes {product!r}")
    if not m.get("name"):
        problems.append("name is missing")
    if not VERSION.fullmatch(str(m.get("version", ""))):
        problems.append(f"version {m.get('version')!r} is not x.y.z")
    if tag is not None and str(m.get("version")) != tag.removeprefix("v"):
        problems.append(f"version {m.get('version')} does not match the release tag {tag}")
    if not m.get("releasedAt"):
        problems.append("releasedAt is missing")
    cl = m.get("changelog") or {}
    if not cl.get("en") or not cl.get("es"):
        problems.append("changelog.en and changelog.es are both required")
    artifacts = m.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        problems.append("artifacts is empty: a release needs at least one installer")
        return problems
    seen = set()
    for a in artifacts:
        name = a.get("file")
        if not isinstance(name, str) or not name or "/" in name or "\\" in name:
            problems.append(f"bad file name {name!r}")
            continue
        if name in seen:
            problems.append(f"{name} is listed twice")
        seen.add(name)
        if a.get("platform") not in PLATFORMS:
            problems.append(f"{name}: platform {a.get('platform')!r} is not windows, macos or linux")
        if a.get("arch") not in ARCHES:
            problems.append(f"{name}: arch {a.get('arch')!r} is not universal, x64 or arm64")
        if a.get("kind") not in KINDS:
            problems.append(f"{name}: kind {a.get('kind')!r} is unknown")
        if not isinstance(a.get("size"), int) or a["size"] < 1:
            problems.append(f"{name}: size must be a positive integer")
        if not re.fullmatch(r"[0-9a-f]{64}", str(a.get("sha256", ""))):
            problems.append(f"{name}: sha256 must be 64 lowercase hex digits")
    return problems


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_dir(directory: Path, product: str | None, tag: str | None, adding: bool = False) -> list[str]:
    path = directory / MANIFEST
    if not path.is_file():
        return [f"{MANIFEST} is missing from {directory}: generate it in the product repository with tools/make_release_manifest.py"]
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"{MANIFEST} is not valid JSON: {e}"]
    problems = schema_problems(m, product, tag)
    listed = {a.get("file"): a for a in m.get("artifacts") or [] if isinstance(a, dict)}
    for name, a in listed.items():
        f = directory / str(name)
        if not f.is_file():
            if not adding:
                problems.append(f"{name} is listed but not in the folder (use --adding if it is already attached to the release)")
        elif f.stat().st_size != a.get("size"):
            problems.append(f"{name} is {f.stat().st_size} bytes, the manifest says {a.get('size')}")
        elif sha256(f) != a.get("sha256"):
            problems.append(f"{name}: SHA-256 differs from the manifest")
    for f in sorted(directory.iterdir()):
        if f.is_file() and INSTALLER.search(f.name) and f.name not in listed:
            problems.append(f"{f.name} is not in the manifest: regenerate it with this installer included")
    return problems


def api(url: str, accept: str = "application/vnd.github+json", auth: bool = True) -> bytes:
    headers = {"Accept": accept, "User-Agent": "release-manifest-check", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and auth:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return r.read(2 * 1024 * 1024)


def check_github(repo: str, tag: str, product: str | None) -> list[str]:
    try:
        release = json.loads(api(f"https://api.github.com/repos/{repo}/releases/tags/{tag}"))
    except urllib.error.HTTPError as e:
        return [f"release {tag} of {repo}: GitHub answered {e.code}"]
    assets = {a["name"]: a for a in release.get("assets", [])}
    if MANIFEST not in assets:
        return [f"release {tag} has no {MANIFEST}: the store and the Launcher will not offer it. Upload one generated with tools/make_release_manifest.py"]
    try:
        # The public download URL, without credentials: the redirect target
        # refuses a request that carries a GitHub token.
        m = json.loads(api(assets[MANIFEST]["browser_download_url"], accept="application/octet-stream", auth=False))
    except (urllib.error.HTTPError, json.JSONDecodeError) as e:
        return [f"{MANIFEST} could not be read: {e}"]
    problems = schema_problems(m, product, tag)
    listed = {a.get("file"): a for a in m.get("artifacts") or [] if isinstance(a, dict)}
    for name, a in listed.items():
        asset = assets.get(name)
        if asset is None:
            problems.append(f"{name} is listed but not attached to the release")
            continue
        if asset.get("size") != a.get("size"):
            problems.append(f"{name} is {asset.get('size')} bytes on GitHub, the manifest says {a.get('size')}")
        digest = str(asset.get("digest") or "")
        if digest.startswith("sha256:") and digest[7:] != a.get("sha256"):
            problems.append(f"{name}: GitHub's SHA-256 differs from the manifest")
    for name in assets:
        if INSTALLER.search(name) and name not in listed:
            problems.append(f"{name} is attached but not in the manifest: regenerate the manifest and upload it again")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    where = ap.add_mutually_exclusive_group(required=True)
    where.add_argument("--dir", type=Path, help="folder about to be uploaded")
    where.add_argument("--github", metavar="TAG", help="a published release's tag")
    ap.add_argument("--repo", help="OWNER/NAME, with --github (default: $GITHUB_REPOSITORY)")
    ap.add_argument("--product", help="the product id this repository publishes")
    ap.add_argument("--tag", help="with --dir: the tag the release will get")
    ap.add_argument(
        "--adding",
        action="store_true",
        help="with --dir: the folder holds only installers being added to a published release; "
        "listed files already attached are not required here (check the release with --github afterwards)",
    )
    args = ap.parse_args()

    if args.github:
        repo = args.repo or os.environ.get("GITHUB_REPOSITORY")
        if not repo:
            ap.error("--repo is required with --github")
        problems = check_github(repo, args.github, args.product)
        subject = f"{repo} {args.github}"
    else:
        problems = check_dir(args.dir, args.product, args.tag, args.adding)
        subject = str(args.dir)

    for p in problems:
        print(f"FAIL  {p}", file=sys.stderr)
    if problems:
        print(f"{MANIFEST} check failed for {subject}.", file=sys.stderr)
        return 1
    print(f"PASS  {MANIFEST} matches {subject}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
