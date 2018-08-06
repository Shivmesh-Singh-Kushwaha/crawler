from io import BytesIO

import pycurl

from .response import Response
from .error import NetworkError


class CurlTransport(object):
    def process_request(self, req):
        data = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, req.url)
            curl.setopt(pycurl.WRITEDATA, data)
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
