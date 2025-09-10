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
''' A "unittest" which uses requests library to verify routes from a base URL.
'''

import logging
import os
import requests
import unittest
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
import websockets
import werkzeug
import json

LOGGER = logging.getLogger(__name__)


class BaseTest(unittest.TestCase):
    ''' Common test logic for login session management.
    '''
    COMPOSE_PROFILES = os.environ.get('COMPOSE_PROFILES', 'full')
    BASE_URL = os.environ.get('CHECKOUT_BASE_URL', 'http://localhost/')
    AUTHN_USER = os.environ.get('CHECKOUT_AUTHN_USER', 'admin')
    AUTHN_PASSWD = os.environ.get('CHECKOUT_AUTHN_PASSWD', 'admin')

    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)
        self.httpsess = requests.Session()
        self.httpsess.verify = os.environ.get('SSL_CERT_FILE')

    def tearDown(self):
        if 'session' in self.httpsess.cookies:
            self._do_logout()

    def _resolve(self, url):
        return urljoin(self.BASE_URL, url)

    def _require_response(self, url, **kwargs):
        method = kwargs.pop('method', 'GET').upper()
        req_data = kwargs.pop('req_data', None)
        req_json = kwargs.pop('req_json', None)
        req_headers = kwargs.pop('req_headers', None)
        resp_status = kwargs.pop('resp_status', [200])
        resp_ctype = kwargs.pop('resp_ctype', None)
        resp_json = kwargs.pop('resp_json', None)
        kwargs.setdefault('allow_redirects', False)
        resolved = self._resolve(url)

        LOGGER.info('Sending %s request to %s', method, resolved)
        resp = self.httpsess.request(
            method, resolved,
            headers=req_headers,
            data=req_data,
            json=req_json,
            **kwargs
        )
        LOGGER.info('Got response %s', resp)
        if resp_status is not None:
            self.assertIn(resp.status_code, resp_status)

        got_ctype = resp.headers.get('content-type')
        if got_ctype is not None:
            # just the type, no options
            got_ctype = werkzeug.http.parse_options_header(got_ctype)[0]
        if resp_ctype is not None:
            self.assertIn(got_ctype, resp_ctype)
        if resp_json is not None:
            resp_json = resp.json()
            self.assertDictEqual(resp_json, resp_json)

        return resp

    def _do_login(self, username, passwd):
        resp = self._require_response(
            url='/authn/dologin.html',
            method='POST',
            req_data={
                'httpd_username': username,
                'httpd_password': passwd,
            },
            resp_status=[302],
        )
        self.assertIn('session', self.httpsess.cookies)
        return resp

    def _do_logout(self):
        resp = self._require_response(
            url='/authn/dologout.html',
            method='POST',
            resp_status=[307],
        )
        self.assertNotIn('session', self.httpsess.cookies)
        return resp


class TestTls(BaseTest):

    def setUp(self):
        scanuri = urlsplit(self.BASE_URL)
        if scanuri.scheme != 'https':
            self.skipTest('Not an TLS-compatible CHECKOUT_BASE_URL')

    def test_tls_opts(self):
        from sslscan import Scanner
        from sslscan.module.scan import BaseScan

        # force to a scanner compatible URI
        scanuri = urlsplit(self.BASE_URL)
        if scanuri.scheme == 'https':
            scanuri = scanuri._replace(scheme='http')

        scanner = Scanner()
        mod_man = scanner.get_module_manager()
        mod_man.load_global_modules()

        scanner.append_load('server.ciphers', '')
        # scanner.append_load('server.renegotiation', '')

        for name in ["tls10", "tls11", "tls12"]:
            scanner.config.set_value(name, True)

        module = scanner.load_handler_from_uri(urlunsplit(scanuri))
        scanner.set_handler(module)
        scanner.reset_knowledge_base()
        scanner.run()

        skb = scanner.get_knowledge_base()
        LOGGER.info('SKB items: %s', skb._items)
        ciphers = set([
            item.protocol_version_name
            for item in skb.get('server.ciphers')
            if item.status_name == 'accepted'
        ])
        self.assertIn('TLSv12', ciphers)

        # self.assertTrue(skb.get('server.renegotiation.support'))
        # self.assertTrue(skb.get('server.renegotiation.secure'))


