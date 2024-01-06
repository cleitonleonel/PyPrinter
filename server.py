#!/usr/bin/python
#  -*- coding: utf-8 -*-
from flask import Flask
from routes.printer_routes import printer_app

app = Flask(__name__)
app.register_blueprint(printer_app)

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
