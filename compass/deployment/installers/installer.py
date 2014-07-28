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

"""Module to provider installer interface.
"""
from Cheetah.Template import Template
from copy import deepcopy
import imp
import logging
import os
import simplejson as json


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class BaseInstaller(object):
    """Interface for installer."""
    NAME = 'installer'

    def __repr__(self):
        return '%r[%r]' % (self.__class__.__name__, self.NAME)

    def deploy(self, **kwargs):
        """virtual method to start installing process."""
        raise NotImplementedError

    def clean_progress(self, **kwargs):
        raise NotImplementedError

    def delete_hosts(self, **kwargs):
        """Delete hosts from installer server."""
        raise NotImplementedError

    def redeploy(self, **kwargs):
        raise NotImplementedError

    def get_tmpl_vars_from_metadata(self, metadata, config):
        template_vars = {}
        self._get_tmpl_vars_helper(metadata, config, template_vars)

        return template_vars

    # TODO(grace): I have slightly modified this impl.
    # Please decide which one to use.
    def _get_tmpl_vars_helper2(self, metadata, config, output):
        for key, config_value in config.iteritems():
            if key in metadata:
                sub_meta = metadata[key]
                try:
                    mapping_to_value = sub_meta['_self']['mapping_to']
                except KeyError:
                    mapping_to_value = None

                if mapping_to_value:
                    mapping_to = sub_meta['_self']['mapping_to']
                    if isinstance(config_value, dict):
                        output[mapping_to] = {}
                        self._get_tmpl_vars_helper(sub_meta, config_value,
                                                   output[mapping_to])
                    else:
                        output[mapping_to] = config_value
                elif isinstance(config_value, dict):
                    self._get_tmpl_vars_helper(sub_meta, config_value,
                                               output)
            else:
                temp = deepcopy(metadata)
                del temp['_self']
                meta_key = temp.keys()[0]
                if meta_key.startswith("$"):
                    sub_meta = metadata[meta_key]
                    if isinstance(config_value, dict):
                        output[key] = {}
                        self._get_tmpl_vars_helper(sub_meta, config_value,
                                                   output[key])
                    else:
                        output[key] = config_value
                else:
                    raise KeyError("'%s' is an invalid metadata!" % key)
        
    def _get_key_mapping(self, is_regular_key, metadata, key):
        mapping_to = key
        if is_regular_key:
            try:
                mapping_to = metadata['_self']['mapping_to']
            except:
                mapping_to = None
        return mapping_to

    def _get_submeta_by_key(self, metadata, key):
        if key in metadata:
            return (True, metadata[key])
    
        temp = deepcopy(metadata)
        del temp['_self']
        meta_key = temp.keys()[0]
        if meta_key.startswith("$"):
            return (False, metadata[meta_key])

        raise KeyError("'%s' is an invalid metadata!" % key)

    def _get_tmpl_vars_helper(self, metadata, config, output):
        for key, config_value in config.iteritems():
            regular_key, sub_meta = self._get_submeta_by_key(metadata, key)
            mapping_to = self._get_key_mapping(regular_key, sub_meta, key)

            if isinstance(config_value, dict):
                if mapping_to:
                    new_output = output[mapping_to] = {}
                else:
                    new_output = output

                self._get_tmpl_vars_helper(sub_meta, config_value,
                                           new_output)
            elif mapping_to:
                output[mapping_to] = config_value

    def get_config_from_template(self, tmpl_dir, vars_dict):
        if not os.path.exists(tmpl_dir) or not vars_dict:
            logging.info("Template or variables dict is not specified!")
            return {}

        tmpl = Template(file=tmpl_dir, searchList=[vars_dict])
        config = json.loads(tmpl.respond(), encoding='utf-8')
        config = json.loads(json.dumps(config), encoding='utf-8')
        return config

    @classmethod
    def get_installer(cls, name, path, **kwargs):
        try:
            mod_file, path, descr = imp.find_module(name, [path])
            if mod_file:
                mod = imp.load_module(name, mod_file, path, descr)
                adapter_info = kwargs['adapter_info']
                cluster_info = kwargs['cluster_info']
                hosts_info = kwargs['hosts_info']
                return getattr(mod, mod.NAME)(adapter_info, cluster_info,
                                              hosts_info)

        except ImportError as exc:
            logging.error('No such module found: %s', name)
            logging.exception(exc)

        return installer


class OSInstaller(BaseInstaller):
    """Interface for os installer."""
    NAME = 'OSInstaller'
    INSTALLER_BASE_DIR = os.path.join(CURRENT_DIR, 'os_installers')

    def get_oses(self):
        """virtual method to get supported oses.

        :returns: list of str, each is the supported os version.
        """
        return []

    @classmethod
    def get_installer(cls, name, adapter_info, cluster_info, hosts_info):
        path = os.path.join(cls.INSTALLER_BASE_DIR, name)
        installer = super(OSInstaller, cls).get_installer(name, path,
            adapter_info=adapter_info, cluster_info=cluster_info,
            hosts_info=hosts_info)

        if not isinstance(installer, OSInstaller):
            logging.info("Installer '%s' is not an OS installer!" % name)
            return None

    def poweron(self, host_id):
        pass

    def poweroff(self, host_id):
        pass

    def reset(self, host_id):
        pass


class PKInstaller(BaseInstaller):
    """Interface for package installer."""
    NAME = 'PKInstaller'
    INSTALLER_BASE_DIR = os.path.join(CURRENT_DIR, 'pk_installers')

    def get_target_systems(self):
        """virtual method to get available target_systems for each os.

        :param oses: supported os versions.
        :type oses: list of st

        :returns: dict of os_version to target systems as list of str.
        """
        return {}

    def get_roles(self, target_system):
        """virtual method to get all roles of given target system.

        :param target_system: target distributed system such as openstack.
        :type target_system: str

        :returns: dict of role to role description as str.
        """
        return {}

    @classmethod
    def get_installer(cls, name, adapter_info, cluster_info, hosts_info):
        path = os.path.join(cls.INSTALLER_BASE_DIR, name)
        installer = super(PKInstaller, cls).get_installer(name, path,
            adapter_info=adapter_info, cluster_info=cluster_info,
            hosts_info=hosts_info)

        if not isinstance(installer, PKInstaller):
            logging.info("Installer '%s' is not a package installer!" % name)
            return None

        return installer
