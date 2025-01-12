# Goal

Grab all **src.rpm** packages which match the pattern listed in the file **package.list** for each wanted product.
This will store the package in the product name directory, ie: **SLE-15-SP6**.

# Python module needed

**python3-tqdm**, **python3-packaging**

```bash
zypper in python3-tqdm python3-packaging
```

# How to use it

```bash
chmod 755 grab_packages.py
./grab_packages.py
```
![image](https://github.com/aginies/grab_packages/blob/298eb4d7c6916ce2030fa00aa79d5e4afa10d180/grab.jpg)

# Configuration

## config.ini

```
[server]
# paths to the repo which contains all the SLE repo
url = https://download.suse.de/ibs
paths = SUSE:/{product_name}:/Update/standard/src, SUSE:/{product_name}:/GA/standard/src 

[files]
# file which contains the pattern to match
packages = packages.list

[store]
# base directory to store the src.rpm files, the product_names will also be used
path = /run/media/aginies/d9d43b59-ccd6-42b2-909d-efd1341db80c/suse/

[products]
product_names = SLE-15-SP7, SLE-15-SP6, SLE-15-SP4, SLE-15-SP3, SLE-15-SP2, SLE-15-SP1, SLE-15, SLE-12-SP5
```

## package.list

```hyper-v
kvm
libcap-ng
libcgroup1
libguestfs
libvirt
libvirt-cim
libvirt-glib
lxc
netcontrol
numactl
open-ovf
open-vm-tools
perl-Sys-Virt
python-virtinst
qemu
snpguest
sanlock
spice
spice-gtk
spice-protocol
spice-vdagent
libguestfs
vhostmd
virt-manager
virt-utils
virt-viewer
virt-top
vm-install
virt-viewer
virt-what
virt-v2v
xen
yast2-vm
```
