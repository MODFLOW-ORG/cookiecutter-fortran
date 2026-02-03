#!/usr/bin/env python
"""Post-generation hook for cookiecutter-fortran."""

import glob
import os
import shutil
import subprocess
import sys


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False



def generate_license_file():
    """Generate LICENSE file based on selected license."""
    license_choice = "{{ cookiecutter.license }}"
    year = "{{ cookiecutter.year }}"
    org = "{{ cookiecutter.org }}"
    
    # CC0 is default in template, skip if chosen
    if license_choice == "CC0":
        print(f"OK - Using default CC0 license")
        return
    
    # Remove LICENSE file if user wants to provide their own
    if license_choice == "None":
        if os.path.exists("LICENSE"):
            os.remove("LICENSE")
        print("OK - LICENSE file removed, add your own license")
        return
    
    # License texts
    licenses = {
        "MIT": f"""MIT License

Copyright (c) {year} {org}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
        "BSD-3-Clause": f"""BSD 3-Clause License

Copyright (c) {year}, {org}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""",
        "Apache-2.0": """Apache License 2.0

For the full license text, see:
https://www.apache.org/licenses/LICENSE-2.0
""",
        "GPL-3.0": """GNU General Public License v3.0

For the full license text, see:
https://www.gnu.org/licenses/gpl-3.0.txt
"""
    }
    
    if license_choice in licenses:
        with open("LICENSE", "w") as f:
            f.write(licenses[license_choice])
        print(f"OK - Generated LICENSE file with {license_choice} license")
    else:
        print(f"WARNING: Unknown license {license_choice}, keeping CC0")


def copy_source_files(source_dir, dest_dir):
    """Copy Fortran and C source files from source_dir to dest_dir."""
    if not os.path.exists(source_dir):
        print(f"ERROR - Source directory does not exist: {source_dir}")
        return []
    
    print(f"\nCopying source files from: {source_dir}")
    
    # Supported extensions
    extensions = ['*.f', '*.f90', '*.for', '*.F', '*.F90', '*.c', '*.h', '*.inc']
    
    copied_files = []
    for ext in extensions:
        pattern = os.path.join(source_dir, '**', ext)
        for filepath in glob.glob(pattern, recursive=True):
            filename = os.path.basename(filepath)
            dest_path = os.path.join(dest_dir, filename)
            
            # Avoid overwriting if file already exists
            if os.path.exists(dest_path):
                print(f"  Skipping {filename} (already exists)")
                continue
            
            try:
                shutil.copy2(filepath, dest_path)
                copied_files.append(filename)
                print(f"  OK - Copied {filename}")
            except Exception as e:
                print(f"  ERROR - Failed to copy {filename}: {e}")
    
    print(f"\nCopied {len(copied_files)} source files")
    return copied_files


def generate_meson_build(source_files, has_c_code):
    """Generate src/meson.build with source file list."""
    if not source_files:
        print("No source files to add to meson.build")
        return
    
    # Separate source files from include files
    compilable_sources = [f for f in source_files if not f.endswith('.inc') and not f.endswith('.h')]
    
    # Sort files: Fortran files first (for module dependencies), then C files
    fortran_files = sorted([f for f in compilable_sources if f.endswith(('.f', '.f90', '.for', '.F', '.F90'))])
    c_files = sorted([f for f in compilable_sources if f.endswith('.c')])
    
    all_sources = fortran_files + c_files
    
    if not all_sources:
        print("No compilable source files found (only .inc or .h files)")
        return
    
    # Generate meson.build content
    meson_content = "# Source files\n"
    meson_content += "sources = files(\n"
    for f in all_sources:
        meson_content += f"  '{f}',\n"
    meson_content += ")\n\n"
    meson_content += "exe = executable(\n"
    meson_content += "                 '{{ cookiecutter.name }}',\n"
    meson_content += "                 sources,\n"
    meson_content += "                 install: true\n"
    meson_content += "                )\n"
    
    # Write to src/meson.build
    meson_build_path = os.path.join('src', 'meson.build')
    with open(meson_build_path, 'w') as f:
        f.write(meson_content)
    
    print(f"\nOK - Generated src/meson.build with {len(all_sources)} source files")


def test_build():
    """Test the build using pixi."""
    print("\n" + "=" * 70)
    print("Testing build...")
    print("=" * 70)
    
    # Check if pixi is available
    try:
        subprocess.run(['pixi', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR - pixi not found. Skipping build test.")
        print("  Install pixi to test the build automatically.")
        return False
    
    # Run setup
    if not run_command("pixi run setup", "Running pixi run setup"):
        print("ERROR - Build setup failed")
        return False
    
    # Run build
    if not run_command("pixi run build", "Running pixi run build"):
        print("ERROR - Build failed")
        return False
    
    print("\nOK - Build completed successfully!")
    return True


def main():
    """Run post-generation tasks."""
    project_dir = os.getcwd()
    source_directory = "{{ cookiecutter.source_directory }}".strip()
    git_init_flag = "{{ cookiecutter.git_init }}".lower() == "yes"
    test_build_flag = "{{ cookiecutter.test_build }}".lower() == "yes"

    print("=" * 70)
    print(f"Setting up project: {{ cookiecutter.name }}")
    print("=" * 70)

    # Generate LICENSE file
    generate_license_file()

    # Initialize git repository (optional)
    if git_init_flag:
        if run_command("git init", "Initializing git repository"):
            print("OK - Git repository initialized")
        else:
            print("ERROR - Failed to initialize git repository")
            print("  You can run 'git init' manually later")

    # Handle source file copying if source_directory is provided
    source_files_copied = False
    if source_directory:
        print("\n" + "=" * 70)
        print("Copying source files...")
        print("=" * 70)
        
        src_dir = os.path.join(project_dir, 'src')
        copied_files = copy_source_files(source_directory, src_dir)
        
        if copied_files:
            has_c_code = "{{ cookiecutter.has_c_code }}" == "yes"
            generate_meson_build(copied_files, has_c_code)
            source_files_copied = True
        else:
            print("ERROR - No source files were copied")

    # Test build if requested and source files were copied
    if test_build_flag and source_files_copied:
        test_build()
    elif test_build_flag and not source_files_copied:
        print("\nSkipping build test (no source files to build)")

    # Create initial git commit (only if git was initialized)
    if git_init_flag and os.path.exists(".git"):
        run_command("git add .", "Staging files")
        run_command(
            'git commit -m "Initial commit from cookiecutter template"',
            "Creating initial commit"
        )

    # Print next steps
    print("\n" + "=" * 70)
    print("Project setup complete!")
    print("=" * 70)
    
    if not source_files_copied:
        print("\nNext steps:")
        print("1. Copy your Fortran source files to the 'src/' directory")
        print("2. Edit 'src/meson.build' and list your source files")
        print("3. Test the build:")
        print("   pixi run setup")
        print("   pixi run build")
        print("4. Run tests:")
        print("   pixi run test")
        if git_init_flag:
            print("5. Push to GitHub when ready")
        else:
            print("5. Initialize git: git init")
            print("6. Push to GitHub when ready")
    else:
        print("\nNext steps:")
        print("1. Review the generated src/meson.build file")
        print("2. Adjust compiler flags in meson.build if needed")
        step = 3
        if not test_build_flag:
            print(f"{step}. Test the build:")
            print("   pixi run setup")
            print("   pixi run build")
            step += 1
        print(f"{step}. Run tests:")
        print("   pixi run test")
        step += 1
        if git_init_flag:
            print(f"{step}. Push to GitHub when ready")
        else:
            print(f"{step}. Initialize git: git init")
            print(f"{step + 1}. Push to GitHub when ready")
    
    print("\nFor more information, see README.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
