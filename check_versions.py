#!/usr/bin/env python3
"""
🔍 Version Compatibility Checker
Ensures all dependencies are up-to-date and compatible
Run before deployment: python check_versions.py
"""

import sys
import subprocess
import json
from datetime import datetime

# Minimum required versions for future-proofing
REQUIRED_VERSIONS = {
    "python": "3.10.0",
    "pip": "24.0",
    "docker": "24.0.0"
}

# Critical dependencies to monitor
CRITICAL_PACKAGES = [
    "hydrogram",
    "pymongo",
    "aiohttp",
    "uvloop"
]

def get_python_version():
    """Get current Python version"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_pip_version():
    """Get current pip version"""
    try:
        result = subprocess.run(
            ["pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.split()[1]
        return version
    except Exception:
        return "Unknown"

def get_docker_version():
    """Get Docker version"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.split()[2].rstrip(',')
        return version
    except Exception:
        return "Not installed"

def check_outdated_packages():
    """Check for outdated Python packages"""
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        outdated = json.loads(result.stdout)
        return outdated
    except Exception:
        return []

def compare_versions(current, required):
    """Compare version strings"""
    current_parts = [int(x) for x in current.split('.')]
    required_parts = [int(x) for x in required.split('.')]
    
    for c, r in zip(current_parts, required_parts):
        if c < r:
            return False
        elif c > r:
            return True
    return True

def main():
    print("=" * 60)
    print("🔍 VERSION COMPATIBILITY CHECK")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_good = True
    
    # Check Python version
    python_version = get_python_version()
    python_ok = compare_versions(python_version, REQUIRED_VERSIONS["python"])
    status = "✅" if python_ok else "❌"
    print(f"{status} Python: {python_version} (Required: {REQUIRED_VERSIONS['python']}+)")
    if not python_ok:
        all_good = False
    
    # Check pip version
    pip_version = get_pip_version()
    pip_ok = compare_versions(pip_version, REQUIRED_VERSIONS["pip"]) if pip_version != "Unknown" else False
    status = "✅" if pip_ok else "⚠️"
    print(f"{status} pip: {pip_version} (Required: {REQUIRED_VERSIONS['pip']}+)")
    if not pip_ok:
        print("   → Upgrade: pip install --upgrade pip")
    
    # Check Docker version
    docker_version = get_docker_version()
    docker_ok = compare_versions(docker_version, REQUIRED_VERSIONS["docker"]) if docker_version != "Not installed" else False
    status = "✅" if docker_ok else "⚠️"
    print(f"{status} Docker: {docker_version} (Required: {REQUIRED_VERSIONS['docker']}+)")
    
    print()
    print("-" * 60)
    
    # Check for outdated packages
    print("📦 Checking for outdated packages...")
    outdated = check_outdated_packages()
    
    if outdated:
        print(f"⚠️  Found {len(outdated)} outdated package(s):")
        for pkg in outdated:
            name = pkg['name']
            current = pkg['version']
            latest = pkg['latest_version']
            critical = "🔴" if name in CRITICAL_PACKAGES else "  "
            print(f"   {critical} {name}: {current} → {latest}")
        print()
        print("   Upgrade all: pip install --upgrade -r requirements.txt")
    else:
        print("✅ All packages are up-to-date!")
    
    print()
    print("=" * 60)
    
    if all_good and not outdated:
        print("🎉 EVERYTHING IS UP-TO-DATE AND COMPATIBLE!")
        print("✅ Ready for deployment")
        return 0
    else:
        print("⚠️  SOME UPDATES RECOMMENDED")
        print("   Review the issues above before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
