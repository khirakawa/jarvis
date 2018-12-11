import sys
sys.path.append('/home/pi/.local/lib/python2.7/site-packages')

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os
import keymap
import sys
import json
from kb_client import *

if not os.geteuid() == 0:
    sys.exit("Only root can run this script")

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

kb = Keyboard()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message("connected")

    def on_message(self, message):
        self.send(message)
        self.write_message('handled message: %s' % message)

    def on_close(self):
        print 'connection closed'

    def send(self, message):
      parsedJson = json.loads(message)
      report = self.getReport(parsedJson)
      if report:
        kb.send_input_direct(report)

    def getReport(self, json):
      # The structure for an bt keyboard input report (size is 10 bytes)
      report = [
          0xA1, # This is an input report
          0x01, # Report ID
          # Bit array for Modifier keys
          [0,   # Right GUI - (usually the Windows key)
            0,   # Right ALT
            0,   # Right Shift
            0,   # Right Control
            0,   # Left GUI - (again, usually the Windows key)
            0,   # Left ALT
            0,   # Left Shift
            0],   # Left Control
          0x00,  # Vendor reserved
          0x00,  # Rest is space for 6 keys
          0x00,
          0x00,
          0x00,
          0x00,
          0x00 ]

      # Expects json to be in the form of {"pressedKeys": ["KEY_LEFTSHIFT", "KEY_A"]}
      if 'pressedKeys' not in json.keys():
        return

      pressedKeys = json['pressedKeys']
      startIndexForKeys = 4

      for pressedKey in pressedKeys:
        modkey_element = keymap.modkey(pressedKey)
        if modkey_element > 0:
            report[2][modkey_element] = 1
        else:
          # Get the hex keycode of the key
          hex_key = keymap.convert(pressedKey)
          report[startIndexForKeys] = hex_key
          startIndexForKeys += 1
      return report


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
