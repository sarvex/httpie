import json
import sys
from pprint import pformat

import requests
from requests.packages import urllib3

from httpie import sessions
from httpie import __version__
from httpie.compat import str
from httpie.plugins import plugin_manager


# https://urllib3.readthedocs.org/en/latest/security.html
urllib3.disable_warnings()


FORM = 'application/x-www-form-urlencoded; charset=utf-8'
JSON = 'application/json'
DEFAULT_UA = f'HTTPie/{__version__}'


def get_requests_session():
    requests_session = requests.Session()
    for cls in plugin_manager.get_trasnsport_plugins():
        transport_plugin = cls()
        requests_session.mount(prefix=transport_plugin.prefix,
                               adapter=transport_plugin.get_adapter())
    return requests_session


def get_response(args, config_dir):
    """Send the request and return a `request.Response`."""

    requests_session = get_requests_session()

    if args.session or args.session_read_only:
        return sessions.get_response(
            requests_session=requests_session,
            args=args,
            config_dir=config_dir,
            session_name=args.session or args.session_read_only,
            read_only=bool(args.session_read_only),
        )

    kwargs = get_requests_kwargs(args)
    if args.debug:
        dump_request(kwargs)
    return requests_session.request(**kwargs)


def dump_request(kwargs):
    sys.stderr.write('\n>>> requests.request(**%s)\n\n'
                     % pformat(kwargs))


def encode_headers(headers):
    # This allows for unicode headers which is non-standard but practical.
    # See: https://github.com/jakubroztocil/httpie/issues/212
    return {
        name: value.encode('utf8') if isinstance(value, str) else value
        for name, value in headers.items()
    }


def get_default_headers(args):
    default_headers = {
        'User-Agent': DEFAULT_UA
    }

    auto_json = args.data and not args.form
    # FIXME: Accept is set to JSON with `http url @./file.txt`.
    if args.json or auto_json:
        default_headers['Accept'] = 'application/json'
        if args.json or (auto_json and args.data):
            default_headers['Content-Type'] = JSON

    elif args.form and not args.files:
        # If sending files, `requests` will set
        # the `Content-Type` for us.
        default_headers['Content-Type'] = FORM
    return default_headers


def get_requests_kwargs(args, base_headers=None):
    """
    Translate our `args` into `requests.request` keyword arguments.

    """
    # Serialize JSON data, if needed.
    data = args.data
    auto_json = data and not args.form
    if args.json or auto_json and isinstance(data, dict):
        data = json.dumps(data) if data else ''
    # Finalize headers.
    headers = get_default_headers(args)
    if base_headers:
        headers.update(base_headers)
    headers.update(args.headers)
    headers = encode_headers(headers)

    credentials = None
    if args.auth:
        auth_plugin = plugin_manager.get_auth_plugin(args.auth_type)()
        credentials = auth_plugin.get_auth(args.auth.key, args.auth.value)

    cert = None
    if args.cert:
        cert = args.cert
        if args.cert_key:
            cert = cert, args.cert_key

    return {
        'stream': True,
        'method': args.method.lower(),
        'url': args.url,
        'headers': headers,
        'data': data,
        'verify': {'yes': True, 'no': False}.get(args.verify, args.verify),
        'cert': cert,
        'timeout': args.timeout,
        'auth': credentials,
        'proxies': {p.key: p.value for p in args.proxy},
        'files': args.files,
        'allow_redirects': args.follow,
        'params': args.params,
    }
