import os
import subprocess
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools import find_packages

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    user_options = build_ext.user_options + [
        ('build-type=', None, 'Specify the CMAKE_BUILD_TYPE (Release or Debug)'),
        ('shared-libs', None, 'Build shared libraries'),
        ('python-wrapper', None, 'Enable Python wrapper'),
        ('python-executable=', None, 'Specify the Python executable'),
        ('python-include-dir=', None, 'Specify Python include directory'),
        ('python-lib=', None, 'Specify Python library path'),
        ('numpy-include-dir=', None, 'Specify NumPy include directory'),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.build_type = 'Release'
        self.shared_libs = True
        self.python_wrapper = True
        self.python_executable = sys.executable
        self.python_include_dir = None
        self.python_lib = None
        self.numpy_include_dir = None

    def finalize_options(self):
        super().finalize_options()

    def run(self):
        try:
            subprocess.check_call(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DCMAKE_BUILD_TYPE={self.build_type}',
            f'-DPYTHON_EXECUTABLE={self.python_executable}',
        ]

        # Add flags based on the user options
        if self.shared_libs:
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
        if self.python_wrapper:
            cmake_args.append('-DBUILD_PYTHON_WRAPPER=ON')
        if self.python_include_dir:
            cmake_args.append(f'-DPython3_INCLUDE_DIR={self.python_include_dir}')
        if self.python_lib:
            cmake_args.append(f'-DPython3_LIBRARY={self.python_lib}')
        if self.numpy_include_dir:
            cmake_args.append(f'-DPython3_NUMPY_INCLUDE_DIR={self.numpy_include_dir}')

        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.check_call(['cmake', '--build', '.'], cwd=build_temp)

setup(
    name="apriltag",
    version="3.4.2",
    description="AprilTag Python bindings",
    packages=find_packages(),
    ext_modules=[CMakeExtension('apriltag')],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
)
