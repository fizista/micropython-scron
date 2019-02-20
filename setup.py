import sys
from pathlib import Path

__dir__ = Path(__file__).absolute().parent
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup

sys.path.append("..")
import sdist_upip

exec(open('scron/version.py').read())

def read(file_relative):
    file = __dir__ / file_relative
    with open(str(file)) as f:
        return f.read()


setup(
    name='micropython-scron',
    version=__version__,
    description='Simple CRON for MicroPython.',
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    url='https://github.com/fizista/micropython-scron',
    author='Wojciech Banaś',
    author_email='fizista@gmail.com',
    maintainer='Wojciech Banaś',
    maintainer_email='fizista+scron@gmail.com',
    license='GPL3',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    keywords='cron scheduler micropython',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['scron'],
)
