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

## Testing a change

Changes can be checked locally:

```bash
./scripts/guard_no_source.sh
python3 -m py_compile scripts/*.py
for f in scripts/*.sh; do bash -n "$f"; done
```
