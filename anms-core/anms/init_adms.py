#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Management System (ANMS).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This work was performed for the Jet Propulsion Laboratory, California
# Institute of Technology, sponsored by the United States Government under
# the prime contract 80NM0018D0004 between the Caltech and NASA under
# subcontract 1658085.
#
''' A separate entrypoint to initialize the ADMs database from filesystem.
'''
import asyncio
import sys
import traceback
import sqlalchemy.exc
from paho import mqtt
from ace import AdmSet, Checker
from anms.models.relational import get_async_session
from anms.routes.adms.adm import handle_adm
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger


logger = OpenSearchLogger(__name__).logger


async def import_adms():
    ''' Scan filesystem for ADMs and import them if needed.
    If they are pre-existing there is no change
    '''
    # Wait for the DB to be accessible
    while True:
        try:
            async with get_async_session() as db_sess:
                await db_sess.execute("SELECT 1")
                break
        except (ConnectionError, sqlalchemy.exc.OperationalError):
            logger.info('Waiting for DB to be accessible...')
            await asyncio.sleep(1)

    admset = AdmSet(cache_dir=False)
    admset.load_default_dirs()
    issues = Checker(admset.db_session()).check()
    for iss in issues:
        logger.error('ADM issue %s', iss)

    for adm_file in admset:
        try:
            logger.info('ADM %s handling started', adm_file.norm_name)
            async with get_async_session() as db_sess:
                await handle_adm(admset, adm_file, db_sess, replace=False)
            logger.info('ADM %s handling finished', adm_file.norm_name)
        except Exception as err:
            # The function already logged any SQL issue at error severity
            logger.error('ADM %s handling failed: %s', adm_file.norm_name, err)
            logger.debug('%s', traceback.format_exc())

    # Notify the aricodec of startup
    config = ConfigBuilder.get_config()
    host = config.get('MQTT_HOST')
    port = config.get('MQTT_PORT')

    logger.info('Connecting to MQTT broker %s to notify aricodec', host)
    client = mqtt.client.Client()
    client.connect(host, port)
    msg = client.publish('aricodec/reload', b'')
    msg.wait_for_publish()
    client.disconnect()

    logger.info('Startup finished')


if __name__ == '__main__':
    asyncio.run(import_adms())
    sys.exit(0)
