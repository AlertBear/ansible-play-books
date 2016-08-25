#!/usr/bin/python
# -*- coding: utf-8 -*-
import xmlrpclib
import subprocess
from ansible.module_utils.basic import *


class Cobbler:

    def __init__(self, module):
        self.module = module
        self.bkr_name = module.params['bkr_name']
        self.ks_url = module.params['ks_url']
        self.stage2_url = module.params['stage2_url']
        self.args = module.params['args']
        self.cb_profile_name = module.params['cb_profile_name']
        self.cb_api_url = module.params['cb_api_url']
        self.server = xmlrpclib.Server(self.cb_api_url)
        self.cb_user = module.params['cb_user']
        self.cb_pass = module.params['cb_pass']
        
        self.cb_credential = (self.cb_user, self.cb_pass)
        self.token = self.login()

    def _debug(self, msg=None):
        print("*" * 100)
        print(msg)

    def _modify_system(self, system_handle, args):
        for k, v in args.items():
            print("Modifying system: %s=%s" % (k, v))
            self.server.modify_system(system_handle, k, v, self.token)
        self.server.save_system(system_handle, self.token)

    def _assign_defaults(self, system, profile, extra_args=None):
        args = dict(
            profile=profile,
            comment="managed-by-zoidberg",
            status="testing",
            kernel_options="",
            kernel_options_post="")
        
        if extra_args is not None:
            args.update(extra_args)
        
        self._modify_system(system, args)

    def _set_netboot_enable(self, system, enabled):
        args = {
            "netboot-enabled": 1 if enabled else 0
        }

        self._modify_system(system, args)

    def _get_system_handle(self):
        return self.server.get_system_handle(self.bkr_name, self.token)

    def login(self):
        return self.server.login(*self.cb_credential)

    def enable_pxe_boot(self):
        args = dict(
            kernel_options="inst.ks={0} inst.stage2={1}".format(self.ks_url,
                                                                self.stage2_url),
        )

        self._debug(self.token)

        sh = self._get_system_handle()
        
        self._assign_defaults(sh, self.cb_profile_name, args)
        self._set_netboot_enable(sh, True)
        return dict(ret="True")
    
    def disable_pxe_boot(self):
        sh = self._get_system_handle()
        self._set_netboot_enable(sh, False)
        return dict(ret="True")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            bkr_name=dict(default='', type='str'),
            args=dict(default={}, type='dict'),
            cb_profile_name=dict(default='', type='str'),
            cb_api_url=dict(default='', type='str'),
            cb_user=dict(default='', type='str'),
            cb_pass=dict(default='', type='str'),
            ks_url=dict(default='', type='str'),
            stage2_url=dict(default='', type='str'),
            pxe=dict(default='no', type='str')
        )
    )

    cobbler = Cobbler(module)

    if module.params['pxe'] == 'yes':
        
        ret = cobbler.enable_pxe_boot()
        module.exit_json(**ret)
    elif module.params['pxe'] == 'no':
        ret = cobbler.disable_pxe_boot()
        module.exit_json(**ret)


if __name__ == '__main__':
    main()
