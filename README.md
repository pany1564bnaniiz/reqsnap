# reqsnap

Lightweight HTTP request logger and diff tool for comparing API responses across environments.

---

## Installation

```bash
pip install reqsnap
```

---

## Usage

Capture a request snapshot and compare responses across environments:

```python
from reqsnap import snap, diff

# Snap a request
response = snap("https://api.staging.example.com/users/1", tag="staging")

# Compare staging vs production
result = diff(
    "https://api.staging.example.com/users/1",
    "https://api.production.example.com/users/1"
)

print(result.summary())
# ✔ Status codes match: 200
# ✗ Body diff detected: 3 fields changed
```

You can also use the CLI:

```bash
# Log a request
reqsnap snap https://api.example.com/endpoint --tag v1

# Diff two environments
reqsnap diff https://api.staging.example.com/health https://api.prod.example.com/health
```

Snapshots are saved locally as JSON files and can be replayed or compared at any time.

---

## Features

- 📸 Snapshot HTTP responses with metadata
- 🔍 Diff response bodies, headers, and status codes
- 🗂 Tag and organize snapshots by environment or version
- 🖥 Simple CLI and Python API

---

## License

MIT © [reqsnap contributors](LICENSE)