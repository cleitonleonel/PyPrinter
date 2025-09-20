from flask import Flask
from pyprinter.routes.printer_routes import printer_app

app = Flask(__name__, static_folder="static", template_folder="pyprinter/templates")
app.register_blueprint(printer_app)
