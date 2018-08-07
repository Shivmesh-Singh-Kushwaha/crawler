from io import BytesIO

import pycurl

from .response import Response
from .error import NetworkError


class CurlTransport(object):
    def process_request(self, req):
        data = BytesIO()
        curl = pycurl.Curl()
        try:
            # Do not use signals for timeouts
            # (!) DNS timeouts will not be processed by default name resolver
            # Need to use cares resolver
            curl.setopt(pycurl.NOSIGNAL, 1)
            # Basic settings
            curl.setopt(pycurl.URL, req.url)
            # Data processing
            curl.setopt(pycurl.WRITEDATA, data)
            # Force connections close
            curl.setopt(pycurl.FORBID_REUSE, 1)
            curl.setopt(pycurl.FRESH_CONNECT, 1)
            # Timeouts
            curl.setopt(pycurl.TIMEOUT_MS, int(1000 * req.timeout))
            curl.setopt(
                pycurl.CONNECTTIMEOUT_MS, int(1000 * req.connect_timeout)
            )
            # Proxy
            if req.proxy:
                curl.setopt(pycurl.PROXY, grab.config['proxy'])
            if req.proxy_auth:
                curl.setopt(pycurl.PROXYUSERPWD, req.proxy_auth)
            key = 'PROXYTYPE_%s' % (req.proxy_type or 'http').upper()
            curl.setopt(pycurl.PROXYTYPE, getattr(pycurl, key))
            # Make request
            curl.perform()
        except pycurl.error as ex:
            raise NetworkError(str(ex), ex)
        else:
            resp = Response(
                code=curl.getinfo(pycurl.HTTP_CODE),
                url=req.url,
                body=data.getvalue(),
                effective_url=curl.getinfo(pycurl.EFFECTIVE_URL),
                bytes_downloaded=curl.getinfo(pycurl.SIZE_DOWNLOAD),
                bytes_uploaded=curl.getinfo(pycurl.SIZE_UPLOAD),
                times={
                    'name_lookup': curl.getinfo(pycurl.NAMELOOKUP_TIME),
                    'connect': curl.getinfo(pycurl.CONNECT_TIME),
                    'total': curl.getinfo(pycurl.TOTAL_TIME),
                },
            )
            return resp
        finally:
            curl.close()
