"""Test suite for cookiecutter-fortran template."""

import subprocess
from pathlib import Path

import pytest


def run_cookiecutter(template_dir, output_dir, **kwargs):
    """Run cookiecutter with given parameters."""
    args = ['cookiecutter', '--no-input', str(template_dir)]
    args.append(f'--output-dir={output_dir}')
    
    for key, value in kwargs.items():
        args.append(f'{key}={value}')
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Command failed: {' '.join(args)}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    return result.returncode == 0


def test_basic_generation(tmp_path):
    """Test basic template generation with defaults."""
    template_dir = Path(__file__).parent
    
    success = run_cookiecutter(template_dir, tmp_path, name='testbasic')
    assert success, "Cookiecutter generation failed"
    
    project_dir = tmp_path / "testbasic"
    
    # Check essential files exist
    required_files = [
        "meson.build", "pixi.toml", "README.md", "LICENSE",
        ".gitignore", "src/meson.build", ".github/workflows/ci.yml"
    ]
    for file in required_files:
        assert (project_dir / file).exists(), f"Missing required file: {file}"


@pytest.mark.parametrize("license_choice", [
    "CC0", "MIT", "BSD-3-Clause", "Apache-2.0", "GPL-3.0", "None"
])
def test_license_generation(tmp_path, license_choice):
    """Test all license options."""
    template_dir = Path(__file__).parent
    
    success = run_cookiecutter(
        template_dir, tmp_path,
        name='testlic',
        license=license_choice,
        git_init='no',
        test_build='no'
    )
    assert success, f"Failed to generate with license={license_choice}"
    
    project_dir = tmp_path / "testlic"
    license_file = project_dir / "LICENSE"
    meson_build = project_dir / "meson.build"
    
    # Check LICENSE file
    if license_choice == "None":
        assert not license_file.exists(), "LICENSE file should not exist for license=None"
        # Check meson.build doesn't have license field
        content = meson_build.read_text()
        assert "license:" not in content, "meson.build should not have license field for None"
    else:
        assert license_file.exists(), f"Missing LICENSE file for license={license_choice}"
        # Check meson.build has correct license
        content = meson_build.read_text()
        assert f"license: '{license_choice}'" in content, \
            f"meson.build missing correct license for {license_choice}"


def test_source_copying(tmp_path):
    """Test automatic source file copying."""
    template_dir = Path(__file__).parent
    
    # Create test source files
    src_dir = tmp_path / "src_input"
    src_dir.mkdir()
    
    (src_dir / "main.f90").write_text("program test\n  print *, 'Hello'\nend program test\n")
    (src_dir / "module.f90").write_text("module testmod\nend module testmod\n")
    (src_dir / "utils.c").write_text("void test() {}\n")
    (src_dir / "header.h").write_text("// Header\n")
    (src_dir / "include.inc").write_text("! Include\n")
    
    # Generate project with source copying
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    success = run_cookiecutter(
        template_dir, output_dir,
        name='testsrc',
        has_c_code='yes',
        source_directory=str(src_dir),
        git_init='no',
        test_build='no'
    )
    assert success, "Source copying generation failed"
    
    project_dir = output_dir / "testsrc"
    
    # Check files were copied
    for file in ["main.f90", "module.f90", "utils.c", "header.h", "include.inc"]:
        assert (project_dir / "src" / file).exists(), f"Source file not copied: {file}"
    
    # Check meson.build was generated correctly
    meson_build = project_dir / "src" / "meson.build"
    content = meson_build.read_text()
    
    assert "'main.f90'" in content, "main.f90 not in meson.build"
    assert "'module.f90'" in content, "module.f90 not in meson.build"
    assert "'utils.c'" in content, "utils.c not in meson.build"
    assert "'header.h'" not in content, "header.h should not be in meson.build sources"
    assert "'include.inc'" not in content, "include.inc should not be in meson.build sources"


def test_full_automation(tmp_path):
    """Test fully automated workflow."""
    template_dir = Path(__file__).parent
    
    # Create test source
    src_dir = tmp_path / "src_input"
    src_dir.mkdir()
    (src_dir / "main.f90").write_text(
        "program hello\n  implicit none\n  print *, 'Hello'\nend program hello\n"
    )
    
    # Generate project with all automation
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    success = run_cookiecutter(
        template_dir, output_dir,
        name='testfull',
        version='1.0.0',
        license='MIT',
        source_directory=str(src_dir),
        git_init='yes',
        test_build='no'
    )
    assert success, "Full automation generation failed"
    
    project_dir = output_dir / "testfull"
    
    # Check everything is set up
    assert (project_dir / "LICENSE").exists()
    assert "MIT License" in (project_dir / "LICENSE").read_text()
    
    assert (project_dir / "src" / "main.f90").exists()
    assert "Hello" in (project_dir / "src" / "main.f90").read_text()
    
    assert (project_dir / "src" / "meson.build").exists()
    assert "'main.f90'" in (project_dir / "src" / "meson.build").read_text()
    
    assert (project_dir / ".git").exists()


def test_git_initialization_optional(tmp_path):
    """Test that git initialization is optional."""
    template_dir = Path(__file__).parent
    
    # Test with git_init=no
    success = run_cookiecutter(
        template_dir, tmp_path,
        name='testnogit',
        git_init='no',
        test_build='no'
    )
    assert success, "Generation with git_init=no failed"
    
    project_dir = tmp_path / "testnogit"
    assert not (project_dir / ".git").exists(), "Git repo should not be initialized"
