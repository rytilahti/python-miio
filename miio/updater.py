import hashlib
import logging
import netifaces
from http.server import HTTPServer, BaseHTTPRequestHandler
from os.path import basename

_LOGGER = logging.getLogger(__name__)


class SingleFileHandler(BaseHTTPRequestHandler):
    """A simplified handler just returning the contents of a buffer."""
    def __init__(self, request, client_address, server):
        self.payload = server.payload
        self.server = server

        super().__init__(request, client_address, server)

    def handle_one_request(self):
        self.server.got_request = True
        self.raw_requestline = self.rfile.readline()

        if not self.parse_request():
            _LOGGER.error("unable to parse request: %s" % self.raw_requestline)
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Length', len(self.payload))
        self.end_headers()
        self.wfile.write(self.payload)


class OneShotServer:
    """A simple HTTP server for serving an update file.

    The server will be started in an emphemeral port, and will only accept
    a single request to keep it simple."""
    def __init__(self, file, interface=None):
        addr = ('', 0)
        self.server = HTTPServer(addr, SingleFileHandler)
        setattr(self.server, "got_request", False)

        self.addr, self.port = self.server.server_address
        self.server.timeout = 10

        _LOGGER.info("Serving on %s:%s, timeout %s" % (self.addr, self.port,
                                                       self.server.timeout))

        self.file = basename(file)
        with open(file, 'rb') as f:
            self.payload = f.read()
            self.server.payload = self.payload
            self.md5 = hashlib.md5(self.payload).hexdigest()
            _LOGGER.info("Using local %s (md5: %s)" % (file, self.md5))

    @staticmethod
    def find_local_ip():
        ifaces_without_lo = [x for x in netifaces.interfaces()
                             if not x.startswith("lo")]
        _LOGGER.debug("available interfaces: %s" % ifaces_without_lo)

        for iface in ifaces_without_lo:
            addresses = netifaces.ifaddresses(iface)
            if netifaces.AF_INET not in addresses:
                _LOGGER.debug("%s has no ipv4 addresses, skipping" % iface)
                continue
            for entry in addresses[netifaces.AF_INET]:
                _LOGGER.debug("Got addr: %s" % entry['addr'])
                return entry['addr']

    def url(self, ip=None):
        if ip is None:
            ip = OneShotServer.find_local_ip()

        url = "http://%s:%s/%s" % (ip, self.port, self.file)
        return url

    def serve_once(self):
        self.server.handle_request()
        if getattr(self.server, "got_request"):
            _LOGGER.info("Got a request, should be downloading now.")
            return True
        else:
            _LOGGER.error("No request was made..")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    upd = OneShotServer("/tmp/test")
    upd.serve_once()
