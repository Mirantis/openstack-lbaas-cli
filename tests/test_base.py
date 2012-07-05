from .utils import unittest

import mock

from balancerclient.common.client import HTTPClient
from balancerclient.common.base import Manager, Resource


class TestManager(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock(spec=HTTPClient)
        self.manager = Manager(self.api)
        self.patcher = mock.patch.object(self.manager, 'resource_class')
        self.resource = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_list(self):
        self.api.json_request.return_value = (mock.Mock(),
                                              {'data': [{'id': 'fakeid1'},
                                                        {'id': 'fakeid2'}]})
        objs = self.manager._list('/fakes', 'data')
        expected = [mock.call(self.manager, {'id': 'fakeid1'}, loaded=True),
                    mock.call(self.manager, {'id': 'fakeid2'}, loaded=True)]
        self.assertTrue(self.api.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.api.json_request.mock_calls,
                         [mock.call('GET', '/fakes')])
        self.assertEqual(self.resource.mock_calls, expected)

    def test_delete(self):
        self.manager._delete('/fakes')
        self.assertTrue(self.api.raw_request.called)
        self.assertEqual(self.api.raw_request.mock_calls,
                         [mock.call('DELETE', '/fakes')])

    def test_update(self):
        self.api.json_request.return_value = (mock.Mock(),
                                              {'data': {'id': 'fakeid'}})
        body = {'data': {'id': 'fakeid',
                         'name': 'fakename'}}
        obj = self.manager._update('/fakes', body, response_key='data')
        self.assertTrue(self.api.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.api.json_request.mock_calls,
                         [mock.call('PUT', '/fakes', body=body)])
        self.assertEqual(self.resource.mock_calls,
                         [mock.call(self.manager, {'id': 'fakeid'})])

    def test_create(self):
        self.api.json_request.return_value = (mock.Mock(),
                                              {'data': {'id': 'fakeid'}})
        body = {'data': {'id': 'fakeid',
                         'name': 'fakename'}}
        obj = self.manager._create('/fakes', body, 'data')
        self.assertTrue(self.api.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.api.json_request.mock_calls,
                         [mock.call('POST', '/fakes', body=body)])
        self.assertEqual(self.resource.mock_calls,
                         [mock.call(self.manager, {'id': 'fakeid'})])

    def test_create_raw(self):
        self.api.json_request.return_value = (mock.Mock(),
                                              {'data': {'id': 'fakeid'}})
        body = {'data': {'id': 'fakeid',
                         'name': 'fakename'}}
        obj = self.manager._create('/fakes', body, 'data', return_raw=True)
        self.assertTrue(self.api.json_request.called)
        self.assertFalse(self.resource.called)
        self.assertEqual(self.api.json_request.mock_calls,
                         [mock.call('POST', '/fakes', body=body)])
        self.assertEqual(obj, {'id': 'fakeid'})

    def test_get(self):
        self.api.json_request.return_value = (mock.Mock(),
                                              {'data': {'id': 'fakeid'}})
        obj = self.manager._get('/fakes', 'data')
        self.assertTrue(self.api.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.api.json_request.mock_calls,
                         [mock.call('GET', '/fakes')])
