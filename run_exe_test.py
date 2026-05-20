#!/usr/bin/env python3
"""Quick test of the built exe to capture any immediate import errors."""
import subprocess
import sys
import os

exe = r'C:\Users\zulub\Downloads\rigel_pyqt6\dist\RIGEL_Business_Trial.exe'
if not os.path.exists(exe):
    print(f"ERROR: {exe} not found")
    sys.exit(1)

print(f"Testing: {exe}")
print("Attempting to run with 10-second timeout...")
print("If it hangs waiting for UI, that's expected.")
print("-" * 60)

try:
    # Run with offscreen to avoid display issues; capture output
    env = os.environ.copy()
    env['QT_QPA_PLATFORM'] = 'offscreen'
    result = subprocess.run(
        [exe],
        capture_output=True,
        text=True,
        timeout=12,
        env=env,
        cwd=r'C:\Users\zulub\Downloads\rigel_pyqt6'
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except subprocess.TimeoutExpired as e:
    print("TIMEOUT - Application likely waiting for user interaction (good)")
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
except Exception as e:
    print("EXCEPTION:", e)
