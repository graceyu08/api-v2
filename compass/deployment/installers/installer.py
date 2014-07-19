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
import logging
import os
import simplejson as json


class Installer(object):
    """Interface for installer."""
    NAME = 'installer'

    def __repr__(self):
        return '%s[%s]' % (self.__class__.__name__, self.NAME)

    def deploy(self, **kwargs):
        """virtual method to start installing process."""
        pass

    def clean_progress(self, **kwargs):
        pass

    def delete_hosts(self, **kwargs):
        """Delete hosts from installer server."""
        pass

    def redeploy(self, **kwargs):
        pass

    def get_tmpl_vars_from_metadata(self, metadata, config):
        template_vars = {}
        self._get_tmpl_vars_helper(metadata, config, template_vars)

        return template_vars

    def _get_tmpl_vars_helper(self, metadata, config, output):
        for key in config:
            config_value = config[key]
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
                        output[mapping_to] = config[key]
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


    @classmethod
    def register(cls, installers_dict, installer):
        if not isinstance(installers_dict, dict):
            raise Exception("Installers holder must be a dictionary!")

        if not issubclass(installer, Installer):
            raise Exception("Not an Installer type! Cannot register!")

        if installer.NAME in installers_dict:
            raise KeyError("installer '%s' already exists!", installer.NAME)

        installers_dict[installer.NAME] = installer

    def get_config_from_template(self, tmpl_dir, vars_dict):
        if not os.path.exists(tmpl_dir) or not vars_dict:
            raise Exception("Template or variables dict is not specified!")
        tmpl = Template(file=tmpl_dir, searchList=[vars_dict])
        config = json.loads(tmpl.respond())

        return config


class OSInstaller(Installer):
    """Interface for os installer."""
    NAME = 'OSInstaller'
    OS_INSTALLERS = {}

    def get_oses(self):
        """virtual method to get supported oses.

        :returns: list of str, each is the supported os version.
        """
        return []

    @classmethod
    def register(cls, installer):
        if not issubclass(installer, OSInstaller):
            name = installer.NAME
            raise Exception("'%s' is not OS Installer type!", name)
        super(OSInstaller, cls).register(cls.OS_INSTALLERS, installer)

    @classmethod
    def get_os_installer(cls, name):
        if name not in cls.OS_INSTALLERS:
            err_msg = "Cannot found Installer '%s'!" % name
            logging.debug(err_msg)
            raise KeyError(err_msg)

        return cls.OS_INSTALLERS[name]


class PKInstaller(Installer):
    """Interface for package installer."""
    NAME = 'PKInstaller'
    PK_INSTALLERS = {}

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
    def register(cls, installer):
        if not issubclass(installer, PKInstaller):
            name = installer.NAME
            raise Exception("'%s' is not Package Installer type!", name)
        super(PKInstaller, cls).register(cls.PK_INSTALLERS, installer)

    @classmethod
    def get_package_installer(cls, name):
        if name not in cls.PK_INSTALLERS:
            err_msg = "Cannot found Installer '%s'!" % name
            logging.debug(err_msg)
            raise KeyError(err_msg)

        return cls.PK_INSTALLERS[name]
