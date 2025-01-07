# Goal

Grab all **src.rpm** packages which match the pattern listed in the file **package.list** for each wanted product.
This will store the package in the product name directory, ie: **SLE-15-SP6**.

# Python module needed

**python3-tqdm**

```bash
zypper in python3-tqdm
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
url = https://download.suse.de/ibs
paths = SUSE:/{product_name}:/Update/standard/src, SUSE:/{product_name}:/GA/standard/src 

[store]
path = /run/media/aginies/d9d43b59-ccd6-42b2-909d-efd1341db80c/suse/

[files]
packages = packages.list

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
