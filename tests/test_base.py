import unittest2
import mock

from balancerclient.common.client import HTTPClient
from balancerclient.common import base


class MockWithoutAttrs(mock.Mock):
    def __init__(self, exclude_attrs=(), **kwargs):
        super(MockWithoutAttrs, self).__init__(**kwargs)
        self.exclude_attrs = exclude_attrs

    def __getattr__(self, name):
        if name in self.exclude_attrs:
            raise AttributeError(name)
        return super(MockWithoutAttrs, self).__getattr__(name)


class TestGetID(unittest2.TestCase):
    def test_get_id_without_id(self):
        mock_obj = MockWithoutAttrs(exclude_attrs=('id',))
        obj = base.getid(mock_obj)
        self.assertEqual(obj, mock_obj)

    def test_get_id_with_id(self):
        mock_obj = mock.Mock(id='fakeid')
        id = base.getid(mock_obj)
        self.assertEqual(id, 'fakeid')


class TestManager(unittest2.TestCase):
    def setUp(self):
        self.client = mock.Mock(spec=HTTPClient)
        self.api = mock.Mock(client=self.client)
        self.manager = base.Manager(self.api)
        self.patcher = mock.patch.object(self.manager, 'resource_class')
        self.resource = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_list(self):
        self.client.json_request.return_value = \
            (mock.Mock(), {'data': [{'id': 'fakeid1'}, {'id': 'fakeid2'}]})
        objs = self.manager._list('/fakes', 'data', body='fakebody')
        expected = [mock.call(self.manager, {'id': 'fakeid1'}, loaded=True),
                    mock.call(self.manager, {'id': 'fakeid2'}, loaded=True)]
        self.assertTrue(self.client.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.client.json_request.mock_calls,
                         [mock.call('GET', '/fakes', body='fakebody')])
        self.assertEqual(self.resource.mock_calls, expected)

    def test_delete(self):
        self.manager._delete('/fakes')
        self.assertTrue(self.client.raw_request.called)
        self.assertEqual(self.client.raw_request.mock_calls,
                         [mock.call('DELETE', '/fakes')])

    def test_update(self):
        self.client.json_request.return_value = \
            (mock.Mock(), {'data': {'id': 'fakeid'}})
        body = {'data': {'id': 'fakeid',
                         'name': 'fakename'}}
        obj = self.manager._update('/fakes', body, response_key='data')
        self.assertTrue(self.client.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.client.json_request.mock_calls,
                         [mock.call('PUT', '/fakes', body=body)])
        self.assertEqual(self.resource.mock_calls,
                         [mock.call(self.manager, {'id': 'fakeid'})])

    def test_create(self):
        self.client.json_request.return_value = \
            (mock.Mock(), {'data': {'id': 'fakeid'}})
        body = {'data': {'id': 'fakeid',
                         'name': 'fakename'}}
        obj = self.manager._create('/fakes', body, 'data')
        self.assertTrue(self.client.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.client.json_request.mock_calls,
                         [mock.call('POST', '/fakes', body=body)])
        self.assertEqual(self.resource.mock_calls,
                         [mock.call(self.manager, {'id': 'fakeid'})])

    def test_create_raw(self):
        self.client.json_request.return_value = \
            (mock.Mock(), {'data': {'id': 'fakeid'}})
        body = {'data': {'id': 'fakeid',
                         'name': 'fakename'}}
        obj = self.manager._create('/fakes', body, 'data', return_raw=True)
        self.assertTrue(self.client.json_request.called)
        self.assertFalse(self.resource.called)
        self.assertEqual(self.client.json_request.mock_calls,
                         [mock.call('POST', '/fakes', body=body)])
        self.assertEqual(obj, {'id': 'fakeid'})

    def test_get(self):
        self.client.json_request.return_value = \
            (mock.Mock(), {'data': {'id': 'fakeid'}})
        obj = self.manager._get('/fakes', 'data')
        self.assertTrue(self.client.json_request.called)
        self.assertTrue(self.resource.called)
        self.assertEqual(self.client.json_request.mock_calls,
                         [mock.call('GET', '/fakes')])


class TestResource(unittest2.TestCase):
    def test_getattr_loaded(self):
        manager = MockWithoutAttrs(exclude_attrs=('get',))
        res = base.Resource(manager, {'id': 'fakeid', 'name': 'fakename'},
                            loaded=True)
        self.assertTrue(hasattr(res, 'id'))
        self.assertTrue(hasattr(res, 'name'))
        self.assertEqual(res.id, 'fakeid')
        self.assertEqual(res.name, 'fakename')

    def test_getattr_loaded_attr_error(self):
        manager = MockWithoutAttrs(exclude_attrs=('get',))
        res = base.Resource(manager, {'id': 'fakeid'}, loaded=True)
        with self.assertRaises(AttributeError) as cm:
            value = res.name
        self.assertEqual(cm.exception.args, ('name',))

    def test_getattr_unloaded_get(self):
        manager = mock.Mock()
        manager.get.return_value = mock.Mock(_info={'id': 'fakeid',
                                                    'name': 'fakename'})
        res = base.Resource(manager, {'id': 'fakeid'})
        res.get()
        self.assertTrue(manager.get.called)
        self.assertEqual(manager.get.mock_calls, [mock.call('fakeid')])
        self.assertTrue(hasattr(res, 'name'))
        self.assertEqual(res.name, 'fakename')

    def test_getattr_unloaded_getattr(self):
        manager = mock.Mock()
        manager.get.return_value = mock.Mock(_info={'id': 'fakeid',
                                                    'name': 'fakename'})
        res = base.Resource(manager, {'id': 'fakeid'})
        name = res.name
        self.assertTrue(manager.get.called)
        self.assertEqual(manager.get.mock_calls, [mock.call('fakeid')])
        self.assertEqual(name, 'fakename')

    def test_get_unloaded(self):
        manager = MockWithoutAttrs(exclude_attrs=('get',))
        res = base.Resource(manager, {'id': 'fakeid'})
        with self.assertRaises(AttributeError) as cm:
            name = res.name
        self.assertEqual(cm.exception.args, ('name',))

    def test_eq_by_id(self):
        manager = mock.Mock()
        res1 = base.Resource(manager, {'id': 'fakeid'}, loaded=True)
        res2 = base.Resource(manager, {'id': 'fakeid'}, loaded=True)
        self.assertTrue(res1 == res2)

    def test_not_eq_by_id(self):
        manager = mock.Mock()
        res1 = base.Resource(manager, {'id': 'fakeid1'}, loaded=True)
        res2 = base.Resource(manager, {'id': 'fakeid2'}, loaded=True)
        self.assertFalse(res1 == res2)

    def test_not_eq_by_isinstance(self):
        manager = mock.Mock()
        res1 = base.Resource(manager, {'id': 'fakeid'}, loaded=True)
        res2 = mock.Mock()
        self.assertFalse(res1 == res2)

    def test_eq_by_info(self):
        manager = mock.Mock()
        res1 = base.Resource(manager, {'name': 'fakename'}, loaded=True)
        res2 = base.Resource(manager, {'name': 'fakename'}, loaded=True)
        self.assertTrue(res1 == res2)

    def test_not_eq_by_info(self):
        manager = mock.Mock()
        res1 = base.Resource(manager, {'name': 'fakename1'}, loaded=True)
        res2 = base.Resource(manager, {'name': 'fakename2'}, loaded=True)
        self.assertFalse(res1 == res2)
