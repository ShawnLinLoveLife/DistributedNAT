"""
This is the server to run the wsgi app. It's inplemented by gevent.wsgiserver.
"""

import os
import sys

from gevent import monkey
from gevent.wsgi import WSGIHandler
from gevent.wsgi import WSGIServer

import webapp
from config import get_config
from daemon import Daemon


class DaemonImpl(Daemon):
    """ Inherit class Daemon and implement our own run() method """

    def __init__(self):
        cur_path = os.path.dirname(os.path.abspath(__file__))
        self.app = webapp.create_app()
        self.app.debug = True
        self.port = get_config().getint("setup", "listen_port")
        self.pidfile = os.path.join(cur_path, '..', get_config().get("setup", "pidpath"))
        Daemon.__init__(self, self.pidfile)

    def run(self):
        """ Implement the run method """
        monkey.patch_all()
        self.app.debug=True
        http_server = WSGIServer(('', self.port), self.app, handler_class=WSGIHandler)
        http_server.serve_forever()


if __name__ == '__main__':
    daemon = DaemonImpl()
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    elif len(sys.argv) == 1:
        daemon.run()
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
