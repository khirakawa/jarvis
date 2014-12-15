import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os
try:
    from jarvis.bt import bt as bt
except:
    print "Warning: This isn't a linux box.  Importing btdev instead."
    from jarvis.bt import btdev as bt
from jarvis.keyboard import keyboard

if not os.geteuid() == 0:
    sys.exit("Only root can run this script")

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

handler = keyboard.Keyboard()
bluetooth = bt.Bluetooth(handler);

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message("connected")

    def on_message(self, message):
        bluetooth.send(message)
        self.write_message('handled message: %s' % message)

    def on_close(self):
        print 'connection closed'

if __name__ == "__main__":

    # Start bluetooth
    bluetooth.listen();

    # Start websocket server
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print "Listening on port:", options.port
    tornado.ioloop.IOLoop.instance().start()
