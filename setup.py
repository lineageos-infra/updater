import re
import ast
from setuptools import setup
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('updater/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='updater',
    version=version,
    url='https;//github.com/LineageOS/updater',
    license='apache-2.0',
    author='LineageOS Infrastructure Team',
    author_email='infra@bymason.com',
    long_description=__doc__,
    packages=['updater'],
    include_package_data=True,
    zip_safe=False,
    platform='any',
)
