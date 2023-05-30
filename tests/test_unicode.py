# coding=utf-8
"""
Various unicode handling related tests.

"""
from utils import http, HTTP_OK
from fixtures import UNICODE


class TestUnicode:

    def test_unicode_headers(self, httpbin):
        # httpbin doesn't interpret utf8 headers
        r = http(f'{httpbin.url}/headers', f'Test:{UNICODE}')
        assert HTTP_OK in r

    def test_unicode_headers_verbose(self, httpbin):
        # httpbin doesn't interpret utf8 headers
        r = http('--verbose', f'{httpbin.url}/headers', f'Test:{UNICODE}')
        assert HTTP_OK in r
        assert UNICODE in r

    def test_unicode_form_item(self, httpbin):
        r = http('--form', 'POST', f'{httpbin.url}/post', f'test={UNICODE}')
        assert HTTP_OK in r
        assert r.json['form'] == {'test': UNICODE}

    def test_unicode_form_item_verbose(self, httpbin):
        r = http(
            '--verbose', '--form', 'POST', f'{httpbin.url}/post', f'test={UNICODE}'
        )
        assert HTTP_OK in r
        assert UNICODE in r

    def test_unicode_json_item(self, httpbin):
        r = http('--json', 'POST', f'{httpbin.url}/post', f'test={UNICODE}')
        assert HTTP_OK in r
        assert r.json['json'] == {'test': UNICODE}

    def test_unicode_json_item_verbose(self, httpbin):
        r = http(
            '--verbose', '--json', 'POST', f'{httpbin.url}/post', f'test={UNICODE}'
        )
        assert HTTP_OK in r
        assert UNICODE in r

    def test_unicode_raw_json_item(self, httpbin):
        r = http(
            '--json',
            'POST',
            f'{httpbin.url}/post',
            u'test:={ "%s" : [ "%s" ] }' % (UNICODE, UNICODE),
        )
        assert HTTP_OK in r
        assert r.json['json'] == {'test': {UNICODE: [UNICODE]}}

    def test_unicode_raw_json_item_verbose(self, httpbin):
        r = http(
            '--json',
            'POST',
            f'{httpbin.url}/post',
            u'test:={ "%s" : [ "%s" ] }' % (UNICODE, UNICODE),
        )
        assert HTTP_OK in r
        assert r.json['json'] == {'test': {UNICODE: [UNICODE]}}

    def test_unicode_url_query_arg_item(self, httpbin):
        r = http(f'{httpbin.url}/get', f'test=={UNICODE}')
        assert HTTP_OK in r
        assert r.json['args'] == {'test': UNICODE}, r

    def test_unicode_url_query_arg_item_verbose(self, httpbin):
        r = http('--verbose', f'{httpbin.url}/get', f'test=={UNICODE}')
        assert HTTP_OK in r
        assert UNICODE in r

    def test_unicode_url(self, httpbin):
        r = http(f'{httpbin.url}/get?test={UNICODE}')
        assert HTTP_OK in r
        assert r.json['args'] == {'test': UNICODE}

    # def test_unicode_url_verbose(self):
    #     r = http(httpbin.url + '--verbose', u'/get?test=' + UNICODE)
    #     assert HTTP_OK in r

    def test_unicode_basic_auth(self, httpbin):
        # it doesn't really authenticate us because httpbin
        # doesn't interpret the utf8-encoded auth
        http(
            '--verbose',
            '--auth',
            f'test:{UNICODE}',
            f'{httpbin.url}/basic-auth/test/{UNICODE}',
        )

    def test_unicode_digest_auth(self, httpbin):
        # it doesn't really authenticate us because httpbin
        # doesn't interpret the utf8-encoded auth
        http(
            '--auth-type=digest',
            '--auth',
            f'test:{UNICODE}',
            f'{httpbin.url}/digest-auth/auth/test/{UNICODE}',
        )
