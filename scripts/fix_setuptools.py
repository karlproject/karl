# https://github.com/pypa/setuptools/issues/997

import os.path

with open('env/lib/python2.7/site-packages/setuptools/dist.py') as f:
    src = f.read()

proper_imports = """
import packaging.specifiers
import packaging.version
"""

if '\nimport packaging\n' in src:
    src = src.replace('\nimport packaging\n', proper_imports)
    with open('env/lib/python2.7/site-packages/setuptools/dist.py', 'w') as f:
        f.write(src)

