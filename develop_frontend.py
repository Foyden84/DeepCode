#!/usr/bin/env python3
"""
Frontend Dashboard Agent Development Script

This script provides the development environment for the frontend component of ICRA.
"""

import os
import sys
from pathlib import Path

# Add the main workspace to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "workspace"))

def main():
    print("=" * 60)
    print(f"Frontend Dashboard Agent Development Environment")
    print("=" * 60)
    print(f"Working Directory: {Path.cwd()}")
    print(f"Branch: feature/icra-frontend-dashboard")
    print(f"Focus: Interactive UI, real-time collaboration, code visualization")
    print()
    print("Instructions available in: frontend_instructions.md")
    print()
    print("Ready for development!")
    print("=" * 60)

if __name__ == "__main__":
    main()
