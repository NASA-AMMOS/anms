#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Managment System (ANMS).
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
from unittest import mock
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from sqlalchemy import func, select
from sqlalchemy.engine import Result
from sqlalchemy.sql import Select

from anms.asgi import FastApiApp
from fastapi import status

# Need to use the full app rather than just ari.router
# This is because AsyncClient adds "/" to the base_url which fails to match @router.get("") paths
from anms.models.relational.ari import ARI
from anms.routes.mappings import RoutesMapper

app: FastApiApp = FastApiApp()
# get the prefix that this is API is registered with.
# Strip off the trailing "/" so that the root get("") is routed correctly
prefix: str = RoutesMapper.ari_api_prefix.rstrip("/")


def get_client() -> AsyncClient:
    return AsyncClient(app=app.app, base_url="http://test")


class AsyncUnifiedAlchemyMagicMock(UnifiedAlchemyMagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncUnifiedAlchemyMagicMock, self).__call__(*args, **kwargs)


# TODO Mocking Async + SQLAlchemy + Pagination does not seem to be very straight forward:
#   * Package mock-alchemy doesn't seem to support async natively so a subclass defined to jam in async support is needed
#   * Issues with built in 'scalar' support when used as session.scalar
#   * Not clear how to mock items returned by executing paginated query such that you can call scalars().unique().all() on it
#   * Plus mocking paginate() or the return statement within pagenate, is basically replacing the one statement in this function so what's the point of the test?
@pytest.mark.skip("Incomplete mocking of database")
class TestGetRoot:

    @pytest.mark.anyio
    @mock.patch('anms.models.relational.async_session_factory')
    async def test_root_paged(self, m_session_factory, mocker):
        # set up mock session
        aris_in_db = [
            ARI(obj_metadata_id=1,
                obj_id=1,
                actual=True),
            ARI(obj_metadata_id=2,
                obj_id=2,
                actual=True)
            # TODO would need more to test expected paging behavior
        ]

        mock_session = AsyncUnifiedAlchemyMagicMock(data=[
            (  # Not sure if this ever gets used within paginate
                [mock.call.select(ARI)],
                [aris_in_db]
            ),
            (  # Tried this to provide a Result when execute is called within paginate but doesn't work
                [mock.call.execute(Select)],
                [aris_in_db]
            ),
            (  # tried this to mock session.scalar(select(...)) as called inside of paginate.  didn't work
                [mock.call.select(func.count())],
                len(aris_in_db)
            ),
        ])
        # this seems to be needed to get around 'scalar' function already implemented by AlchemyMagicMock that fails
        mock_session.scalar = AsyncUnifiedAlchemyMagicMock(return_value=len(aris_in_db))
        # TODO This still results in error because paginate expects session.execute to return a Result.  How to mock?
        # set up mock session_factory to return mock session
        m_session_factory.return_value = mock_session

        async with get_client() as ac:
            response = await ac.get(prefix)
        assert response.status_code == status.HTTP_200_OK
        # TODO assert expected result model is applied: Page[schemas.ARI]
        # TODO compare response.content (?) to what is expected

        # TODO test paging parameters (needs more data)



@pytest.mark.skip("Incomplete mocking of database")
class TestGetAll:

    @pytest.mark.anyio
    @mock.patch('anms.models.relational.async_session_factory')
    async def test_all_ari(self, m_session_factory):
        # set up mock session
        aris_in_db = [
            ARI(obj_metadata_id=1,
                obj_id=1,
                actual=True),
            ARI(obj_metadata_id=2,
                obj_id=2,
                actual=True)
        ]

        mock_session = AsyncUnifiedAlchemyMagicMock(data=[
            # TODO None of these seem to result in actual data appearing in the result
            (
                [mock.call.select(ARI)],
                [aris_in_db]
            ),
            (
                [mock.call.scalars(select(ARI))],
                [aris_in_db]
            ),
            (
                [mock.call.scalars(ARI)],
                [aris_in_db]
            ),
        ])
        m_session_factory.return_value = mock_session
        async with get_client() as ac:
            response = await ac.get(prefix + "/all")
        assert response.status_code == status.HTTP_200_OK
        # TODO assert expected result model is applied: List[schemas.ARI]
        # TODO compare response.content (?) to what is expected


# TODO implement tests for
#  /all/display
#  /id/display/{obj_metadata_id}/{obj_id}
#  /id/{obj_metadata_id}/{obj_id}
#  /name/display/{obj_name}
#  /name/{obj_name}
