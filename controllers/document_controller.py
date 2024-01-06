#!/usr/bin/python
#  -*- coding: utf-8 -*-
import os
import xmltodict

BASE_DIR = os.getcwd()


class DocumentController(object):

    def __init__(self, source=None, content=None):
        self.content = content
        self.filepath = source
        self.data = None
        self.logo_path = None
        self.total_itens = None
        self.get_data()

    def get_data(self):
        if not self.content:
            with open(self.filepath, 'rb') as xml:
                self.data = xmltodict.parse(xml)
        else:
            self.data = xmltodict.parse(self.content)

    def logo(self, logo_path=f'{BASE_DIR}/src/media/nf-e-nota-fiscal-eletronica.png'):
        self.logo_path = logo_path
        return self.logo_path

    def emit(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["emit"]

    def itens(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["det"]

    def info_nfe(self):
        return self.data["nfeProc"]["protNFe"]["infProt"]

    def info_itens(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["det"]["prod"]

    def fiscal(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["ide"]

    def impost(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["total"]["ICMSTot"]

    def protocol(self):
        return self.data["nfeProc"]["protNFe"]["infProt"]["nProt"]

    def codes(self):
        return self.data["nfeProc"]["NFe"]["infNFeSupl"]

    def payments(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["pag"]

    def additional_info(self):
        return self.data["nfeProc"]["NFe"]["infNFe"]["infAdic"]
