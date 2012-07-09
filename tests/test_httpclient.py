import unittest2
import mock

from balancerclient.common import client
from balancerclient.common import exceptions


class TestHTTPClient(unittest2.TestCase):
    def setUp(self):
        self.client = client.HTTPClient(endpoint='http://localhost:8181',
                                        token='faketoken')

    @mock.patch('httplib2.Http.request', autospec=True)
    def test_http_request_default_headers(self, mock_req):
        mock_req.return_value = (mock.Mock(status=200), 'fakebody')
        resp, body = self.client._http_request('http://fakes', 'GET')
        headers = {'User-Agent': 'python-balancerclient',
                   'X-Auth-Token': 'faketoken'}
        expected = mock.call(self.client, 'http://fakes', 'GET',
                             headers=headers)
        self.assertTrue(mock_req.called)
        self.assertEqual(mock_req.mock_calls, [expected])
        self.assertEqual(body, 'fakebody')

    @mock.patch('httplib2.Http.request', autospec=True)
    def test_http_request_custom_headers(self, mock_req):
        mock_req.return_value = (mock.Mock(status=200), 'fakebody')
        resp, body = self.client._http_request('http://fakes', 'GET',
                             headers={'Content-Type': 'application/json'})
        headers = {'User-Agent': 'python-balancerclient',
                   'X-Auth-Token': 'faketoken',
                   'Content-Type': 'application/json'}
        expected = mock.call(self.client, 'http://fakes',
                             'GET', headers=headers)
        self.assertTrue(mock_req.called)
        self.assertEqual(mock_req.mock_calls, [expected])
        self.assertEqual(body, 'fakebody')

    @mock.patch('httplib2.Http.request', autospec=True)
    def test_http_request_redirect(self, mock_req):
        mock_redirect = mock.MagicMock(status=302)
        mock_redirect.__getitem__.return_value = 'http://location'
        mock_req.side_effect = iter(((mock_redirect, 'fakebody1'),
                                    (mock.Mock(status=200), 'fakebody2')))
        resp, body = self.client._http_request('http://fakes', 'GET')
        headers = {'User-Agent': 'python-balancerclient',
                   'X-Auth-Token': 'faketoken'}
        expected = [mock.call(self.client, 'http://fakes', 'GET',
                              headers=headers),
                    mock.call(self.client, 'http://location', 'GET',
                              headers=headers)]
        self.assertTrue(mock_req.called)
        self.assertEqual(mock_req.mock_calls, expected)
        self.assertEqual(body, 'fakebody2')

    @mock.patch('json.loads', autospec=True)
    @mock.patch('json.dumps', autospec=True)
    @mock.patch('balancerclient.common.exceptions.from_response',
                autospec=True)
    @mock.patch('balancerclient.common.client.HTTPClient._http_request',
                autospec=True)
    def test_json_request(self, mock_http_request, mock_from_response,
                          mock_json_dumps, mock_json_loads):
        mock_http_request.return_value = (mock.Mock(status=200),
                                          '{"id": "fake2"}')
        mock_json_dumps.return_value = '{"id": "fake1"}'
        mock_json_loads.return_value = {'id': 'fake2'}
        resp, body = self.client.json_request('POST', '/fakes',
                                              body={'id': 'fake1'})
        expected = mock.call(self.client, 'http://localhost:8181/fakes',
                             'POST',
                             body='{"id": "fake1"}',
                             headers={'Content-Type': 'application/json'})
        self.assertTrue(mock_json_dumps.called)
        self.assertTrue(mock_http_request.called)
        self.assertTrue(mock_json_loads.called)
        self.assertFalse(mock_from_response.called)
        self.assertEqual(mock_json_dumps.mock_calls,
                         [mock.call({'id': 'fake1'})])
        self.assertEqual(mock_json_loads.mock_calls,
                         [mock.call('{"id": "fake2"}')])
        self.assertEqual(body, {'id': 'fake2'})
        self.assertEqual(mock_http_request.mock_calls, [expected])

    @mock.patch('json.loads', autospec=True)
    @mock.patch('json.dumps', autospec=True)
    @mock.patch('balancerclient.common.exceptions.from_response',
                autospec=True)
    @mock.patch('balancerclient.common.client.HTTPClient._http_request',
                autospec=True)
    def test_json_request_nobody(self, mock_http_request, mock_from_response,
                                 mock_json_dumps, mock_json_loads):
        mock_http_request.return_value = (mock.Mock(status=200), None)
        resp, body = self.client.json_request('POST', '/fakes')
        expected = mock.call(self.client, 'http://localhost:8181/fakes',
                             'POST',
                             headers={'Content-Type': 'application/json'})
        self.assertFalse(mock_json_dumps.called)
        self.assertTrue(mock_http_request.called)
        self.assertFalse(mock_json_loads.called)
        self.assertFalse(mock_from_response.called)
        self.assertEqual(mock_http_request.mock_calls, [expected])

    @mock.patch('json.loads', autospec=True)
    @mock.patch('json.dumps', autospec=True)
    @mock.patch('balancerclient.common.exceptions.from_response',
                autospec=True)
    @mock.patch('balancerclient.common.client.HTTPClient._http_request',
                autospec=True)
    def test_json_request_loads_failed(self, mock_http_request,
                                       mock_from_response, mock_json_dumps,
                                       mock_json_loads):
        mock_json_loads.side_effect = ValueError()
        mock_http_request.return_value = (mock.Mock(status=200),
                                          '{"id": "fake"}')
        resp, body = self.client.json_request('GET', '/fakes')
        self.assertFalse(mock_json_dumps.called)
        self.assertTrue(mock_http_request.called)
        self.assertTrue(mock_json_loads.called)
        self.assertFalse(mock_from_response.called)
        self.assertEqual(body, '{"id": "fake"}')

    @mock.patch('json.loads', autospec=True)
    @mock.patch('json.dumps', autospec=True)
    @mock.patch('balancerclient.common.exceptions.from_response',
                autospec=True)
    @mock.patch('balancerclient.common.client.HTTPClient._http_request',
                autospec=True)
    def test_json_request_fake_status(self, mock_http_request,
                                      mock_from_response, mock_json_dumps,
                                      mock_json_loads):
        mock_from_response.return_value = fake_error = ValueError('fake')
        mock_http_request.return_value = mock_resp = (mock.Mock(status=401),
                                                      None)
        with self.assertRaises(ValueError) as cm:
            resp, body = self.client.json_request('GET', '/fakes')
        self.assertFalse(mock_json_dumps.called)
        self.assertTrue(mock_http_request.called)
        self.assertFalse(mock_json_loads.called)
        self.assertTrue(mock_from_response.called)
        self.assertEqual(mock_from_response.mock_calls,
                         [mock.call(*mock_resp)])
        self.assertEqual(cm.exception, fake_error)

    @mock.patch('balancerclient.common.exceptions.from_response',
                autospec=True)
    @mock.patch('balancerclient.common.client.HTTPClient._http_request',
                autospec=True)
    def test_raw_request(self, mock_http_request, mock_from_response):
        mock_http_request.return_value = (mock.Mock(status=200), 'fakebody')
        resp, body = self.client.raw_request('POST', '/fakes')
        expected = mock.call(self.client, 'http://localhost:8181/fakes',
                             'POST',
                             headers={'Content-Type':
                                            'application/octet-stream'})
        self.assertTrue(mock_http_request.called)
        self.assertFalse(mock_from_response.called)
        self.assertEqual(mock_http_request.mock_calls, [expected])

    @mock.patch('balancerclient.common.exceptions.from_response',
                autospec=True)
    @mock.patch('balancerclient.common.client.HTTPClient._http_request',
                autospec=True)
    def test_raw_request_fake_status(self, mock_http_request,
                                     mock_from_response):
        mock_from_response.return_value = fake_error = ValueError('fake')
        mock_http_request.return_value = (mock.Mock(status=401), 'fakebody')
        with self.assertRaises(ValueError) as cm:
            resp, body = self.client.raw_request('POST', '/fakes')
        expected = mock.call(self.client, 'http://localhost:8181/fakes',
                             'POST',
                             headers={'Content-Type':
                                            'application/octet-stream'})
        self.assertTrue(mock_http_request.called)
        self.assertTrue(mock_from_response.called)
        self.assertEqual(mock_http_request.mock_calls, [expected])
        self.assertEqual(cm.exception, fake_error)


