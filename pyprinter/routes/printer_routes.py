import os
import io
import signal
from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
    render_template
)
from xml.etree import ElementTree
from pyprinter.controllers.coupon_controller import DanfcePrinter
from pyprinter.controllers.conversor_controller import make_dict

printer_app = Blueprint('printer_app', __name__)
version = "0.0.1"


def stop_server():
    try:
        os.kill(os.getpid(), signal.SIGINT)
    except Exception as e:
        print(f"Erro ao parar o servidor: {str(e)}")


def validate_xml(xml_content):
    try:
        ElementTree.fromstring(xml_content)
        return True
    except ElementTree.ParseError:
        return False


def prepare_content():
    request_file = request.files.get('file')
    logo = request.form.get('logo')
    if request_file and request_file.filename.endswith(".xml"):
        content = request_file.stream.read().decode()
        data = {
            "xml_content": content,
            "logo": logo
        }
    else:
        data = request.get_json()
    if data.get("xml_content"):
        if not validate_xml(data.get("xml_content")):
            return {
                "error": True,
                "message": "Invalid XML format"
            }

        return make_dict(
            content=data.get("xml_content"),
            logo=data.get("logo"),
        )

    return data


@printer_app.route("/", methods=['GET'])
def home():
    return render_template("home.html")

@printer_app.route("/api/v1/status", methods=['GET'])
def status():
    return jsonify(message="ok", version=version)

@printer_app.route('/stop', methods=['GET'])
def stop():
    stop_server()
    return jsonify(
        {'status': 'stopped'}
    )


@printer_app.route("/api/v1/geradanfce", methods=['POST'])
def danfce_generator():
    try:
        printer = DanfcePrinter()
        printer.initialize(dummy=True)
    except Exception as e:
        return jsonify(
            {"error": True, "message": e}
        ), 500
    content = prepare_content()
    if content.get("error"):
        return jsonify(content), 500

    document, message = printer.print_document(content)
    if not document:
        return jsonify(
            {"error": True, "message": message}
        ), 500
    return send_file(
        io.BytesIO(document),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='output_escpos.bin'
    )
