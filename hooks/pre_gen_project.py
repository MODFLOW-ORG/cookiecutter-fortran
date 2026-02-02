#!/usr/bin/env python
"""Pre-generation hook for cookiecutter-fortran."""

import re
import sys


def validate_name(name):
    """Validate that program name is suitable for a directory/package name."""
    if not re.match(r'^[a-z][a-z0-9_-]*$', name):
        print("ERROR: name must:")
        print("  - Start with a lowercase letter")
        print("  - Contain only lowercase letters, numbers, hyphens, and underscores")
        print(f"  Got: {name}")
        sys.exit(1)


def validate_version(version):
    """Validate that version follows semantic versioning."""
    # Allow versions like 1.0.0, 1.2.3, 1.19.01, 4.00.05
    if not re.match(r'^\d+(\.\d+)*$', version):
        print("ERROR: version must follow format: X.Y.Z (e.g., 1.0.0, 1.19.01)")
        print(f"  Got: {version}")
        sys.exit(1)


def main():
    """Validate cookiecutter inputs."""
    name = "{{ cookiecutter.name }}"
    version = "{{ cookiecutter.version }}"

    print("Validating cookiecutter inputs...")
    validate_name(name)
    validate_version(version)
    print("OK - All inputs valid")


if __name__ == "__main__":
    main()
