from flask import Flask
from pyprinter.routes.printer_routes import printer_app

app = Flask(__name__)
app.register_blueprint(printer_app)


def main():
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
