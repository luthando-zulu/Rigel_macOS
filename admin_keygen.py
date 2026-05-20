"""
RIGEL Business — Admin License Key Generator
Run ONLY on your secure admin machine. Never distribute this file.

Usage:
  python3 admin_keygen.py

Then enter the customer's Machine ID (shown in their activation dialog)
and the script outputs the RIGEL-XXXX-XXXX-XXXX-XXXX key to email them.
"""

import hashlib
import sys

# !! MUST MATCH SECRET_SALT in rigel_core.py !!
SECRET_SALT = "TestRigel#2026_Dev$Salt!XZ9q"   # ← update before production


def generate_key(machine_id: str) -> str:
    raw    = f"{machine_id}|{SECRET_SALT}".encode()
    digest = hashlib.sha256(raw).hexdigest().upper()
    parts  = [digest[i:i+4] for i in range(0, 16, 4)]
    return "RIGEL-" + "-".join(parts)


def main():
    print("\n" + "="*55)
    print("  RIGEL Business — Admin License Key Generator")
    print("  Stella Lumen (Pty) Ltd")
    print("="*55 + "\n")
    print("  ⚠  Keep this script private. Never share it.\n")

    mid = input("  Enter customer Machine ID: ").strip()
    if len(mid) < 16:
        print("  ERROR: Machine ID looks too short.")
        sys.exit(1)

    key = generate_key(mid)
    print(f"\n  ✓  License Key: {key}")
    print(f"\n  Email this key to the customer in the format:")
    print(f"  RIGEL-XXXX-XXXX-XXXX-XXXX\n")
    print("="*55 + "\n")


if __name__ == "__main__":
    main()
