# Goal

Grab all **src.rpm** packages which match the pattern listed in the file **package.list** for wanted product.
This will store the source rpm package in the product name directory, ie: **SLE-15-SP6**. 
This script grab the latest version of the package in the **update** channel and also initial package in **GA**.

# Python module needed

**python3-tqdm**

```bash
zypper in python3-tqdm
```

# How to use grab_packages.py

```bash
chmod 755 grab_packages.py
./grab_packages.py
```
![image](https://github.com/aginies/grab_packages/blob/298eb4d7c6916ce2030fa00aa79d5e4afa10d180/grab.jpg)

# How to use package_comparison.py

```bash
chmod 755 package_comparison.py
package_comparison.py result packages.list
```


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
product_names = SLE-15-SP7, SLE-15-SP6, SLE-15-SP4, SLE-15-SP3, SLE-15-SP2, SLE-15-SP1, SLE-15, SLE-12-SP5, 16.0
```

## packages.list

```
hyper-v
libcap-ng
libcgroup1
libguestfs
libvirt
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
virt-what
virt-v2v
xen
yast2-vm
```
