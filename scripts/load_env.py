import json
import os
import shutil
import subprocess
import sys

def decrypt_config():
    raw_key = os.environ.get("CONFIG_KEY", "")
    if not raw_key:
        sys.stderr.write("::error::Missing CONFIG_KEY secret.\n")
        sys.exit(1)

    candidates = [
        raw_key.strip(),
        raw_key.strip().strip("'\""),
        raw_key,
        raw_key.rstrip("\r\n"),
    ]

    openssl_bin = shutil.which("openssl")
    if not openssl_bin:
        for fallback in [
            "C:\\Program Files\\Git\\usr\\bin\\openssl.exe",
            "/usr/bin/openssl",
            "/usr/local/bin/openssl",
        ]:
            if os.path.isfile(fallback):
                openssl_bin = fallback
                break

    if not openssl_bin:
        sys.stderr.write("::error::openssl binary not found.\n")
        sys.exit(1)

    enc_file = os.path.join(os.path.dirname(__file__), "config.enc")
    if not os.path.isfile(enc_file):
        enc_file = "scripts/config.enc"

    seen = set()
    last_err = ""
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        for extra_flags in [["-md", "sha256"], []]:
            cmd = [
                openssl_bin,
                "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "100000",
                *extra_flags,
                "-in", enc_file,
                "-pass", "stdin"
            ]
            p = subprocess.run(cmd, input=candidate.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode == 0 and p.stdout:
                try:
                    return json.loads(p.stdout.decode("utf-8"))
                except Exception:
                    pass
            elif p.stderr:
                last_err = p.stderr.decode("utf-8", "ignore").strip()

            os.environ["_CONFIG_CANDIDATE"] = candidate
            cmd_env = [
                openssl_bin,
                "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "100000",
                *extra_flags,
                "-in", enc_file,
                "-pass", "env:_CONFIG_CANDIDATE"
            ]
            p_env = subprocess.run(cmd_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.environ.pop("_CONFIG_CANDIDATE", None)
            if p_env.returncode == 0 and p_env.stdout:
                try:
                    return json.loads(p_env.stdout.decode("utf-8"))
                except Exception:
                    pass
            elif p_env.stderr:
                last_err = p_env.stderr.decode("utf-8", "ignore").strip()

    detail = f" ({last_err})" if last_err else ""
    sys.stderr.write(f"::error::Failed to decrypt configuration with CONFIG_KEY{detail}. Please verify the secret in repository settings.\n")
    sys.exit(1)

def main():
    config = decrypt_config()

    vars_raw = os.environ.get("VARS_RAW", "{}")
    try:
        variables = json.loads(vars_raw) if vars_raw else {}
    except Exception:
        variables = {}

    env_file = os.environ.get("GITHUB_ENV")

    def export_var(name, val):
        if val is None:
            return
        val_str = str(val)
        if "\n" in val_str:
            delimiter = "ENV_DELIMITER_TOKEN"
            entry = f"{name}<<{delimiter}\n{val_str}\n{delimiter}\n"
        else:
            entry = f"{name}={val_str}\n"

        if env_file:
            with open(env_file, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            sys.stdout.write(entry)

    for key, val in config.get("static_env", {}).items():
        if val and any(s in key.lower() for s in ["token", "secret", "password", "key", "cert", "guid", "pfx", "p12"]):
            for line in str(val).splitlines():
                if line.strip():
                    sys.stdout.write(f"::add-mask::{line.strip()}\n")
        export_var(key, val)

    if "RECROLL_SOURCE_TOKEN" in config.get("static_env", {}):
        export_var("SOURCE_TOKEN", config["static_env"]["RECROLL_SOURCE_TOKEN"])
    if "KUROKO_SOURCE_TOKEN" in config.get("static_env", {}):
        export_var("CLIENT_TOKEN", config["static_env"]["KUROKO_SOURCE_TOKEN"])

    gw = os.environ.get("GITHUB_WORKSPACE")
    if gw:
        export_var("KUROKO_SOURCE_DIR", os.path.join(gw, "kuroko").replace("\\", "/"))

    for key in config.get("var_keys", []):
        val = variables.get(key)
        if val:
            export_var(key, val)

    missing = []
    for req in config.get("required", []):
        val = None
        if req in config.get("static_env", {}):
            val = config["static_env"][req]
        elif req in variables and variables[req]:
            val = variables[req]
        elif os.environ.get(req):
            val = os.environ.get(req)

        if not val:
            missing.append(req)

    if missing:
        sys.stderr.write(f"::error::Required configuration or credential missing: {missing[0]}\n")
        sys.exit(1)

    sys.stdout.flush()

if __name__ == "__main__":
    main()
