#!/usr/bin/python
# -*- coding: utf-8 -*
"""
Create RHEVH40 PXE Profiles

Usage:
  createrhevh40pxe.py pre <iso_name>
  createrhevh40pxe.py pxe <iso_name> <distro_name>
  createrhevh40pxe.py subpxe <distro_name>


Options:
  -h --help     Show this screen.
  -v --version     Show version.
"""
import os
import sys
import tempfile
from docopt import docopt


ISO_DIR = "/var/www/builds/rhvh_ngn/iso"
PXE_DIR = "/var/www/builds/rhvh_ngn/pxedir"

PXE_REPO_ROOT = "/home/dracher/Projects/pxerepo"
PXE_DIRTRO_DIR = os.path.join(PXE_REPO_ROOT, "distros")
PXE_PROFILE_DIR = os.path.join(PXE_REPO_ROOT, "profiles")

DISTRO_TPL = """
[General]
arch : x86_64
breed : redhat
comment :
kernel : http://10.66.10.22:8090/rhvh_ngn/pxedir/{iso_name}/pxeboot/vmlinuz
initrd : http://10.66.10.22:8090/rhvh_ngn/pxedir/{iso_name}/pxeboot/initrd.img
kernel_options : inst.stage2=http://10.66.10.22:8090/rhvh_ngn/pxedir/{iso_name}/stage2 inst.ks=http://10.66.10.22:8090/rhevh/ngn/latest/ngn.ks
kernel_options_post :
ks_meta :
mgmt_classes :
os_version : other
redhat_management_key :
redhat_management_server :
template_files :
"""

PROFILE_TPL = """
[General]
distro = {distro_name}
"""

SUB_PROFILE_TPL = """
[General]
distro = {distro_name}
kernel_options = "inst.ks=http://10.66.10.22:8090/rhevh/ngn/latest/ks/{user_name}.ks"
"""

SUB_KS_USERS = (
    "cshao",
    "dguo",
    "huzhao",
    "jiawu",
    "weiwang",
    "yaniwang",
    "ycui",
    "yizhao")


def mount_iso(name):
    mount_dir = tempfile.mkdtemp()
    pxe_dir = os.path.join(PXE_DIR, name)
    if not os.path.exists(pxe_dir):
        os.mkdir(pxe_dir)

    stage2_dir = os.path.join(pxe_dir, "stage2")
    if not os.path.exists(stage2_dir):
        os.mkdir(stage2_dir)

    os.system("mount -o loop %s %s" % (os.path.join(ISO_DIR, name), mount_dir))
    os.system("cp -r %s %s" % (os.path.join(mount_dir, "images", "pxeboot"),
                               pxe_dir))
    os.system("cp -r %s %s" % (os.path.join(mount_dir, "LiveOS"),
                               stage2_dir))

    os.system("umount %s" % mount_dir)
    os.system("rm -rf %s" % mount_dir)


def create_pxe(i, p):
    os.chdir(PXE_REPO_ROOT)
    os.system("git pull")

    with open(os.path.join(PXE_DIRTRO_DIR, "%s.distro" % p), "w") as distro:
        distro.write(DISTRO_TPL.format(iso_name=i))

    with open(os.path.join(PXE_PROFILE_DIR, "%s.profile" % p), "w") as profile:
        profile.write(PROFILE_TPL.format(distro_name=p))

    os.system("git add -A && git commit -m 'add distro %s' && git push" % p)


def create_sub_pxe(distro_name):
    os.chdir(PXE_REPO_ROOT)
    os.system("git pull")

    for user in SUB_KS_USERS:
        with open(os.path.join(PXE_PROFILE_DIR,
                               "%s-%s.profile" % (distro_name, user)), "w") as profile:
            profile.write(SUB_PROFILE_TPL.format(distro_name=distro_name, user_name=user))

    os.system("git add -A && git commit -m 'add sub-profiles of %s' && git push" % distro_name)


if __name__ == "__main__":
    args = docopt(__doc__, version='0.1.0')

    if args['pre']:
        if os.geteuid() != 0:
            print "must run as root"
            sys.exit(1)
        iso = args['<iso_name>']
        mount_iso(iso)

    elif args['pxe']:
        iso_name = args['<iso_name>']
        distro_name = args['<distro_name>']
        create_pxe(iso_name, distro_name)

    elif args['subpxe']:
        distro_name = args['<distro_name>']
        create_sub_pxe(distro_name)
