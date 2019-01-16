# Copyright (C) 2018 Alexander Petrovskiy <alexpe@mellanox.com>
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.

import os
import re
from sos.plugins import Plugin, RedHatPlugin, UbuntuPlugin, DebianPlugin

class MlnxLinuxSwitch(Plugin, RedHatPlugin, UbuntuPlugin, DebianPlugin):

    """Get extra info from Mellanox Linux Switch"""
    plugin_name = "mlnx_linux_switch"
    profiles = ('network', 'hardware', 'system')

    option_list = [
        ("sysinfo-snapshot", "collect Mellanox sysinfo-snapshot", "slow", False)
    ]

    def setup(self):
        self.get_kernel_config()
        self.get_onie_version()
        self.get_fw_dump()
        if self.get_option("sysinfo-snapshot"):
            self.get_sysinfo_snapshot()

    def postproc(self):
        # cleanup
        self.call_ext_prog("umount /tmp/onie") 
        self.call_ext_prog("rmdir /tmp/onie")
        self.call_ext_prog("mst stop")
        self.call_ext_prog("rm -fr /tmp/mstdump")
        self.call_ext_prog("rm -fr /tmp/sysinfo-snapshot")


    def get_devlink_devs(self):
        """Returns a list for which items are devlink devices.
        """
        devlink_dev_result = self.call_ext_prog("devlink dev show")
        dev_list = []
        if devlink_dev_result['status'] == 0:
            for dev in devlink_dev_result['output'].splitlines():
                dev_list.append(dev)
        return dev_list

    def get_kernel_config(self):
        # copy kernel configuration
        self.add_copy_spec([
            "/boot/config",
            "/boot/config-*",
            "/proc/config.gz"
        ])

    
    def get_onie_version(self):
        # ONIE Version
        self.call_ext_prog("mkdir /tmp/onie")
        self.call_ext_prog("mount /dev/sda2 /tmp/onie")
        if os.path.exists("/tmp/onie/onie/tools/bin/onie-version"):
            self.add_cmd_output("/tmp/onie/onie/tools/bin/onie-version")


    def dump_fw(self, device, dest_dir):
        # do it three times to perform three consecutive register dumps
        for i in range(3):
            cmd = 'sh -c "mstdump %s > %s"' % (device, os.path.join(dest_dir, "mstdump"+str(i)))
            self.call_ext_prog(cmd, chroot=False)


    def get_fw_dump(self):
        # Getting Mellanox FW dump
        dumpdir = "/tmp/mstdump/"
        self.call_ext_prog("mkdir %s" % dumpdir)
        if not os.path.exists("/dev/mst"):
            self.call_ext_prog("mst start")
        mst_output = self.call_ext_prog("mst status")
        if re.findall(".*MST PCI configuration module loaded.*", mst_output['output']):
            self.dump_fw("/dev/mst/mt*conf0", dumpdir)
        else:
            for dev in self.get_devlink_devs():
                if dev.startswith("pci/"):
                    dev = dev.split("/")[1]
                self.dump_fw(dev, dumpdir)
        self.add_copy_spec([dumpdir])


    def get_sysinfo_snapshot(self):
        # collect sysinfo-snapshot dump
        sysinfo_result = self.call_ext_prog("sysinfo-snapshot.py --json --pcie --no_ib --mtusb -fw")
        if sysinfo_result['status'] == 0:
            res = re.findall("(/tmp/sysinfo-snapshot.*.tgz)", sysinfo_result['output'])
            if res:
                sysinfo_file = res[0]
                self.add_copy_spec([sysinfo_file])