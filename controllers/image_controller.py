#!/usr/bin/python
#  -*- coding: utf-8 -*-
import io
import re
import qrcode
import base64
from PIL import (Image,
                 ImageDraw,
                 ImageFont)


def line_break(text, limit):
    lines = text.splitlines()
    lines_broken = []
    for line in lines:
        words = line.split()
        line_broken = ''
        for word in words:
            if len(line_broken + word) <= limit:
                line_broken += word + ' '
            else:
                lines_broken.append(line_broken.strip())
                line_broken = word + ' '
        lines_broken.append(line_broken.strip())
    return "\n".join(lines_broken)


class ImageController:

    def __init__(self):
        pass

    def load_logo(self, img_source, target_size=(100, 100)):
        img = Image.open(img_source)
        img = img.resize(target_size, Image.LANCZOS)
        return img

    def generate_header(self, text, img_source, output_path):
        # Largura desejada da imagem em milímetros
        image_width_mm = 80
        # Converta a largura para pixels (considerando uma escala padrão de 1mm por coluna)
        image_width_pixels = int(image_width_mm * 8)  # 1mm = 8 pixels
        edited_text = line_break(text, 34)
        total_lines = len(edited_text.split("\n")) + 2
        total_height = total_lines * 20
        blank_image = Image.new('RGB', (image_width_pixels, total_height), 'white')
        if "data:image" in img_source:
            data_img = re.sub('^data:image/.+;base64', '', img_source)
            decoded_img = base64.b64decode(data_img)
            img_source = io.BytesIO(decoded_img)
        logo = Image.open(img_source).convert('RGBA')
        logo = logo.resize((150, 150), Image.LANCZOS)
        blank_image.paste(logo, (10, 10), logo)
        draw = ImageDraw.Draw(blank_image)
        font = ImageFont.load_default(size=20)
        draw.text((200, 10), edited_text, font=font, fill='black')
        # blank_image.save(output_path)
        return blank_image

    def qrcode_adjust(self, text_data, qr_data="PyPrinter", output_path="qr_adjust.png", img_source=None):
        # Largura desejada da imagem em milímetros
        image_width_mm = 80
        # Converta a largura para pixels (considerando uma escala padrão de 1mm por coluna)
        image_width_pixels = int(image_width_mm * 8)  # 1mm = 8 pixels
        blank_image = Image.new('RGB', (image_width_pixels, 250), 'white')
        info_image = Image.new('RGB', (int(image_width_pixels / 2), 250), 'white')
        img = self.generate_qr_code(qr_data)
        if img_source:
            img = Image.open(img_source).convert('RGBA')
        img.convert('RGBA')
        img = img.resize((216, 216), Image.LANCZOS)
        blank_image.paste(img, (20, 15))
        draw = ImageDraw.Draw(info_image)
        # font = ImageFont.load_default(size=18)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 20)
        draw.text((10, 25), text_data, fill="black", font=font_bold, spacing=10, align="center")
        # info_image.save("text_image.png")
        info_image.convert("RGBA")
        blank_image.paste(info_image, (240, 0))
        # blank_image.save(output_path, format="PNG")
        return blank_image

    def generate_qr_code(self, data, output_path="qrcode.png"):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=1
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # img.save(output_path)
        return img
