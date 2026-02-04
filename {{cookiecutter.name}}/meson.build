project(
  '{{cookiecutter.name}}',
  {{cookiecutter.languages}},
  version: '{{cookiecutter.version}}',
  {% if cookiecutter.license != 'None' %}license: '{{cookiecutter.license}}',
  {% endif %}meson_version: '>= 1.3.1',
  default_options : [
    'b_vscrt=static_from_buildtype',
    'buildtype=release',
])

fc = meson.get_compiler('fortran')
fc_id = fc.get_id()
message('Fortran Compiler ID:', fc_id)

{% if cookiecutter.has_c_code == 'yes' %}
cc = meson.get_compiler('c')
cc_id = cc.get_id()
message('C Compiler ID:', cc_id)
{% endif %}

compile_args = []
link_args = []
extra_deps = []

if fc_id == 'gcc'
  compile_args += ['-fall-intrinsics', '-fbacktrace', '-ffpe-summary=overflow']
  # Link quadmath library on macOS (required for gfortran runtime)
  if host_machine.system() == 'darwin'
    quadmath_dep = fc.find_library('quadmath', required: true, static: true)
    extra_deps += [quadmath_dep]
  endif
endif

if fc_id == 'intel' or fc_id == 'intel-cl'
  compile_args += ['-diag-disable=10441']
  link_args += ['-diag-disable=10441']
endif

if fc_id == 'intel-llvm' or fc_id == 'intel-llvm-cl'
  compile_args += ['-diag-disable=10441']
  link_args += ['-diag-disable=10441']
endif

add_project_arguments(fc.get_supported_arguments(compile_args), language: 'fortran')
add_project_link_arguments(fc.get_supported_arguments(link_args), language: 'fortran')

subdir('src')

test('version',
     exe,
     args : [],
     should_fail: true,
     workdir: meson.current_source_dir())
