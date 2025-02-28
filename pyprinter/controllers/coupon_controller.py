from pyprinter.controllers.text_controller import (
    line_break,
    format_cpf_cnpj,
    description_break
)
from pyprinter.controllers.image_controller import ImageController
from escpos.printer import Usb, Dummy

img_controller = ImageController()


class DanfcePrinter(object):

    def __init__(
            self,
            vendor_id=0x0416,
            product_id=0x5011,
            init_point=0x81,
            end_point=0x03
    ):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.init_point = init_point
        self.end_point = end_point
        self.printer = None

    def initialize(self, dummy=False):

        if dummy:
            self.printer = Dummy(
                devfile="document.txt",
                autocut=True
            )
        else:
            self.printer = Usb(
                self.vendor_id,
                self.product_id,
                in_ep=self.init_point,
                out_ep=self.end_point,
                profile="POS80"
            )
        self.printer.profile.profile_data["media"]["width"]["mm"] = 80
        self.printer.profile.profile_data["media"]["width"]["pixels"] = 640
        self.printer.profile.profile_data["media"]["dpi"] = 203
        self.printer.charcode('CP850')

    def print_line_separator(self, text="-", size_line=48):
        line = f"{text * size_line}"
        self.printer.set(bold=True, font="a")
        self.printer.text(line)

    def print_header_logo(self, img_source, text_header):
        header_img = img_controller.generate_header(
            text_header, img_source,
            "draw_logo.jpeg"
        )
        self.printer.image(header_img.convert('L'))

    def print_title_document(self):
        self.print_line_separator(text="=")
        self.printer.ln()
        self.printer.set(bold=True, align='center', font="b")
        self.printer.textln("DANFE NFC-e - DOCUMENTO AUXILIAR DA NOTA")
        self.printer.textln("FISCAL DE CONSUMIDOR ELETRONICA")

    def print_payments(self, data):
        self.print_line_separator()
        self.printer.textln("Forma De Pagamento                          Pago")
        self.printer.set(bold=True, align='left', font="b")
        self.printer.set(bold=False)
        for row in data["payments"]:
            formatted_row = f"{row[0]:<40} {row[1]:>23}"
            self.printer.textln(formatted_row)

    def print_url_document(self, data):
        self.print_line_separator()
        self.printer.set(bold=False, align='center', font="b")
        self.printer.textln(data["text_url_sefaz"])

    def print_type_document(self, consumer, ambient, emission):
        self.print_line_separator()
        self.printer.set(bold=True, align='center', font="a")
        ambient_info, address_text = ("", "")
        document = (
                consumer.get("CPF") or
                consumer.get("CNPJ", "")
        )
        name = consumer.get("xNome")
        address_consumer = consumer.get("enderDest", {})
        street = address_consumer.get("xLgr")
        number = address_consumer.get("nro")
        neighborhood = address_consumer.get("xBairro")
        city = address_consumer.get("xMun")
        self.printer.textln(f'CONSUMIDOR {format_cpf_cnpj(document)}')
        self.printer.set(bold=False, align='center', font="b")
        if all([name, street, number, neighborhood, city]):
            self.printer.textln(f"{line_break(name.replace(' - ', ' '), limit=40)}")
            address_text = (
                f"{street}, {number} "
                f"{neighborhood} - {city}"
            )
        if ambient.upper() != "PRODUCAO":
            ambient_complement = "AMBIENTE DE" if ambient.upper() == "HOMOLOGACAO" else ""
            ambient_info = f'NFC-E EMITIDA EM {ambient_complement} {ambient.upper()}'
        if emission.upper() == "CONTINGENCIA":
            self.printer.set(bold=True, align='center', font="a")
            self.printer.textln("EMITIDA EM CONTINGENCIA")
            self.printer.set(bold=False, align='center', font="a")
            self.printer.textln("Pendente de Autorizacao")

        # Não imprimir informações de endereço do cliente.
        # self.printer.text(address_text)

        self.printer.set(bold=True, align='center', font="a")
        self.printer.textln(f"{ambient_info}")

    def print_qrcode(self, fiscal, qr_url):
        qr_img_container = img_controller.qrcode_adjust(
            fiscal,
            qr_data=qr_url
        )
        self.print_line_separator()
        self.printer.set(align='center')
        self.printer.image(
            qr_img_container.convert('L'),
            impl='bitImageColumn',
            center=True
        )

    def print_complements(self, data):
        self.print_line_separator()
        self.printer.set(bold=False, align='center', font="b")
        self.printer.control("B")
        self.printer.textln(data["complements"])

    def print_message(self, data):
        self.print_line_separator()
        self.printer.set(bold=False, align='center', font="b")
        message = data["message"]
        lines = "\n".join([message[i:i + 60] for i in range(0, len(message), 60)])
        self.printer.textln(lines)

    def print_header_document(self):
        self.print_line_separator(text="=")
        self.printer.set(bold=True, font="b")
        header = (
            f"{'Codigo':<6} {'Descricao dos produtos':<26} "
            f"{'Quantidade':>14} {'Preco':>7} {'Total':>7}"
        )
        self.printer.textln(header)

    def print_produtcs(self, products):
        for product in products:
            result_str = ""
            code, description, quantity, price, total = product
            self.printer.set(bold=False, font="b")
            if len(description) > 30:
                broken_description = line_break(description, 31)
                first_line = f"{code:<6} {broken_description[0]:<31} {quantity:>9} {price:>7} {total:>7}"
                result_str += first_line
                for index, line in enumerate(broken_description[1:]):
                    if index > 0:
                        result_str += '\n'
                    max_length = 56 if len(line) > 20 else 31
                    result_str += f"{'':>6} {line:<{max_length}}"
            else:
                result_str = f"{code:<6} {description:<31} {quantity:>9} {price:>7} {total:>7}"
            self.printer.textln(result_str)

    def print_table(self, products):
        for product in products:
            result_str = ""
            code, description, quantity, price, total = product
            formated_price = f"{float(price):.2f}"
            self.printer.set(bold=False, font="b")
            if len(description) > 30:
                broken_description = description_break(description, 57)
                result_str += f"{code:<6} {broken_description[0]:<57}"
                for line in broken_description[1:]:
                    result_str += f"{'':<6} {line:<57}"
            else:
                result_str += f"{code:<6} {description:<57}"
            result_str += f"{'':<6} {'':<31} {quantity:>9} {formated_price:>7} {total:>7}"
            self.printer.textln(result_str)

    def print_itens(self, data):
        self.print_line_separator()
        self.printer.set(bold=True, align='left', font="a")
        self.printer.textln(data)

    def print_document(self, data):
        text_header = data["header"]["issuer"]
        img_source = data["header"]["logo"]
        products_list = data["products"]
        total_items = data["totais"]
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
            # self.print_products(products_list)
            self.print_table(products_list)
            self.print_itens(total_items)
            self.print_payments(data)
            self.print_url_document(data)
            self.print_type_document(consumer, ambient, emission)
            self.print_qrcode(fiscal, qrcode)
            self.print_complements(data)
            self.print_message(data)
            self.printer.print_and_feed(1)
            # self.printer.ln(count=6)
            self.printer.cut()
            result = (
                self.printer.output,
                "Documento enviado para impressão com sucesso."
            )
        except Exception as e:
            result = (False, f"Error: {e}")
        return result
