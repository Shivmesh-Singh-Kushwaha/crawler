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
            # dns timeouts will not be processed in default name resolver
            # needs to use cares resolver
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
            curl.perform()
        except pycurl.error as ex:
            raise NetworkError(str(ex), ex)
        else:
            resp = Response(
                url=req.url,
                body=data.getvalue(),
            )
            return resp
        finally:
            curl.close()
