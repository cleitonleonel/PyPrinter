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

    def _get_inf_nfe(self):
        """
        Método privado para obter a parte específica dos dados relacionada a infNFe.
        """
        return self.data["nfeProc"]["NFe"]["infNFe"]

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
        return self._get_inf_nfe()["emit"]

    def dest(self):
        return self._get_inf_nfe().get("dest", {})

    def itens(self):
        return self._get_inf_nfe()["det"]

    def info_nfe(self):
        return self.data["nfeProc"]["protNFe"]["infProt"]

    def info_itens(self):
        return self._get_inf_nfe()["det"]["prod"]

    def fiscal(self):
        return self._get_inf_nfe()["ide"]

    def impost(self):
        return self._get_inf_nfe()["total"]["ICMSTot"]

    def protocol(self):
        return self.info_nfe()["nProt"]

    def codes(self):
        return self.data["nfeProc"]["NFe"]["infNFeSupl"]

    def payments(self):
        return self._get_inf_nfe()["pag"]

    def additional_info(self):
        return self._get_inf_nfe()["infAdic"]
