from http.server import HTTPServer, BaseHTTPRequestHandler
import hashlib
import logging

_LOGGER = logging.getLogger(__name__)


class UpdateServer(BaseHTTPRequestHandler):
    """A simplified handler just returning the contents of a single file."""
    def __init__(self, request, client_address, server):
        self.payload = server.payload
        self.server = server

        super().__init__(request, client_address, server)

    def handle_one_request(self):
        self.server.got_request = True
        self.raw_requestline = self.rfile.readline()

        if not self.parse_request():
            print("unable to parse request")
            return

        print("got %s for %s" % (self.command, self.path))

        self.send_response(200)
        self.send_header('Content-type', 'application/octet-stream')
        self.end_headers()
        self.wfile.write(self.payload)


class Updater:
    """A simple HTTP server for serving an update file.

    The server will be started in an emphemeral port, and will only accept
    a single request to keep it simple."""
    def __init__(self, file, interface=None):
        addr = ('', 0)
        self.server = HTTPServer(addr, UpdateServer)
        self.server.got_request = False
        _, self.port = self.server.server_address
        _LOGGER.info("Serving on port %s" % self.port)
        self.server.timeout = 10

        with open(file, 'rb') as f:
            self.payload = f.read()
            self.server.payload = self.payload
            self.md5 = hashlib.md5(self.payload).hexdigest()
            _LOGGER.info("Using local %s (md5: %s)" % (file, self.md5))

    def serve_once(self):
        self.server.handle_request()
        if self.server.got_request:
            _LOGGER.info("Got a request, serving the file hopefully")
        else:
            _LOGGER.error("No request was made..")
            return


if __name__ == "__main__":
    import netifaces
    ifaces_without_lo = [x for x in netifaces.interfaces() if not x.startswith("lo")]
    # print(ifaces_without_lo)
    logging.basicConfig(level=logging.DEBUG)
    upd = Updater("/tmp/test")
    upd.serve_once()
