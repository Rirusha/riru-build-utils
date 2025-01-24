project('riru-build-utils',
    version: '0.7.0',
    meson_version: '>= 1.0.0'
)

python = import('python')

# Module objects
py_installation = python.find_installation('python3')

# Make sure Python is installed and found
if not py_installation.found()
    error('No valid python3 binary found')
endif

required_python_version = '3.10'
if not py_installation.language_version().version_compare('>= ' + required_python_version)
  error('Python @0@ or newer is required.'.format(required_python_version))
endif

PYTHON_DIR = py_installation.get_path('purelib')
PKGDATA_DIR = get_option('prefix') / get_option('datadir') / meson.project_name ()

subdir('data')

install_subdir(
    'riru_build_utils',
    install_dir: py_installation.get_install_dir()
)

# Install the executable file
bin_config = configuration_data()
bin_config.set('pkgdatadir', PKGDATA_DIR)
bin_config.set('pythondir', PYTHON_DIR)

configure_file(
    input: 'rbu.in',
    output: 'rbu',
    configuration: bin_config,
    install_dir: get_option('prefix') / get_option('bindir'),
    install_mode: 'rwxr-xr-x'
)
