#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
from ansible.module_utils.basic import *


class Beaker:

    CMDs = dict(
        reboot='bkr system-power --insecure --action reboot {bkr_name}',
    )

    def __init__(self, module):
        self.module = module
        self.bkr_name = module.params['bkr_name']

    def _exec_cmd(self, cmd, args, output=False):
        _cmd = self.CMDs[cmd].format(**args)
        if not output:
            ret = subprocess.call(_cmd, shell=True)
            return ret
        else:
            ret = subprocess.check_output(_cmd, shell=True)
            return ret

    def reboot(self):
        rcode = self._exec_cmd('reboot', dict(bkr_name=self.bkr_name))
        return dict(ret=rcode)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            bkr_name=dict(default='', type='str'),
            action=dict(default='reboot', type='str')
        )
    )

    beaker = Beaker(module)

    if module.params['action'] == 'reboot':
        ret = beaker.reboot()
        module.exit_json(**ret)


if __name__ == '__main__':
    main()
