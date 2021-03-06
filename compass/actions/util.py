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

"""Module to provide util for actions

   .. moduleauthor:: Xiaodong Wang ,xiaodongwang@huawei.com>
"""
import logging
import redis

from contextlib import contextmanager


@contextmanager
def lock(lock_name, blocking=True, timeout=10):
    redis_instance = redis.Redis()
    instance_lock = redis_instance.lock(lock_name, timeout=timeout)
    try:
        locked = instance_lock.acquire(blocking=blocking)
        if locked:
            logging.debug('acquired lock %s', lock_name)
            yield instance_lock
        else:
            logging.info('lock %s is already hold', lock_name)
            yield None

    except Exception as error:
        logging.info(
            'redis fails to acquire the lock %s', lock_name)
        logging.exception(error)
        yield None

    finally:
        instance_lock.acquired_until = 0
        instance_lock.release()
        logging.debug('released lock %s', lock_name)
