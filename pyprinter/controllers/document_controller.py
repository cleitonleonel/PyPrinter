import xmltodict
from pyprinter.config import get_project_root

BASE_DIR = get_project_root()
LOGO_DEFAULT_PATH = (BASE_DIR / 'pyprinter/resources/media/nf-e-nota-fiscal-eletronica.png').as_posix()


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
        if self.data.get("nfeProc"):
            inf_nfe = self.data["nfeProc"]["NFe"]["infNFe"]
        else:
            inf_nfe = self.data["NFe"]["infNFe"]
        return inf_nfe

    def get_data(self):
        if not self.content:
            with open(self.filepath, 'rb') as xml:
                self.data = xmltodict.parse(xml)
        else:
            self.data = xmltodict.parse(self.content)

    def logo(self, logo_path=LOGO_DEFAULT_PATH):
        self.logo_path = logo_path
        return self.logo_path

    def emit(self):
        return self._get_inf_nfe()["emit"]

    def dest(self):
        return self._get_inf_nfe().get("dest", {})

    def itens(self):
        return self._get_inf_nfe()["det"]

    def info_nfe(self):
        if self.data.get("nfeProc"):
            info_nfe = self.data["nfeProc"]["protNFe"]["infProt"]
        else:
            info_nfe = self.data["NFe"]
            info_nfe["chNFe"] = info_nfe["infNFe"]["@Id"].replace("NFe", "")
        return info_nfe

    def info_itens(self):
        return self._get_inf_nfe()["det"]["prod"]

    def identification_nfe(self):
        return self._get_inf_nfe()["ide"]

    def impost(self):
        return self._get_inf_nfe()["total"]["ICMSTot"]

    def protocol(self):
        return self.info_nfe()["nProt"]

    def codes(self):
        if self.data.get("nfeProc"):
            codes = self.data["nfeProc"]["NFe"]["infNFeSupl"]
        else:
            codes = self.data["NFe"]["infNFeSupl"]
        return codes

    def payments(self):
        return self._get_inf_nfe()["pag"]

    def additional_info(self):
        return self._get_inf_nfe()["infAdic"]
