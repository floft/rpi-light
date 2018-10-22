#!/usr/bin/env python3
"""
Turn on/off lights via setting serial port high/low
"""
import sys
import json
import yaml
import time
import serial
import logging
import argparse
import tornado.web
import tornado.gen
import tornado.ioloop
import tornado.template
import tornado.httpserver

class Lights:
    """
    Turn on/off lights via serial

    Usage:
        s = Serial("/dev/ttyUSB0")
        s.on()
        time.sleep(3)
        s.off()
    """
    def __init__(self, port, **kwargs):
        self.state = False # Off to start with
        self.port = port
        self.serial = serial.Serial(port, **kwargs)

    def update(self):
        """ Update to whatever the internal state is set to """
        self.serial.setRTS(self.state)

    def on(self):
        self.state = True
        self.update()

    def off(self):
        self.state = False
        self.update()

    def toggle(self):
        self.state = not self.state
        self.update()
        return self.state

def demo_toggle(serial_port="/dev/ttyUSB0", seconds=3):
    """ Demo lights by toggling on/off every so many seconds """
    l = Lights(serial_port)

    while True:
        print("Lights on")
        l.on()
        time.sleep(seconds)
        print("Lights off")
        l.off()
        time.sleep(seconds)

class BaseHandler(tornado.web.RequestHandler):
    """ Inherit from this for all pages, so we'll have access to these """
    @property
    def config(self):
        return self.application.config

    @property
    def lights(self):
        return self.application.lights

class MainHandler(BaseHandler):
    def get(self):
        self.write("""
<html>
<head><title>rpi-lights</title></head>
<body>
<h1>rpi-lights</h1>
<p>This is a <a href="https://github.com/floft/rpi-lights">rpi-lights</a> server.</p>
</body>
</html>""")

class WebHookHandler(BaseHandler):
    """ On/off hook -- password protected via the key """
    def get(self):
        key = self.get_argument("key", "")
        action = self.get_argument("action", "")

        if key == config["key"]:
            self.write("Correct")

            if action == "on":
                self.lights.on()
                self.write(json.dumps({"result": "on"}))
            elif action == "off":
                self.lights.off()
                self.write(json.dumps({"result": "off"}))
            elif action == "toggle":
                result = self.lights.toggle()
                bool_str = {
                    False: "off",
                    True: "on",
                }
                self.write(json.dumps({"result": bool_str[result]}))
            else:
                self.write(json.dumps({"error": "invalid-action"}))
        else:
            self.write(json.dumps({"error": "invalid-key"}))

class Application(tornado.web.Application):
    """
    Main Tornado web app that handles what directories point to what functions
    """
    def __init__(self, config, lights):
        self.config = config
        self.lights = lights
        handlers = [
            (config["root"], MainHandler),
            (config["root"]+"/", MainHandler),
            (config["root"]+"/hook", WebHookHandler),
        ]
        settings = dict(
            debug=config["debug"]
        )
        super(Application, self).__init__(handlers, **settings)

def run_tornado(config, lights):
    """ Start HTTP server """
    http_server = tornado.httpserver.HTTPServer(Application(config, lights))
    http_server.listen(config["port"])
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    # Command-line options
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="", type=str,
        help="Which config file to use (required)")
    parser.add_argument("--debug", dest="debug", action="store_true",
        help="Enable debug mode")
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    # Get config and make sure required options are there
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f)
    except IOError:
        print("Could not open config file:", args.config)
        sys.exit(1)

    for s in ["root", "port", "serial", "key"]:
        assert s in config, "Must define "+s+" in config"

    # Set additional config options from the command line options
    config["debug"] = args.debug

    # Manage turning lights on and off
    lights = Lights(config["serial"])

    # Start the webserver
    run_tornado(config, lights)
