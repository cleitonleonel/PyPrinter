from pyprinter.controllers.text_controller import line_break, format_cpf_cnpj
from pyprinter.controllers.image_controller import ImageController
from PIL import Image, ImageDraw, ImageFont

img_controller = ImageController()


class DanfcePrinter(object):
    def __init__(self):
        self.image = None
        self.draw = None
        self.font = ImageFont.load_default()
        self.width = int(80 * 3.78)  # 80mm converted to pixels (assuming 96 DPI, 3.78 pixels per mm)
        self.height = int(210 * 3.78)  # 210mm converted to pixels, initial height
        self.y_position = 0

    def initialize(self):
        self.image = Image.new('RGB', (self.width, self.height), 'white')
        self.draw = ImageDraw.Draw(self.image)

    def save_image(self, file_path):
        self.image = self.image.crop((0, 0, self.width, self.y_position))
        self.image.save(file_path)

    def print_line_separator(self, text="-", size_line=48):
        line = text * size_line
        self.draw.text((10, self.y_position), line, font=self.font, fill="black")
        self.y_position += 20

    def print_header_logo(self, img_source, text_header):
        header_img = Image.open(img_source).convert('L')
        self.image.paste(header_img, (10, self.y_position))
        self.y_position += header_img.height + 10
        lines = text_header.split("\n")
        for line in lines:
            self.draw.text((header_img.width + 20, self.y_position), line, font=self.font, fill="black")
            self.y_position += 20

    def print_title_document(self):
        self.print_line_separator(text="=", size_line=40)
        self.draw.text((10, self.y_position), "DANFE NFC-e - DOCUMENTO AUXILIAR DA NOTA", font=self.font, fill="black")
        self.y_position += 20
        self.draw.text((10, self.y_position), "FISCAL DE CONSUMIDOR ELETRONICA", font=self.font, fill="black")
        self.y_position += 20

    def print_header_document(self):
        self.print_line_separator(text="=", size_line=40)
        header = ("Codigo  Descricao dos produtos             Qtd    Preco  Total")
        self.draw.text((10, self.y_position), header, font=self.font, fill="black")
        self.y_position += 20

    def print_payments(self, data):
        self.print_line_separator()
        self.draw.text((10, self.y_position), "Forma De Pagamento                     Pago", font=self.font,
                       fill="black")
        self.y_position += 20
        for row in data["payments"]:
            formatted_row = f"{row[0]:<25} {row[1]:>15}"
            self.draw.text((10, self.y_position), formatted_row, font=self.font, fill="black")
            self.y_position += 20

    def print_url_document(self, data):
        self.print_line_separator()
        self.draw.text((10, self.y_position), data["text_url_sefaz"], font=self.font, fill="black")
        self.y_position += 20

    def print_type_document(self, consumer, ambient, emission):
        self.print_line_separator()
        document = (consumer.get("CPF") or consumer.get("CNPJ", ""))
        name = consumer.get("xNome")
        address_consumer = consumer.get("enderDest", {})
        street = address_consumer.get("xLgr")
        number = address_consumer.get("nro")
        neighborhood = address_consumer.get("xBairro")
        city = address_consumer.get("xMun")
        self.draw.text((10, self.y_position), f'CONSUMIDOR {format_cpf_cnpj(document)}', font=self.font, fill="black")
        self.y_position += 20
        if all([name, street, number, neighborhood, city]):
            self.draw.text((10, self.y_position), line_break(name.replace(' - ', ' '), limit=25), font=self.font,
                           fill="black")
            self.y_position += 20
            address_text = (f"{street}, {number} {neighborhood} - {city}")
            self.draw.text((10, self.y_position), address_text, font=self.font, fill="black")
            self.y_position += 20
        if ambient.upper() != "PRODUCAO":
            ambient_info = f'NFC-E EMITIDA EM AMBIENTE DE {ambient.upper()}'
            self.draw.text((10, self.y_position), ambient_info, font=self.font, fill="black")
            self.y_position += 20
        if emission.upper() == "CONTINGENCIA":
            self.draw.text((10, self.y_position), "EMITIDA EM CONTINGENCIA", font=self.font, fill="black")
            self.y_position += 20
            self.draw.text((10, self.y_position), "Pendente de Autorizacao", font=self.font, fill="black")
            self.y_position += 20

    def print_qrcode(self, fiscal, qr_url):
        qr_img_container = img_controller.qrcode_adjust(fiscal, qr_data=qr_url)
        self.print_line_separator()
        qr_size = 150  # Ajuste o tamanho do QR code para 150 pixels
        qr_img_resized = qr_img_container.resize((qr_size, qr_size))
        self.image.paste(qr_img_resized.convert('L'), (10, self.y_position))
        self.y_position += qr_img_resized.height + 10

    def print_complements(self, data):
        self.print_line_separator()
        self.draw.text((10, self.y_position), data["complements"], font=self.font, fill="black")
        self.y_position += 20

    def print_message(self, data):
        self.print_line_separator()
        message = data["message"]
        lines = "\n".join([message[i:i + 40] for i in range(0, len(message), 40)])
        self.draw.text((10, self.y_position), lines, font=self.font, fill="black")
        self.y_position += 20

    def print_products(self, products):
        for product in products:
            code, description, quantity, price, total = product
            if len(description) > 25:
                broken_description = line_break(description, 25).split("\n")
                first_line = f"{code:<6} {broken_description[0]:<25} {quantity:>4} {price:>7} {total:>7}"
                self.draw.text((10, self.y_position), first_line, font=self.font, fill="black")
                self.y_position += 20
                for line in broken_description[1:]:
                    max_length = 31 if len(line) > 20 else 25
                    self.draw.text((10, self.y_position), f"{'':>6} {line:<{max_length}}", font=self.font, fill="black")
                    self.y_position += 20
            else:
                result_str = f"{code:<6} {description:<25} {quantity:>4} {price:>7} {total:>7}"
                self.draw.text((10, self.y_position), result_str, font=self.font, fill="black")
                self.y_position += 20

    def print_items(self, data):
        self.print_line_separator()
        self.draw.text((10, self.y_position), data, font=self.font, fill="black")
        self.y_position += 20

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
            self.print_products(products_list)
            self.print_items(total_items)
            self.print_payments(data)
            self.print_url_document(data)
            self.print_type_document(consumer, ambient, emission)
            self.print_qrcode(fiscal, qrcode)
            self.print_complements(data)
            self.print_message(data)
            self.save_image("document.png")
            result = (True, "Documento salvo como imagem com sucesso.")
        except Exception as e:
            result = (False, f"Error: {e}")
        return result
