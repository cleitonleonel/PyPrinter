#!/usr/bin/python
#  -*- coding: utf-8 -*-
import io
from flask import (Blueprint,
                   jsonify,
                   request,
                   send_file)
from xml.etree import ElementTree
from controllers.coupon_controller import DanfcePrinter
from controllers.conversor_controller import make_dict

printer_app = Blueprint('printer_app', __name__)
version = "0.0.1"


def validate_xml(xml_content):
    try:
        ElementTree.fromstring(xml_content)
        return True
    except ElementTree.ParseError:
        return False


@printer_app.route("/", methods=['GET'])
def index():
    return jsonify(message="ok", version=version)


@printer_app.route("/geradanfce", methods=['POST'])
def danfce_generator():
    try:
        request_file = request.files.get('file')
        if request_file and ".xml" in request_file.filename:
            content = request_file.stream.read().decode()
            data = {"xml_content": content}
        else:
            data = request.get_json()
        if data.get("xml_content"):
            if not validate_xml(data.get("xml_content")):
                return jsonify({"error": True, "message": "Invalid XML format"})
            data = make_dict(content=data.get("xml_content"))
        printer = DanfcePrinter()
        printer.initialize(dummy=True)
    except Exception as e:
        return jsonify({"error": True, "message": e})
    document, message = printer.print_document(data)
    if not document:
        return jsonify({"error": True, "message": message})
    return send_file(
        io.BytesIO(document),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='output_escpos.bin'
    )
