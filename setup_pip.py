import os
import subprocess
import shutil
import sys
import sysconfig
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy
from cmake_setuptools import CMakeExtension, CMakeBuildExt, distutils_dir_name, \
    convert_to_manylinux

from distutils.sysconfig import get_python_lib

# setup does not clean up the build directory, so do it manually
shutil.rmtree('build', ignore_errors=True)

cuda_version = ''.join(os.environ.get('CUDA', 'unknown').split('.')[:2])

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# temporary fix. cugraph 0.5 will have a cugraph.get_include()
cudf_include = os.path.normpath(sys.prefix) + '/include'

cython_files = ['python/pagerank/pagerank_wrapper.pyx']

extensions = [
    CMakeExtension('cugraph', sourcedir='cpp'),
    Extension("cugraph",
              sources=cython_files,
              include_dirs=[numpy_include,
                            cudf_include,
                            'src',
                            'include',
                            '../gunrock',
                            '../gunrock/externals/moderngpu/include',
                            '../gunrock/externals/cub'],
              library_dirs=[get_python_lib(), distutils_dir_name('lib')],
              libraries=['nvgraph'],
              language='c++',
              extra_compile_args=['-std=c++11'])
]

install_requires = [
    'numpy',
    'cython'
]

name = 'cugraph-cuda{}'.format(cuda_version)
version = os.environ.get('GIT_DESCRIBE_TAG', '0.0.0.dev0').lstrip('v')
setup(name='cugraph',
      version=version,
      description='cuGraph - RAPIDS Graph Analytic Algorithms',
      long_description=open('README.md', encoding='UTF-8').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/rapidsai/cugraph',
      author='NVIDIA Corporation',
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ],
      packages=find_packages(where='python'),
      ext_modules=cythonize(extensions),
      install_requires=install_requires,
      license="Apache",
      cmdclass={
          'build_ext': CMakeBuildExt
      },
      headers=['include'],
      zip_safe=False)

convert_to_manylinux(name, version)
