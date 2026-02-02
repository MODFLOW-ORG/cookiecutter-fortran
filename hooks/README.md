# Cookiecutter Hooks

This directory contains hooks that run before and after project generation.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [pre_gen_project.py](#pre_gen_projectpy)
- [post_gen_project.py](#post_gen_projectpy)
  - [Optional: Git Initialization](#optional-git-initialization)
  - [Optional: Source File Management](#optional-source-file-management)
  - [Optional: Build Testing](#optional-build-testing)
  - [Always Runs](#always-runs)
- [Customizing](#customizing)
- [Use Cases](#use-cases)
  - [Use Case 1: Legacy USGS Program Migration](#use-case-1-legacy-usgs-program-migration)
  - [Use Case 2: New Program from Scratch](#use-case-2-new-program-from-scratch)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## pre_gen_project.py

Runs before project generation. Validates user inputs:
- Ensures `name` follows naming conventions (lowercase, starts with letter, only contains lowercase letters, numbers, hyphens, underscores)
- Ensures `version` follows semantic versioning format (X.Y.Z)
- Exits with error if validation fails

## post_gen_project.py

Runs after project generation. Performs setup tasks:

### Optional: Git Initialization
If user sets `git_init` to "yes":
- Initializes git repository
- Creates initial commit with template files
- Prints git-related next steps

### Optional: Source File Management
If user provides a `source_directory` path:
- Recursively searches for Fortran and C source files (`.f`, `.f90`, `.for`, `.F`, `.F90`, `.c`, `.h`, `.inc`)
- Copies all found source files to the `src/` directory
- Auto-generates `src/meson.build` with proper source file list
  - Separates compilable sources from include files (.inc, .h)
  - Orders Fortran files before C files (for module dependencies)
  - Excludes non-compilable files from the sources list

### Optional: Build Testing
If user sets `test_build` to "yes" and source files were copied:
- Checks if pixi is available
- Runs `pixi run setup` to configure the build
- Runs `pixi run build` to compile the program
- Reports success or failure

### Always Runs
- Prints next steps for the user

## Customizing

You can modify these hooks to:
- Add additional validation in `pre_gen_project.py`
- Perform additional setup in `post_gen_project.py` (e.g., installing dependencies, running formatters)
- Add more hooks (see https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html)

## Use Cases

### Use Case 1: Legacy USGS Program Migration
You have an existing USGS Fortran program distributed as a tarball and want to create a modern repository:

```bash
# Extract the program
tar -xzf modflow-program.tar.gz

# Run cookiecutter with source_directory pointing to extracted src/
cookiecutter path/to/template
# source_directory: /path/to/extracted/src
# git_init: yes
# test_build: yes

# Hook automatically:
# - Copies all source files
# - Generates meson.build
# - Tests the build
# - Creates git repo
```

### Use Case 2: New Program from Scratch
You're starting a new Fortran program:

```bash
# Run cookiecutter without source_directory
cookiecutter path/to/template
# source_directory: (leave empty)
# git_init: yes
# test_build: no

# Hook sets up structure, you manually:
# - Add source files to src/
# - Edit src/meson.build
# - Run pixi run setup && pixi run build
```
