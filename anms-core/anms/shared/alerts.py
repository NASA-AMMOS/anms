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

"""
Store new alerts into the database 
"""

from anms.shared.config import ConfigBuilder
from datetime import datetime
from anms.shared.opensearch_logger import OpenSearchLogger
from anms.models.relational import get_session

from anms.models.relational.alert import Alert
from anms.routes import alerts_ws

config = ConfigBuilder.get_config()
LOGGER = OpenSearchLogger(__name__, log_console=True).logger

async def store_alert(title: str, status: int, message: str):
    
    with get_session() as session:
    # insert new alert into the database 
        now = datetime.now()
        in_stm = Alert(title=title, status=status, message=message, created_at=now , updated_at=now)    
        session.add(in_stm)
        session.commit()
    
    # emit new websocket alert
    await alerts_ws.new_alert({"title":title, "status":status, "message":message, "created_at":now })

                
            