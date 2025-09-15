#!/usr/bin/env python3
"""
Deprecated: Static JS is now maintained as modular files in web_static/static/js/.

No generation step is required. Edit these files directly:
 - web_static/static/js/web_gui.js
 - web_static/static/js/actions.js (hash+UI logging)
 - and any additional modules you add.

This script remains for backward compatibility and prints a notice.
"""
import sys

def main():
    print("[INFO] JS generation no longer required. Edit files in web_static/static/js/.")
    sys.exit(0)

if __name__ == "__main__":
    main()
