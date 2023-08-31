#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import logging
import sys
from datetime import timedelta

from sqlalchemy.orm import Session
from tenacity import (after_log, before_log, retry, stop_after_attempt,
                      wait_fixed)

from anms.components import schemas
from anms.models.relational import get_session
from anms.models.relational.user import User
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger

max_tries = timedelta(minutes=1).total_seconds()  # max number of retries
wait_seconds = timedelta(seconds=1).total_seconds()  # retry every n


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def verify_connectivity() -> None:
    try:
        with get_session() as db:
            # Try to create session to check if DB is awake
            db.execute("SELECT 1")
    except Exception as e:
        logger.error("Connection Error", exc_info=e)
        raise e


def seed_data(db: Session) -> None:
    pass


def main() -> None:
    logger.info("Initializing DB Connectivity")
    verify_connectivity()
    logger.info("DB Connected")
    with get_session() as session:
        seed_data(session)


if __name__ == "__main__":
    main()
