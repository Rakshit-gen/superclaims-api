#!/usr/bin/env python3

import os
from pathlib import Path

def print_tree(directory, prefix="", max_depth=3, current_depth=0):
    if current_depth >= max_depth:
        return
    
    try:
        entries = sorted(Path(directory).iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return
    
    entries = [e for e in entries if not e.name.startswith('.') and e.name not in ['__pycache__', 'venv', 'env']]
    
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{entry.name}")
        
        if entry.is_dir():
            extension_prefix = "    " if is_last else "│   "
            print_tree(entry, prefix + extension_prefix, max_depth, current_depth + 1)

if __name__ == "__main__":
    print("SuperClaims Backend - Project Structure")
    print("=" * 50)
    print("superclaims-backend/")
    print_tree(".", max_depth=3)
    print("\n✓ Project structure generated successfully!")
