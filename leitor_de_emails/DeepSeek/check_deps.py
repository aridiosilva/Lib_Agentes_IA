import pkg_resources, sys
required = [
    "google-auth>=2.23.0",
    "google-auth-oauthlib>=1.0.0",
    "google-api-python-client>=2.108.0",
    "pypdf>=3.17.0",
    "pdfplumber>=0.10.0",
    "python-dateutil>=2.8.2",
    "requests>=2.31.0",
]
missing = False
for req in required:
    try:
        pkg_resources.require(req)
        print(f"[OK]   {req}")
    except Exception as e:
        print(f"[MISSING] {req} → {e}")
        missing = True
sys.exit(1 if missing else 0)