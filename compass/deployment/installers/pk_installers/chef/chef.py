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

"""package installer: chef plugin."""
import logging
import os
import shutil
import simplejson as json

from Cheetah.Template import Template
from compass.deployment.installers.config_manager import BaseConfigManager
from compass.deployment.installers.installer import PKInstaller
from compass.utils import setting_wrapper as setting
from compass.utils import util


class ChefInstaller(PKInstaller):
    """chef package installer."""
    NAME = 'chef'
    ENV_TMPL_NAME = 'env.tmpl'
    NODE_TMPL_NAME = 'node.tmpl'
    DATABAGITEM_TMPL_NAME = 'databagitem.tmpl'

    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(ChefInstaller, self).__init__()

        self.config_manager = ChefConfigManager(adapter_info, cluster_info,
                                                hosts_info)
        self.tmpl_dir = self.config_manager.get_target_system_tmpl_dir()
        self.installer_url_ = self.config_manager.get_chef_url()
        self.databag = self.config_manager.get_databag_name()
        key, client = self.config_manager.get_chef_credentials()

        self.api_ = self._get_chef_api(key, client)
        logging.debug('%s instance created', self)

    def __repr__(self):
        return '%s[name=%s,installer_url=%s,global_databag_name=%s]' % (
            self.__class__.__name__, self.NAME, self.installer_url_,
            self.global_databag_name_)

    def _get_chef_api(self, key=None, client=None):
        """Initializes chef API client."""
        import chef
        chef_api = None
        try:
            if key and client:
                chef_api = chef.ChefAPI(self.installer_url_, key, client)
            else:
                chef_api = chef.autoconfigure()

        except Exception as ex:
            raise Exception("Failed to instantiate chef API, error: %s",
                            ex.message)
        return chef_api

    def get_env_name(self, adapter_name, cluster_id):
        return "-".join((adapter_name, cluster_id))

    def get_node(self, node_name):
        """Get chef node."""
        import chef
        if not self.api_:
            logging.info("Cannot find ChefAPI object!")
            raise Exception("Cannot find ChefAPI object!")

        node = chef.Node(node_name, api=self.api_)
        if node not in chef.Node.list(api=self.api_):
            # Create this node on chef server.
            node.save()

        return node

    def delete_node(self, node):
        """clean node attributes about target system."""
        # TODO: clean its log
        import chef
        if node is None:
            raise Exception("Node is None, cannot delete a none node.")
        node_name = node.name
        client_name = node_name
        try:
            node.delete()
            client = chef.Client(client_name, api=self.api_)
            client.delete()
            logging.debug('delete node %s', node_name)
            log_dir_prefix = setting.INSTALLATION_LOGDIR[self.NAME]
            self._clean_log(log_dir_prefix, node_name)
        except Exception as error:
            logging.debug(
                'failed to delete node %s, error: %s', node_name, error)

    def add_roles(self, node, roles):
        """Add roles to the node."""
        if node is None:
            raise Exception("Node is None!")

        if not roles:
            logging.info("Role list is None. Run list will no change.")
            return

        run_list = node.run_list
        for role in roles:
            if role not in run_list:
                node.run_list.append('role[%s]' % role)

        node.save()
        logging.debug('The Run List for node %s is %s',
                      node.name, node.run_list)

    def set_node_env(self, node, env_name):
        """Set chef environment to node."""
        if not node:
            raise Exception("Node is None!")

        node_env = node.chef_environment
        if not node_env or node_env == 'default':
            node.chef_environment = env_name

        node.save()

    def update_node_attributes(self, node, vars_dict):
        """Create or update node run_list and environment."""

        node_tmpl_dir = os.path.join(self.tmpl_dir, self.NODE_TMPL_NAME)
        if not os.path.exists(node_tmpl_dir):
            logging.info(("No node template found!"
                          "No attributes will be updated!"))
            return
        node_tmpl = Template(file=node_tmpl_dir, searchList=[vars_dict])
        node_attr_dict = json.loads(node_tmpl.respond())

        for attr in node_attr_dict:
            setattr(node, attr, node_attr_dict[attr])

        node.save()

    def update_environment(self, env_name, vars_dict):
        """Generate environment config based on the template file and
           upload it to chef server. Return environment name.
        """
        import chef
        env_tmpl_file = os.path.join(self.env_dir, env_name)
        if not os.path.exists(env_tmpl_file):
            logging.info("No environment template is found!!")
            return

        env_tmpl = Template(file=env_tmpl_file, searchList=[vars_dict])
        env_content = json.loads(env_tmpl.respond())

        env = chef.Environment(env_name, api=self.api_)
        for attr in env_content:
            if attr in env.attributes:
                setattr(env, attr, env_content[attr])
        env.save()

    def update_databag(self, vars_dict):
        """Generate databag config based on the template file and upload
           it to chef server. Return databag name.
        """
        pass

    def _get_tmpl_vars(self):
        pk_metadata = self.config_manager.get_pk_config_meatadata()
        pk_config = self.config_manager.get_cluster_pk_config()
        vars_dict = self._Installer._get_tmpl_vars_from_metadata(pk_metadata,
                                                                 pk_config)
        role_mapping_config = self.config_manager.get_cluster_role_mapping()
        util.merge_dict(vars_dict, role_mapping_config)
        return vars_dict


    def deploy(self):
        """Start to deploy system."""
        if not self.config:
            raise Exception("No config for package installer found!")
        adapter_name = self.config_manager.get_adapter_name()
        env_name = self._get_env_name(adapter_name)

        cheetah_search_list = self._get_tmpl_vars()
        self.update_environment(env_name, cheetah_search_list)

        host_list = self.config_manager.get_host_id_list()
        for host_id in host_list:
            node_name = self.config_manager.get_host_fullname(host_id)
            roles = self.config_manager.get_host_roles(host_id)

            node = self.get_node(node_name)
            self.set_node_env(node, env_name)
            self.add_roles(node, roles)

    def generate_installer_config(self):
        """Render chef config file (client.rb) by OS installing right after
           OS is installed successfully.
           The output format: 
           {
              '1'($host_id):{
                  'tool': 'chef',
                  'chef_url': 'https://xxx',
                  'chef_client_name': '$host_fullname',
                  'chef_node_name': '$host_fullname'
              },
              .....
           }
        """
        host_ids = self.config_manager.get_host_id_list()
        os_installer_configs = {}
        for host_id in host_ids:
            fullname = self.config_manager.get_host_fullname(host_id)
            temp = {
                "tool": "chef",
                "chef_url": self.installer_url_
            }
            temp['chef_client_name'] = fullname
            temp['chef_node_name'] = fullname
            os_installer_configs[host_id] = temp

        return os_installer_configs

    def clean_progress(self):
        """Clean all installing log about the node."""
        log_dir_prefix = setting.INSTALLATION_LOGDIR[self.NAME]
        hosts_list = self.config_manager.get_host_id_list()
        for host_id in hosts_list:
            fullname = self.config_manager.get_host_fullname()
            self._clean_log(log_dir_prefix, fullname)

    def _clean_log(self, log_dir_prefix, node_name):
        log_dir = os.path.join(log_dir_prefix, node_name)
        shutil.rmtree(log_dir, True)

    def get_supported_target_systems(self):
        """get target systems from chef. All target_systems for compass will
           be stored in the databag called "compass".
        """
        databag = self.__get_compass_databag()
        target_systems = {}
        for system_name, item in databag:
            target_systems[system_name] = item

        return target_systems

    def __get_databag_item(self, item_name):
        """Get compass databag item."""
        import chef
        databag = self.__get_compass_databag()
        databag_items = chef.DataBagItem.list(self.api_)
        if item_name not in databag_items:
            logging.info("No item '%s' was found in the databag %s",
                         item_name, self.compass_databag)
            return None

        item = chef.DataBagItem(databag, item_name, api=self.api_)

        return item

    def _update_databag_item(self, adapter_name, item_name, config, save=True):
        """update databag item."""
        pass

    def _clean_databag_item(self, target_system, bag_item_name):
        """clean databag item."""
        import chef
        databag_items = self.tmp_databag_items_.setdefault(
            target_system, {})
        if bag_item_name not in databag_items:
            databag = self._get_databag(target_system)
            databag_items[bag_item_name] = chef.DataBagItem(
                databag, bag_item_name, api=self.api_)

        bag_item = databag_items[bag_item_name]
        try:
            bag_item.delete()
            logging.debug(
                'databag item %s is removed from target_system %s',
                bag_item_name, target_system)
        except Exception as error:
            logging.debug(
                'no databag item %s to delete from target_system %s: %s',
                bag_item_name, target_system, error)

        del databag_items[bag_item_name]

    def redeploy(self):
        """reinstall host."""
        pass


