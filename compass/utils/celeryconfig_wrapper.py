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

"""celeryconfig wrapper.

   .. moduleauthor:: Xiaodong Wang <xiaodongwang@huawei.com>
"""
import logging
import os.path

from compass.utils import setting_wrapper as setting


CELERY_RESULT_BACKEND = 'amqp://'

BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_IMPORTS = ('compass.tasks.tasks',)


if setting.CELERYCONFIG_FILE:
    CELERY_CONFIG = os.path.join(
        setting.CELERYCONFIG_DIR,
        setting.CELERYCONFIG_FILE)

    try:
        logging.info('load celery config from %s', CELERY_CONFIG)
        execfile(CELERY_CONFIG, globals(), locals())
    except Exception as error:
        logging.exception(error)
        raise error