import json
import os
import sys

def main():
    try:
        config = json.load(sys.stdin)
    except Exception as e:
        sys.stderr.write(f"::error::Failed to parse configuration: {e}\n")
        sys.exit(1)

    secrets_raw = os.environ.get("SECRETS_RAW", "{}")
    vars_raw = os.environ.get("VARS_RAW", "{}")

    try:
        secrets = json.loads(secrets_raw) if secrets_raw else {}
    except Exception:
        secrets = {}

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
        export_var(key, val)

    for key in config.get("secret_keys", []):
        val = secrets.get(key)
        if val:
            for line in str(val).splitlines():
                if line.strip():
                    sys.stdout.write(f"::add-mask::{line.strip()}\n")
            export_var(key, val)

    for key in config.get("var_keys", []):
        val = variables.get(key)
        if val:
            export_var(key, val)

    missing = []
    for req in config.get("required", []):
        val = None
        if req in config.get("static_env", {}):
            val = config["static_env"][req]
        elif req in secrets and secrets[req]:
            val = secrets[req]
        elif req in variables and variables[req]:
            val = variables[req]
        elif os.environ.get(req):
            val = os.environ.get(req)

        if not val:
            missing.append(req)

    if missing:
        sys.stderr.write("::error::Required build credentials or configuration missing.\n")
        sys.exit(1)

    sys.stdout.flush()

if __name__ == "__main__":
    main()
