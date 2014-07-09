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
    TMPL_DIR = 'TMPL_DIR'
    COMPASS_DATABAG = "compass_databag"
    CHEFSERVER_URL = "chef_server_url"
    KEY = "key_path"
    CLIENT = "client_name"

    def __init__(self, adapter_info, config):
        super(ChefInstaller, self).__init__()

        self.config_manager = ChefConfigManager(adapter_info, config)
        installer_settings = self.config_manager.get_pk_installer_settings()

        tmpl_dir = os.path.join(setting.TMPL_DIR, self.NAME)
        self.env_dir = os.path.join(tmpl_dir, 'environments')
        self.databag_dir = os.path.join(tmpl_dir, 'databags')

        if self.CHEFSERVER_URL not in installer_settings:
            raise Exception("No chef server url provided!")

        self.installer_url_ = installer_settings[self.CHEFSERVER_URL]

        self.compass_databag = None
        key = None
        client = None
        if self.COMPASS_DATABAG in installer_settings:
            self.compass_databag = installer_settings[self.COMPASS_DATABAG]

        if self.KEY in installer_settings and self.CLIENT in installer_settings:
            key = installer_settings[self.KEY]
            client = installer_settings[self.CLIENT]

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

    def set_chef_env(self, node, env_name):
        """Set chef environment to node."""
        if not node:
            raise Exception("Node is None!")

        node_env = node.chef_environment
        if env_name != node_env:
            node.chef_environment = env_name

        node.save()

    def update_node_attributes(self, node_name, node_attr_dict):
        """Create or update node run_list and environment."""
        pass

    def create_or_update_environment(self, env_name, vars_dict):
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

    def create_or_update_databag(self, search_list):
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
        mapping_callback = getattr((os.path.join(self.mapping_callback_dir,
                                                 adapter_name)),
                                    'generate_deploy_config')
        deploy_config = {}
        if mapping_callback:
            deploy_config = mapping_callback(self.config_manager)
        else:
            # Use default callback to generate deploy_config
            deploy_config = self._generate_deploy_config()

        try:
            self.config_manager.set_deploy_config(deploy_config)
        except Exception as ex:
            raise Exception(ex.message)

        env_name = self._get_env_name(adapter_name)

        cheetah_search_list = self._get_tmpl_vars()
        self.create_or_update_environment(env_name, cheetah_search_list)

        host_list = self.config_manager.get_host_id_list()
        for host_id in host_list:
            node_name = self.config_manager.get_host_fullname(host_id)
            roles = self.config_manager.get_host_roles(host_id)

            node = self.get_node(node_name)
            self.set_chef_env(node, env_name)
            self.add_roles(node, roles)

        return deploy_config

    def _generate_deploy_config(self):
        """Re-organize the original os config for each host by grouping it
           by roles(KEY: "role_mapping"). Add some more config items
           to the new config. The format for re-organzied config will be:
        """
        pass

    def get_pk_info_for_os_installer(self):
        """Render chef config file (client.rb) by OS installing right after
           OS is installed successfully.
        """
        host_list = self.original_config['hosts']
        os_installer_configs = {}
        for host_info in host_list:
            temp = {
                "tool": "chef",
                "chef_url": self.installer_url_
            }
            temp['chef_client_name'] = host_info['fullname']
            temp['chef_node_name'] = host_info['fullname']
            os_installer_configs[host_info['host_id']] = temp

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

    def __get_compass_databag(self):
        import chef
        databags = chef.DataBag.list(api=self.api_)
        if self.compass_databag not in databags:
            raise Exception("Cannot find databag called '%s'!",
                            self.compass_databag)
        databag = chef.DataBag(self.compass_databag, self.api_)
        return databag

    def __get_compass_databag_item(self, item_name):
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
    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(ChefConfigManager, self).__init__(adapter_info,
                                                cluster_info,
                                                hosts_info)

    def get_network_mapping(self):
        cluster_pk_config = self.get_cluster_pk_config()
        if 'network_mapping' not in cluster_pk_config:
            logging.info("No keyword 'network_mapping' find!")
            return None

        return cluster_pk_config['network_mapping']

    def get_host_roles(self, host_id):
        host_info = self.get_host_info(host_id)
        if not host_info:
            return None

        return host_info['roles']

    def get_cluster_role_mapping(self):
        if not self.deploy_config:
            raise Exception('Deploy config has not been set yet!')

        return self.deploy_config['cluster']['role_mapping']
