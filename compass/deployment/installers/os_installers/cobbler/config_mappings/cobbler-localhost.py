# Copyright 2014 Huawei Technologies Co. Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""os installer cobbler plugin.

.. moduleauthor:: Xiaodong Wang <xiaodongwang@huawei.com>
"""
import functools
from compass.config_management.utils.config_translator import ConfigTranslator
from compass.config_management.utils.config_translator import KeyTranslator
from compass.config_management.utils import config_translator_callbacks


TO_HOST_TRANSLATOR = ConfigTranslator(
    mapping={
        '/networking/global/gateway': [KeyTranslator(
            translated_keys=['/gateway']
        )],
        '/networking/global/nameservers': [KeyTranslator(
            translated_keys=['/name_servers']
        )],
        '/networking/global/search_path': [KeyTranslator(
            translated_keys=['/name_servers_search']
        )],
        '/networking/global/proxy': [KeyTranslator(
            translated_keys=['/ksmeta/proxy']
        )],
        '/networking/global/ignore_proxy': [KeyTranslator(
            translated_keys=['/ksmeta/ignore_proxy']
        )],
        '/networking/global/ntp_server': [KeyTranslator(
            translated_keys=['/ksmeta/ntp_server']
        )],
        '/security/server_credentials/username': [KeyTranslator(
            translated_keys=['/ksmeta/username']
        )],
        '/security/server_credentials/password': [KeyTranslator(
            translated_keys=['/ksmeta/password'],
            translated_value=config_translator_callbacks.get_encrypted_value
        )],
        '/partition': [KeyTranslator(
            translated_keys=['/ksmeta/partition']
        )],
        '/networking/interfaces/*/mac': [KeyTranslator(
            translated_keys=[functools.partial(
                config_translator_callbacks.get_key_from_pattern,
                to_pattern='/modify_interface/macaddress-%(nic)s')],
            from_keys={'nic': '../nic'},
            override=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management')
        )],
        '/networking/interfaces/*/ip': [KeyTranslator(
            translated_keys=[functools.partial(
                config_translator_callbacks.get_key_from_pattern,
                to_pattern='/modify_interface/ipaddress-%(nic)s')],
            from_keys={'nic': '../nic'},
            override=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management')
        )],
        '/networking/interfaces/*/netmask': [KeyTranslator(
            translated_keys=[functools.partial(
                config_translator_callbacks.get_key_from_pattern,
                to_pattern='/modify_interface/netmask-%(nic)s')],
            from_keys={'nic': '../nic'},
            override=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management')
        )],
        '/networking/interfaces/*/dns_alias': [KeyTranslator(
            translated_keys=[functools.partial(
                config_translator_callbacks.get_key_from_pattern,
                to_pattern='/modify_interface/dnsname-%(nic)s')],
            from_keys={'nic': '../nic'},
            override=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management')
        )],
        '/networking/interfaces/*/nic': [KeyTranslator(
            translated_keys=[functools.partial(
                config_translator_callbacks.get_key_from_pattern,
                to_pattern='/modify_interface/static-%(nic)s')],
            from_keys={'nic': '../nic'},
            translated_value=True,
            override=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management'),
        ), KeyTranslator(
            translated_keys=[functools.partial(
                config_translator_callbacks.get_key_from_pattern,
                to_pattern='/modify_interface/management-%(nic)s')],
            from_keys={'nic': '../nic'},
            translated_value=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management'),
            override=functools.partial(
                config_translator_callbacks.override_path_has,
                should_exist='management')
        ), KeyTranslator(
            translated_keys=['/ksmeta/promisc_nics'],
            from_values={'promisc': '../promisc'},
            translated_value=functools.partial(
                config_translator_callbacks.add_value,
                get_value_callback=lambda config: [
                    value for value in config.split(',') if value
                ],
                return_value_callback=lambda values: ','.join(values)
            ),
            override=True
        )],
    }
)
