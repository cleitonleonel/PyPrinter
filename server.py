from flask import Flask
from pyprinter.routes.printer_routes import printer_app

app = Flask(__name__)
app.register_blueprint(printer_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
