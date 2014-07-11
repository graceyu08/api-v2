# Copyright 2014 Huawei Technologies Co. Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""os installer cobbler plugin.
"""
import logging
import os
import shutil
import simplejson as json
import xmlrpclib

from Cheetah.Template import Template
from compass.deployment.installers.config_manager import BaseConfigManager
from compass.deployment.installers.installer import OSInstaller
from compass.utils import setting_wrapper as setting
from compass.utils import util


class CobblerInstaller(OSInstaller):
    """cobbler installer"""
    NAME = 'cobbler'
    CREDENTIALS = "credentials"
    USERNAME = 'username'
    PASSWORD = 'password'
    INSTALLER_URL = "cobbler_url"
    TMPL_DIR = 'tmpl_dir'
    SYS_TMPL_NAME = 'system.tmpl'
    PROFILE = 'profile'

    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(CobblerInstaller, self).__init__()
        self.config_manager = CobblerConfigManager(adapter_info,
                                                   cluster_info, hosts_info)
        installer_settings = self.config_manager.get_os_installer_settings()
        try:
            username = installer_settings[self.CREDENTIALS][self.USERNAME]
            password = installer_settings[self.CREDENTIALS][self.PASSWORD]
            cobbler_url = installer_settings[self.INSTALLER_URL]
            self.tmpl_dir = installer_settings[self.TMPL_DIR]
        except KeyError as ex:
            raise KeyError(ex.message)

        # the connection is created when cobbler installer is initialized.
        self.remote_ = xmlrpclib.Server(cobbler_url, allow_none=True)
        self.token_ = self.remote_.login(username, password)

        logging.debug('%s instance created', self)

    def __repr__(self):
        return '%s[name=%s,remote=%s,token=%s' % (
            self.__class__.__name__, self.NAME,
            self.remote_, self.token_)

    def get_supported_oses(self):
        """get supported os versions.

        :returns: list of os version.

        .. note::
           In cobbler, we treat profile name as the indicator
           of os version. It is just a simple indicator
           and not accurate.
        """
        profiles = self.remote_.get_profiles()
        oses = []
        for profile in profiles:
            oses.append(profile['name'])
        return oses

    def deploy(self):
        """Sync cobbler to catch up the latest update config and start to
           install OS.
        """
        os_version = self.config_manager.get_os_version()
        profile = self._get_profile_from_server(os_version)
        host_ids = self.config_manager.get_host_id_list()
        for host_id in host_ids:
            fullname = self.config_manager.get_host_fullname(host_id)
            vars_dict = self._get_tmpl_vars_dict(host_id, fullname=fullname,
                                                 profile=profile)

            self.update_host_os_config_to_server(host_id, fullname, vars_dict)
        # sync to cobbler and trigger installtion.
        self._sync()

    def set_package_installer_config(self, package_configs):
        self.pk_installer_config = package_configs

    def _sync(self):
        """Sync the updated config to cobbler and trigger installation."""
        self.remote_.sync(self.token_)
        logging.debug('sync %s', self)
        os.system('service rsyslog restart')

    def _get_system_config(self, vars_dict):
        """get updated system config."""
        os_version = self.config_manager.get_os_version()
        system_tmpl_file = os.path.join(os.path.join(self.tmpl_dir, os_version),
                                   self.SYS_TMPL_NAME)
        system_tmpl = Template(file=system_tmpl_file, searchList=[vars_dict])
        system_config = json.loads(system_tmpl.respond())

        # update package config info to ksmeta
        if self.pk_installer_config:
            ksmeta = system_config.setdefault("ksmeta", {})
            util.merge_dict(ksmeta, self.pk_installer_config)
            system_config["ksmeta"] = ksmeta

        return system_config

    def _get_profile_from_server(self, os_version):
        """get profile name."""
        profile = self.remote_.find_profile({'name': os_version})[0]
        return profile

    def _get_system_id(self, fullname, create_if_not_exists=True):
        """get system reference id for the host."""
        sys_name = fullname
        try:
            sys_id = self.remote_.get_system_handle(sys_name, self.token_)

            logging.debug('using existing system %s for %s', sys_id, sys_name)
        except Exception:
            if create_if_not_exists:
                sys_id = self.remote_.new_system(self.token_)
                logging.debug('create new system %s for %s', sys_id, sys_name)
            else:
                sys_id = None

        return sys_id

    def _clean_system(self, fullname):
        """clean system."""
        sys_name = fullname
        try:
            self.remote_.remove_system(sys_name, self.token_)
            logging.debug('system %s is removed', sys_name)
        except Exception:
            logging.debug('no system %s found to remove', sys_name)

    def _save_system(self, sys_id):
        """save system config update."""
        self.remote_.save_system(sys_id, self.token_)

    def _update_system_config(self, sys_id, system_config):
        """update modify system."""
        for key, value in system_config.items():
            self.remote_.modify_system(sys_id, key, value, self.token_)

    def _netboot_enabled(self, sys_id):
        """enable netboot."""
        self.remote_.modify_system(sys_id, 'netboot_enabled',
                                   True, self.token_)

    def clean_progress(self):
        """clean log files and config for hosts which to deploy."""
        host_list = self.config_manager.get_host_id_list()
        log_dir_prefix = setting.INSTALLATION_LOGDIR[self.NAME]
        for host_id in host_list:
            fullname = self.config_manager.get_host_fullname(host_id)
            self._clean_log(log_dir_prefix, fullname)

    def _clean_log(self, log_dir_prefix, system_name):
        """clean log."""
        log_dir = os.path.join(log_dir_prefix, system_name)
        shutil.rmtree(log_dir, True)

    def redeploy(self):
        """redeploy hosts."""
        host_ids = self.config_manager.get_host_id_list()
        for host_id in host_ids:
            fullname = self.config_manager.get_host_fullname(host_id)
            sys_id = self._get_system_id(fullname, False)
            if sys_id:
                self._netboot_enabled(sys_id)
                self._save_system(sys_id)

        self._sync()

    def update_host_os_config_to_server(self, host_id, fullname, vars_dict):
        """update host config and upload to cobbler server."""
        sys_id = self._get_system_id(fullname)

        system_config = self._get_system_config(vars_dict)
        logging.debug('%s system config to update: %s', host_id, system_config)

        self._update_system_config(sys_id, system_config)
        self._netboot_enabled(sys_id)
        self._save_system(sys_id)

    def delete_host(self, fullname):
        """Delete the host from cobbler server and clean up the installation
           progress.
        """
        try:
            log_dir_prefix = setting.INSTALLATION_LOGDIR[self.NAME]
            self._clean_system(fullname)
            self._clean_log(log_dir_prefix, fullname)
        except Exception as ex:
            logging.info("Deleting host got exception: %s", ex.message)

    def _get_tmpl_vars_dict(self, host_id, **kwargs):
        vars_dict = {}
        fullname = None
        if self.FULLNAME in kwargs:
            fullname = kwargs[self.FULLNAME]
        else:
            fullname = self.config_manager.get_host_fullname(host_id)

        if self.PROFILE in kwargs:
            profile = kwargs[self.PROFILE]
        else:
            os_version = self.config_manager.get_os_version()
            profile = self._get_profile_from_server(os_version)
        
        # Set fullname, MAC address and hostname
        vars_dict[self.FULLNAME] = fullname
        vars_dict[self.MAC_ADDR] = self.config_manager.get_host_mac_address(
                                   host_id)
        vars_dict[self.HOSTNAME] = self.config_manager.get_hostname(host_id)
        vars_dict[self.PROFILE] = profile

        os_config_metadata = self.config_manager.get_os_config_metadata()
        host_os_config = self.config_manager.get_host_os_config(host_id)

        # Get template variables values from metadata
        temp_vars_dict = self.get_tmpl_vars_from_metadata(os_config_metadata,
                                                          host_os_config)
        util.merge_dict(vars_dict, temp_vars_dict)

        return {'host': vars_dict}

OSInstaller.register(CobblerInstaller)


class CobblerConfigManager(BaseConfigManager):

    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(CobblerConfigManager, self).__init__(adapter_info,
                                                cluster_info,
                                                hosts_info)
