from pyprinter.routes.printer_routes import printer_app
from flask import Flask, render_template
from flask_cors import CORS
import threading
import webview

HOST = "0.0.0.0"
PORT = 8000


def start_server():
    app = Flask(__name__)
    app.register_blueprint(printer_app)

    CORS(app)

    @app.route('/')
    def home():
        return render_template("index.html")

    app.run(
        host=HOST,
        port=PORT,
        debug=True,
        use_reloader=False
    )


def main():
    flask_thread = threading.Thread(
        target=start_server,
        daemon=True
    )
    flask_thread.daemon = True
    flask_thread.start()

    webview.settings["ALLOW_DOWNLOADS"] = True
    webview.create_window(
        "PyPrinter",
        url=f"http://127.0.0.1:{PORT}",
        width=650,
        height=750
    )
    webview.start()
