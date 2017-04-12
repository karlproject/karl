import os

default_cfg = """
[buildout]
eggs-directory = ~/.buildout/eggs
download-cache = ~/.buildout/download-cache
abi-tag-eggs = true
"""

dot_buildout = os.path.expanduser("~/.buildout")
if not os.path.exists(dot_buildout):
    os.mkdir(dot_buildout)
    with open(os.path.join(dot_buildout, 'default.cfg'), 'w') as f:
        f.write(default_cfg)