class TestAuthnz(BaseTest):
    ''' Exercise just the CAM gateway interface.
    '''

    def test_access_denied(self):
        resp = self._require_response(
            url='/',
            resp_status=[302],
        )
        self.assertEqual(
            self._resolve('/authn/login.html'),
            self._resolve(resp.headers['location'])
        )

    def test_authn_root(self):
        resp = self._require_response(
            url='/authn/',
            resp_status=[301],
        )
        self.assertEqual(
            self._resolve('/authn/login.html'),
            self._resolve(resp.headers['location'])
        )

    def test_login_page(self):
        resp = self._require_response(
            url='/authn/login.html',
            resp_status=[200],
            resp_ctype=['text/html'],
        )

    def test_login_nocreds(self):
        resp = self._require_response(
            url='/authn/dologin.html',
            method='POST',
            req_data={
            },
            resp_status=[302],
        )
        self.assertEqual(
            self._resolve('/authn/login.html'),
            self._resolve(resp.headers['location'])
        )
        self.assertEqual({}, self.httpsess.cookies)

    def test_login_valid(self):
        resp = self._require_response(
            url='/authn/dologin.html',
            method='POST',
            req_data={
                'httpd_username': self.AUTHN_USER,
                'httpd_password': self.AUTHN_PASSWD,
            },
            resp_status=[302],
        )
        self.assertIn('session', self.httpsess.cookies)
        sess = self.httpsess.cookies.get(name='session', path='/')
        self.assertIsNotNone(sess)

    def test_logout_page(self):
        resp = self._require_response(
            url='/authn/dologout.html',
            resp_status=[307],
            resp_ctype=['text/html'],
        )

    def test_logout_invalid(self):
        resp = self._require_response(
            url='/authn/dologout.html',
            method='POST',
            resp_status=[307],
        )
        self.assertNotIn('session', self.httpsess.cookies)


class TestPrimaryRoutes(BaseTest):
    ''' Exercise primary routes of the backend load balancer.
    '''

    def setUp(self):
        super(TestPrimaryRoutes, self).setUp()
        self._do_login(
            username=self.AUTHN_USER,
            passwd=self.AUTHN_PASSWD,
        )

    def test_anms_ui(self):
        if self.COMPOSE_PROFILES == 'light':
            self.skipTest('Using light profile')

        resp = self._require_response(
            url='/',
            resp_status=[200],
            resp_ctype=['text/html'],
        )
        resp = self._require_response(
            url='/home',
            resp_status=[200],
            resp_ctype=['text/html'],
        )
        resp = self._require_response(
            url='/monitor',
            resp_status=[200],
            resp_ctype=['text/html'],
        )
        resp = self._require_response(
            url='/agents',
            resp_status=[200, 401],
            resp_ctype=['text/html'],
        )
        resp = self._require_response(
            url='/build',
            resp_status=[200],
            resp_ctype=['text/html'],
        )
        resp = self._require_response(
            url='/build',
            resp_status=[200],
            resp_ctype=['text/html'],
        )

    def test_grafana(self):
        if self.COMPOSE_PROFILES == 'light':
            self.skipTest('Using light profile')

        resp = self._require_response(
            url='/grafana/',
            resp_status=[200],
        )

    def test_anms_core(self):
        resp = self._require_response(
            url='/core/hello',
            resp_status=[200],
            resp_ctype=['text/plain'],
        )
        resp = self._require_response(
            url='/core/docs/',
            resp_status=[200],
            resp_ctype=['text/html'],
        )

    def test_refdm(self):
        # any API access
        resp = self._require_response(
            url='/nm/nm/api/version',
            resp_status=[200],
            resp_ctype=['application/json'],
        )

        eid_seg = quote('ipn:2.5', safe="")
        agent_base = self._resolve(f'/nm/nm/api/agents/eid/{eid_seg}/')

        resp = self.httpsess.get(agent_base + 'reports')
        if resp.status_code == 404:
            resp = self._require_response(
                url='/nm/nm/api/agents',
                method='POST',
                req_headers={
                    'content-type': 'text/plain',
                },
                req_data='ipn:2.5',
                resp_status=[200],
            )

        resp = self._require_response(
            url=(agent_base + 'send?form=text'),
            method='POST',
            req_headers={
                'content-type': 'text/plain',
            },
            req_data='ari:/EXECSET/n=1;(//ietf/dtnma-agent/CTRL/inspect)\r\n',
            resp_status=[200],
        )


class TestWebsockets(BaseTest, unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        super(TestWebsockets, self).setUp()
        self._do_login(
            username=self.AUTHN_USER,
            passwd=self.AUTHN_PASSWD,
        )

    async def test_grafana_live(self):
        if self.COMPOSE_PROFILES == 'light':
            self.skipTest('Using light profile')

        cookies = (f'{key}={val}' for key, val in self.httpsess.cookies.items())
        wsuri = urlsplit(self._resolve('/grafana/api/live/ws'))
        if wsuri.scheme == 'http':
            wsuri = wsuri._replace(scheme='ws')
        elif wsuri.scheme == 'https':
            wsuri = wsuri._replace(scheme='wss')
        kwargs = {
            'uri': urlunsplit(wsuri),
            'additional_headers': {
                'Cookie': '; '.join(cookies),
            },
        }
        async with websockets.connect(**kwargs) as wsc:
            pong_waiter = await wsc.ping()
            await pong_waiter

            await wsc.close()
            await wsc.wait_closed()
