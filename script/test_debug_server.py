import time

from test.util.server import server

def main(**kwargs):
    server.start()
    time.sleep(3)
    server.stop()
