import sys
import importlib.metadata
import re

required = [
    "google-auth>=2.23.0",
    "google-auth-oauthlib>=1.0.0",
    "google-api-python-client>=2.108.0",
    "pypdf>=3.17.0",
    "pdfplumber>=0.10.0",
    "python-dateutil>=2.8.2",
    "requests>=2.31.0",
]

def parse_version(v_str):
    return tuple(map(int, re.findall(r'\d+', v_str)))

missing = False
for req in required:
    match = re.match(r'^([a-zA-Z0-9\-_]+)(>=|==)?(.*)$', req)
    if not match:
        continue
    pkg_name, op, req_version = match.groups()
    try:
        installed_version = importlib.metadata.version(pkg_name)
        if op == '>=':
            if parse_version(installed_version) < parse_version(req_version):
                print(f"[VERSION ERROR] {pkg_name} installed version {installed_version} is less than required {req_version}")
                missing = True
            else:
                print(f"[OK]   {req} (Installed: {installed_version})")
        else:
            print(f"[OK]   {req} (Installed: {installed_version})")
    except importlib.metadata.PackageNotFoundError:
        print(f"[MISSING] {pkg_name}")
        missing = True

sys.exit(1 if missing else 0)