import os
import subprocess
import sys
import tempfile


def shell(cmd):
    return subprocess.check_call(cmd, shell=True)


def shell_capture(cmd):
    output = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
    return output

if 'doctotext' in shell_capture('which doctotext'):
    sys.exit(0) # already installed

if len(sys.argv) > 1:
    homedir = '~%s' % sys.argv[1]
else:
    homedir = '~'

tmp = tempfile.mkdtemp('doctotext')
try:
    os.chdir(tmp)
    tarball = 'http://karlhosting.github.io/doctotext-0.12.0-x86-linux.tar.bz2'
    shell('wget %s' % tarball)
    shell('tar xvfj *.tar.bz2')
    src = os.path.join(tmp, 'doctotext')

    home = os.path.expanduser(homedir)
    bin = os.path.join(home, 'bin')
    if not os.path.exists(bin):
        os.mkdir(bin)

    exe = os.path.join('bin', 'doctotext')
    if not os.path.exists(exe):
        shell('cp %s/doctotext %s' % (src, bin))

    lib = os.path.join(home, 'lib')
    if not os.path.exists(lib):
        os.mkdir(lib)

    for so in ('libwv2.so.1', 'libxlsreader.so.0'):
        so_path = os.path.join(lib, so)
        if not os.path.exists(so_path):
            shell('cp %s/%s %s' % (src, so, lib))

    if 'doctotext' in shell_capture('which doctotext'):
        sys.exit(0) # already installed

    shell('echo export PATH=%s:\\$PATH >> %s/.bash_profile' % (bin, homedir))
    shell('echo export LD_LIBRARY_PATH=%s >> %s/.bash_profile' % (lib, homedir))
finally:
    shell('rm -rf %s' % tmp)
