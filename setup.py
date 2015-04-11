from setuptools import setup
from imageset import imageset

setup(name='imageset',
      version=imageset.version,
      description='Process Xcode imagesets into compiler-checkable files',
      url='http://github.com/natestedman/imageset',
      author='Nate Stedman',
      author_email='nate@natestedman.com',
      license='ISC',
      packages=['imageset'],
      install_requires = ['pystache'],
      entry_points = {
          'console_scripts': [
              'imageset = imageset.imageset:main'
          ]
      },
      zip_safe=False)