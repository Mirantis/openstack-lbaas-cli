import httplib2
import mock

from .utils import unittest

from balancerclient.common import client
from balancerclient.common import exceptions


fake_response = httplib2.Response({"status": 200})
fake_body = '{"hi": "there"}'


def get_client():
    cl = client.HTTPClient(username="username", password="password",
                           tenant_name="project_name", auth_url="auth_test")
    return cl


def get_authed_client():
    cl = get_client()
    cl.endpoint_url = 'http://example.com'
    cl.auth_token = 'token'
    return cl


class ClientTest(unittest.TestCase):

    @mock.patch('httplib2.Http.request')
    @mock.patch('time.time')
    def test_get(self, mock_time, mock_request):
        mock_time.return_value = 1234
        mock_request.return_value = (fake_response, fake_body)
        cl = get_authed_client()
        resp, body = cl.do_request('/hi', 'GET')
        headers = {'X-Auth-Token': 'token',
                   'User-Agent': cl.USER_AGENT,
                   'Accept': 'application/json',
                   'Content-Type': 'application/json',
        }
        self.assertEqual(mock_request.call_args,
                         mock.call('http://example.com/hi', 'GET',
                                   headers=headers))

    @mock.patch('httplib2.Http.request')
    def test_auth_failure(self, mock_request):
        mock_request.return_value = (fake_response, fake_body)
        cl = get_client()
        self.assertRaises(exceptions.AuthorizationFailure, cl.authenticate)
