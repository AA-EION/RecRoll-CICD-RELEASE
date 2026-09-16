# Notes for AI agents working in this repository

## Overview

Public release runners. This repository contains workflows, guard scripts and release configuration. **It contains no application code and must never contain any.**

## The layout rule

**Never add application or packaging code here.**

That includes `.cpp`, `.h`, `.mm`, `CMakeLists.txt`, `.cmake`, `.iss`, `.wxs`, project files, `Source/`, `Resources/`, `installer/`, `libs/`, and any certificate or key.

`scripts/guard_no_source.sh` enforces this on every push and pull request. Run it before you commit:

```bash
./scripts/guard_no_source.sh
```

## Configuration & Decryption

All internal configuration, repository targets, and operational settings are stored in an encrypted payload.

To understand the configuration, inspect the environment, or make sense of the pipeline:
1. **Ask the user for the decryption password.** Do not attempt to guess or brute force.
2. Once the user provides the password, use it to decrypt the configuration file locally in context to inspect operational parameters.
3. **Never** hardcode, commit, or push decrypted values, secret names, variable names, repository paths, or links into this repository.
4. Keep the repository completely sanitized at all times.

## Testing a change

Changes can be checked locally:

```bash
./scripts/guard_no_source.sh
python3 -m py_compile scripts/*.py
for f in scripts/*.sh; do bash -n "$f"; done
```
