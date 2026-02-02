# Template for Fortran programs

This is a cookiecutter template for creating Fortran program repositories with meson build system, pixi environment management, and GitHub Actions CI.

## Usage

### Basic Usage

1. Install cookiecutter:
   ```bash
   pip install cookiecutter
   # or
   pixi global install cookiecutter
   ```

2. Generate a new project:
   ```bash
   cookiecutter path/to/cookiecutter-fortran
   ```

3. Answer the prompts:
   - `name`: Program name (must start with lowercase letter, use only lowercase, numbers, hyphens, underscores)
   - `version`: Version number following format X.Y.Z (e.g., 1.0.0, 1.19.01)
   - `description`: Short description of the program
   - `year`: Copyright year
   - `org`: Organization name (default: USGS)
   - Citation fields for both report and software
   - `has_c_code`: Whether the program includes C code (yes/no)
   - `source_directory`: (Optional) Path to existing source files to copy
   - `git_init`: Whether to initialize git repository (yes/no)
   - `test_build`: Whether to test the build after setup (yes/no)

### Automated Source File Setup

If you provide a `source_directory` path, the post-generation hook will automatically:
1. Copy all Fortran (.f, .f90, .for) and C (.c) source files from that directory
2. Generate `src/meson.build` with the correct source file list
3. Optionally test the build (if `test_build` is "yes")

Example with automatic source setup:
```bash
cookiecutter path/to/cookiecutter-fortran
# When prompted for source_directory, provide:
# /path/to/extracted/program/src
```

### Manual Setup

If you don't provide a `source_directory`, you'll need to:
1. Copy your source files to the `src/` directory
2. Edit `src/meson.build` to list all your source files
3. Test the build: `pixi run setup && pixi run build`

## What the Hooks Do

The post-generation hook (`hooks/post_gen_project.py`) automatically:
- Optionally initializes git repository (if `git_init` is "yes")
- Copies source files if `source_directory` is provided
- Generates `src/meson.build` with source file list
- Tests the build if `test_build` is "yes"
- Creates initial git commit (if git was initialized)
- Displays next steps

The pre-generation hook (`hooks/pre_gen_project.py`) validates:
- Program name follows naming conventions
- Version follows semantic versioning format

## What's Included

- `meson.build`: Main build configuration with compiler flags
- `src/meson.build`: Source files listing (auto-generated if source_directory provided)
- `pixi.toml`: Pixi environment and task definitions
- `README.md`: Project README with citation placeholders
- `LICENSE`: CC0 license
- `.gitignore`: Standard ignores for Fortran/meson projects
- `.github/workflows/ci.yml`: CI workflow testing multiple compilers (GCC 11/12/13, Intel Classic, Intel ifx)

## Example Workflow

For a USGS program with existing source code:

```bash
# Download and extract the program source
curl -O https://water.usgs.gov/path/to/program.tar.gz
tar -xzf program.tar.gz

# Generate repository from template
cookiecutter path/to/cookiecutter-fortran

# Fill in prompts:
# name: mf2000
# version: 1.19.01
# source_directory: /path/to/extracted/mf2k.1_19/src
# git_init: yes
# test_build: yes

# The hook will:
# - Copy all source files
# - Generate src/meson.build
# - Run the build test
# - Initialize git and create initial commit

# You're done! Push to GitHub when ready.
```
