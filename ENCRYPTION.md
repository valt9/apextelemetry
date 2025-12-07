Encryption and Key Setup

Purpose
- Explain how to generate and provide keys for encrypting `username` and `email` and for deterministic HMAC lookup.

Design summary
- Passwords: still hashed with bcrypt (non-reversible) — no change.
- Lookup: deterministic HMAC (SHA-256) stored in `username_hmac` and `email_hmac` to allow queries (login/uniqueness checks).
- Storage: actual `username` and `email` are stored encrypted using Fernet (symmetric encryption) in `username_encrypted` and `email_encrypted`.

Required environment variables
- `FERNET_KEY` (required): the Fernet key used to encrypt/decrypt `username` and `email`.
- `HMAC_KEY` (optional): key used to compute deterministic HMACs. If not provided, `FERNET_KEY` is used for HMAC as a fallback. Using a separate `HMAC_KEY` is recommended.

Generate keys (PowerShell)
```powershell
# Generate a Fernet key (base64 url-safe 32 bytes)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Optionally generate a separate HMAC key (random base64 string)
python - <<'PY'
import os, base64
print(base64.urlsafe_b64encode(os.urandom(32)).decode())
PY
```

Set keys in PowerShell (example)
```powershell
$env:FERNET_KEY = '<paste-generated-fernet-key-here>'
$env:HMAC_KEY = '<paste-hmac-key-here>'
```

Install dependencies
```powershell
python -m pip install -r requirements.txt
```

Run the app locally (example)
```powershell
python c:\Users\aldus\Desktop\Apex Telemetry\app.py
```

Testing flow (no migration)
1. Ensure `FERNET_KEY` (and optionally `HMAC_KEY`) are set in your environment.
2. Start the app.
3. Register a new user via the `/register` page. The app will store HMACs and encrypted values automatically.
4. Log in with the created username/password.
5. Optional: Inspect the SQLite DB (e.g., using `sqlite3 apex_telemetry.db`) to verify `username_hmac`, `username_encrypted`, etc.

Migration note (skipped)
- This repository change stores encrypted fields and HMACs in new columns. Existing users in a pre-change DB will not be automatically migrated by the current commit.
- If you want a migration script to convert existing plaintext `username`/`email` columns into the new encrypted columns, I can add a one-time migration script and run it for you. This should only be executed after backing up the DB.

Migration script
- A helper script has been added at: `scripts/migrate_users_encrypt.py`.
- Usage example (from project root):
```powershell
python scripts/migrate_users_encrypt.py --db-path apex_telemetry.db
```
- The script creates a backup `apex_telemetry.db.bak` by default. Use `--no-backup` to skip.
- The script will add the new columns if missing and populate them from existing plaintext `username`/`email` values.

Security notes
- Keep `FERNET_KEY` and `HMAC_KEY` secret and do not commit them to source control.
- In production, place keys in a secure secret manager or environment configuration for your host provider.
- Consider rotating keys carefully: rotating `FERNET_KEY` will require decrypting and re-encrypting stored values; rotating `HMAC_KEY` will break deterministic lookup unless you store multiple HMACs or re-hash all records.

If you want, I can now:
- Add a migration script to convert existing user rows (one-time) and mark that TODO complete.
- Or create a short `SECURITY.md` describing recommended deployment practices.
