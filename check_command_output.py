#!/usr/bin/env python3
"""Check command output capture"""
import subprocess
import sys

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return {
            'success': True,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'stdout': e.stdout.strip(),
            'stderr': e.stderr.strip(),
            'returncode': e.returncode,
            'error': str(e)
        }

def main():
    """Main function"""
    # Test basic command
    print("Testing command execution...")
    result = run_command("echo 'Hello, World!'")
    
    if result['success']:
        print("✅ Command executed successfully")
        print(f"Output: {result['stdout']}")
    else:
        print(f"❌ Command failed: {result.get('error', 'Unknown error')}")
        if result['stderr']:
            print(f"Error output: {result['stderr']}")
    
    # Test Python version
    print("\nTesting Python version...")
    result = run_command("python --version")
    if result['success']:
        print(f"✅ {result['stdout']}")
    else:
        print(f"❌ Could not get Python version: {result.get('error', 'Unknown error')}")
    
    # Test directory listing
    print("\nTesting directory listing...")
    result = run_command("ls -la")
    if result['success']:
        print("✅ Directory listing successful")
        print("First few items:")
        for line in result['stdout'].split('\n')[:5]:
            print(f"  {line}")
    else:
        print(f"❌ Directory listing failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