PKInstaller.register(ChefInstaller)


class ChefConfigManager(BaseConfigManager):
    TMPL_DIR = 'template_dir'
    DATABAG_NAME = "databag"
    CHEFSERVER_URL = "chef_server_url"
    KEY_DIR = "key_dir"
    CLIENT = "client_name"

    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(ChefConfigManager, self).__init__(adapter_info,
                                                cluster_info,
                                                hosts_info)

    def get_target_system_tmpl_dir(self):
        pk_installer_settings = self.get_pk_installer_settings()
        if self.TMPL_DIR not in pk_installer_settings:
            raise KeyError("'%s' must be set in package settings!",
                           self.TMPL_DIR)
        return pk_installer_settings[self.TMPL_DIR]

    def get_chef_url(self):
        pk_installer_settings = self.get_pk_installer_settings()
        if self.CHEFSERVER_URL not in pk_installer_settings:
            raise KeyError("'%s' must be set in package settings!",
                           self.CHEFSERVER_URL)

        return pk_installer_settings[self.CHEFSERVER_URL]

    def get_chef_credentials(self):
        pk_installer_settings = self.get_pk_installer_settings()
        if self.KEY_DIR in pk_installer_settings and\
            self.CLIENT in pk_installer_settings:
            cred = (pk_installer_settings[self.KEY_DIR],
                    pk_installer_settings[self.CLIENT])
            return cred

        return (None, None)

    def get_databag_name(self):
        pk_installer_settings = self.get_pk_installer_settings()
        if self.DATABAG_NAME not in pk_installer_settings:
            logging.info("No databag name provided for this adapter!")
            return None

        return pk_installer_settings[self.DATABAG_NAME]
