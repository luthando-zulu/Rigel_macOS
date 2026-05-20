#!/usr/bin/env python3
"""
RIGEL Business v4.1.0 - Prototype Verification Script
Tests all major components before the presentation
"""

import sys
import os
from pathlib import Path

# Ensure workspace root is on the path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def test_imports():
    """Test all critical imports"""
    print("=" * 70)
    print("RIGEL BUSINESS v4.1.0 - PROTOTYPE VERIFICATION")
    print("=" * 70)
    print()
    
    print("[1/5] Testing core imports...")
    try:
        from accounting import CHART_OF_ACCOUNTS, AccountingLedger
        print(f"    ✓ Accounting module loaded")
        print(f"    ✓ Chart of Accounts: {len(CHART_OF_ACCOUNTS)} accounts")
    except Exception as e:
        print(f"    ✗ Failed to import accounting: {e}")
        return False
    
    print()
    print("[2/5] Testing installation wizard...")
    try:
        from installation.installation_wizard import license_manager, InstallConstants
        print(f"    ✓ Installation wizard loaded")
        print(f"    ✓ License manager initialized")
        print(f"    ✓ App version: {InstallConstants.APP_VERSION}")
    except Exception as e:
        print(f"    ✗ Failed to import installation wizard: {e}")
        return False
    
    print()
    print("[3/5] Testing registration handler...")
    try:
        # We can't instantiate without Qt, but we can import
        import registration.registration_handler
        print(f"    ✓ Registration handler module loaded")
    except Exception as e:
        print(f"    ✗ Failed to import registration handler: {e}")
        return False
    
    print()
    print("[4/5] Testing rigel_core...")
    try:
        import rigel_pyqt6.rigel_core
        print(f"    ✓ Main application core loaded")
        from rigel_pyqt6.rigel_core import launch_application
        print(f"    ✓ Application launcher available")
    except Exception as e:
        print(f"    ✗ Failed to import rigel_core: {e}")
        return False
    
    print()
    print("[5/5] Testing chart of accounts content...")
    try:
        coa_sample = list(CHART_OF_ACCOUNTS.items())[:5]
        print(f"    ✓ Sample COA entries loaded:")
        for code, account in coa_sample:
            print(f"        {code}: {account['name']} ({account['type']})")
    except Exception as e:
        print(f"    ✗ Failed to sample COA: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✓ ALL COMPONENTS VERIFIED SUCCESSFULLY")
    print("=" * 70)
    print()
    print("Ready to launch! Run: python run_rigel.py")
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