class TestAuthHttpClient(unittest2.TestCase):
    def setUp(self):
        self.patcher1 = mock.patch('balancerclient.common.client.HTTPClient.'
                                   '_json_request', autospec=True)
        self.patcher2 = mock.patch('balancerclient.common.client.'
                                   'ServiceCatalog')
        self.mock_json_request = self.patcher1.start()
        self.mock_json_request.return_value = (mock.Mock(status=200),
                                               {'access': 'fakecatalog'})
        self.mock_service_catalog = self.patcher2.start()
        self.mock_service_catalog.return_value = mock_catalog = mock.Mock()
        self.get_token = mock_catalog.get_token = mock.Mock()
        self.url_for = mock_catalog.url_for = mock.Mock()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_authenticate(self):
        self.get_token.return_value = {'id': 'fakeid',
                                       'tenant_id': 'faketenantid'}
        self.url_for.return_value = 'http://localhost:8181'
        cl = client.HTTPClient(username='fakeuser', password='fakepass',
                               tenant_name='fake', auth_url='http://fakes',
                               region_name='fakeregion')
        expected = mock.call(cl, 'POST', 'http://fakes/tokens',
                             body={'auth': {'passwordCredentials':
                                                {'username': 'fakeuser',
                                                'password': 'fakepass'},
                                            'tenantName': 'fake'}})
        self.assertTrue(self.mock_json_request.called)
        self.assertTrue(self.mock_service_catalog.called)
        self.assertTrue(self.get_token.called)
        self.assertTrue(self.url_for.called)
        self.assertEqual(self.mock_json_request.mock_calls, [expected])
        self.assertEqual(self.mock_service_catalog.mock_calls,
                         [mock.call('fakecatalog'),
                          mock.call().get_token(),
                          mock.call().url_for(attr='region',
                                              filter_value='fakeregion')])
        self.assertEqual(cl.endpoint, 'http://localhost:8181')

    def test_authenticate_failure(self):
        self.get_token.return_value = {}
        with self.assertRaises(exceptions.AuthorizationFailure) as cm:
            cl = client.HTTPClient(username='fakeuser', password='fakepass',
                                   tenant_name='fake', auth_url='http://fakes',
                                   region_name='fakeregion')
        self.assertTrue(self.mock_json_request.called)
        self.assertTrue(self.mock_service_catalog.called)
        self.assertTrue(self.get_token.called)
        self.assertFalse(self.url_for.called)
