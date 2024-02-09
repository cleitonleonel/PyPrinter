#!/usr/bin/python
#  -*- coding: utf-8 -*-
from controllers.text_controller import (line_break,
                                         format_cpf_cnpj)
from controllers.image_controller import ImageController
from escpos.printer import Usb, Dummy

img_controller = ImageController()


class DanfcePrinter(object):

    def __init__(self,
                 vendor_id=0x0416,
                 product_id=0x5011,
                 initpoint=0x81,
                 endpoint=0x03):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.initpoint = initpoint
        self.endpoint = endpoint
        self.printer = None

    def initialize(self, dummy=False):

        if dummy:
            self.printer = Dummy(devfile="document.txt", autocut=True)
        else:
            self.printer = Usb(self.vendor_id,
                               self.product_id,
                               in_ep=self.initpoint,
                               out_ep=self.endpoint,
                               profile="POS80")
        self.printer.profile.profile_data["media"]["width"]["mm"] = 80
        self.printer.profile.profile_data["media"]["width"]["pixels"] = 640
        self.printer.profile.profile_data["media"]["dpi"] = 203
        self.printer.charcode('CP850')

    def print_line_separator(self, text="-", size_line=48):
        line = text * size_line
        self.printer.set(bold=True, font="a")
        self.printer.text(line + "\n")

    def print_header_logo(self, img_source, text_header):
        header_img = img_controller.generate_header(text_header, img_source,
                                                    "draw_logo.jpeg")
        self.printer.image(header_img.convert('L'))

    def print_title_document(self):
        self.print_line_separator(text="=")
        self.printer.set(bold=True, align='center', font="b")
        self.printer.line_spacing(spacing=1)
        self.printer.text("DANFE NFC-e - DOCUMENTO AUXILIO DA NOTA\n")
        self.printer.line_spacing(spacing=1)
        self.printer.text("FISCAL DE CONSUMIDOR ELETRONICA\n")

    def print_header_document(self):
        self.print_line_separator(text="=")
        self.printer.set(bold=True, font="b")
        header = (f"{'Codigo':<6} {'Descricao dos produtos':<26} "
                  f"{'Quantidade':>14} {'Preco':>7} {'Total':>7}")
        self.printer.text(header + "\n")
        self.printer.line_spacing(spacing=1)

    def print_payments(self, data):
        self.print_line_separator()
        self.printer.text("Forma De Pagamento                          Pago\n")
        self.printer.set(bold=True, align='left', font="b")
        self.printer.line_spacing(spacing=1)
        self.printer.set(bold=False)
        for row in data["payments"]:
            formatted_row = f"{row[0]:<40} {row[1]:>23}"
            self.printer.text(f"{formatted_row}\n")

    def print_url_document(self, data):
        self.print_line_separator()
        self.printer.set(bold=False, align='center', font="b")
        self.printer.line_spacing(spacing=1)
        self.printer.text(data["text_url_sefaz"])

    def print_type_document(self, consumer, ambient, emission):
        self.print_line_separator()
        self.printer.set(bold=True, align='center', font="a")
        self.printer.line_spacing(spacing=1)
        ambient_info, address_text = ("", "")
        document = (consumer.get("CPF") or
                    consumer.get("CNPJ", ""))
        name = consumer.get("xNome")
        address_consumer = consumer.get("enderDest", {})
        street = address_consumer.get("xLgr")
        number = address_consumer.get("nro")
        neighborhood = address_consumer.get("xBairro")
        city = address_consumer.get("xMun")
        self.printer.text(f'CONSUMIDOR {format_cpf_cnpj(document)}\n')
        self.printer.set(bold=False, align='center', font="b")
        if all([name, street, number, neighborhood, city]):
            self.printer.text(f"{line_break(name.replace(' - ', ' '), limit=40)}\n")
            address_text = (f"{street}, {number} "
                            f"{neighborhood} - {city}\n")
        if ambient.upper() != "PRODUCAO":
            ambient_complement = "AMBIENTE DE" if ambient.upper() == "HOMOLOGACAO" else ""
            ambient_info = f'NFC-E EMITIDA EM {ambient_complement} {ambient.upper()}\n'
        if emission.upper() == "CONTINGENCIA":
            self.printer.set(bold=True, align='center', font="a")
            self.printer.text("\nEMITIDA EM CONTINGENCIA\n")
            self.printer.text("Pendente de Autorizacao\n")
        self.printer.text(address_text)
        self.printer.set(bold=True, align='center', font="a")
        self.printer.line_spacing(spacing=1)
        self.printer.text("\n" + ambient_info)

    def print_qrcode(self, fiscal, qr_url):
        qr_img_container = img_controller.qrcode_adjust(fiscal,
                                                        qr_data=qr_url)
        self.print_line_separator()
        self.printer.set(align='center')
        self.printer.image(qr_img_container.convert('L'),
                           impl='bitImageColumn',
                           center=True)

    def print_complements(self, data):
        self.print_line_separator()
        self.printer.set(bold=False, align='center', font="b")
        self.printer.control("B")
        self.printer.line_spacing(spacing=1)
        self.printer.text(data["complements"])

    def print_message(self, data):
        self.print_line_separator()
        self.printer.set(bold=False, align='center', font="b")
        self.printer.line_spacing(spacing=1)
        message = data["message"]
        lines = "\n".join([message[i:i + 60] for i in range(0, len(message), 60)])
        self.printer.text(lines)

    def print_produtcs(self, products):
        for product in products:
            result_str = ""
            code, description, quantity, price, total = product
            self.printer.set(bold=False, font="b")
            self.printer.line_spacing(spacing=1)
            if len(description) > 30:
                broken_description = line_break(description, 31).split("\n")
                first_line = f"{code:<6} {broken_description[0]:<31} {quantity:>9} {price:>7} {total:>7}"
                result_str += first_line
                for index, line in enumerate(broken_description[1:]):
                    if index > 0:
                        result_str += '\n'
                    max_length = 56 if len(line) > 20 else 31
                    result_str += f"{'':>6} {line:<{max_length}}"
            else:
                result_str = f"{code:<6} {description:<31} {quantity:>9} {price:>7} {total:>7}"
            self.printer.text(result_str + "\n")

    def print_itens(self, data):
        self.print_line_separator()
        self.printer.set(bold=True, align='left', font="a")
        self.printer.line_spacing(spacing=1)
        self.printer.text(data)

    def print_document(self, data):
        text_header = data["header"]["issuer"]
        img_source = data["header"]["logo"]
        products_list = data["products"]
        total_itens = data["totais"]
        fiscal = data["fiscal"]
        url_sefaz = data["url_sefaz"]
        qrcode = data["qrcode"]
        consumer = data["consumer"]
        ambient = data["ambient"]
        emission = data["emission_type"]
        try:
            self.print_header_logo(img_source, text_header)
            self.print_title_document()
            self.print_header_document()
            self.print_produtcs(products_list)
            self.print_itens(total_itens)
            self.print_payments(data)
            self.print_url_document(data)
            self.print_type_document(consumer, ambient, emission)
            self.print_qrcode(fiscal, qrcode)
            self.print_complements(data)
            self.print_message(data)
            self.printer.cut()
            result = (self.printer.output,
                      "Documento enviado para impressão com sucesso.")
        except Exception as e:
            result = (False, e)
        return result
