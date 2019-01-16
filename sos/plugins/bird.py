# Copyright (C) 2018 Alexander Petrovskiy <alexpe@mellanox.com>
#
# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.plugins import Plugin, RedHatPlugin, UbuntuPlugin, DebianPlugin


class Bird(Plugin, RedHatPlugin, UbuntuPlugin, DebianPlugin):
    """Bird routing daemon
    """

    plugin_name = 'bird'
    profiles = ('network',)
    packages = ('bird',)

    def setup(self):
        self.add_copy_spec([
            "/etc/bird/*",
            "/etc/bird.conf"
        ])
        self.add_cmd_output("birdc show status")
        self.add_cmd_output("birdc show memory")
        self.add_cmd_output("birdc show protocols all")
        self.add_cmd_output("birdc show route all")
        self.add_cmd_output("birdc symbols")
        self.add_cmd_output("birdc show bfd sessions")
        self.add_cmd_output("birdc show ospf")
        self.add_cmd_output("birdc show rip")
        self.add_cmd_output("birdc show static")

