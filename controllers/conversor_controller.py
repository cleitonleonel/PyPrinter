#!/usr/bin/python
#  -*- coding: utf-8 -*-
import io
import base64
from PIL import Image
from datetime import datetime
from controllers.document_controller import DocumentController


def base64_img(file_path):
    img = Image.open(file_path)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
    return f'data:image/png;base64,{img_base64}'


def get_header(data):
    string_header = (
        f'{data.emit()["CNPJ"]}\n'
        f'{data.emit()["xNome"]}\n'
        f'{data.emit()["enderEmit"]["xLgr"]}, {data.emit()["enderEmit"].get("nro", "")}\n'
        f'{data.emit()["enderEmit"]["xBairro"]} - {data.emit()["enderEmit"]["CEP"]},'
        f'{data.emit()["enderEmit"].get("xCpl", "")}\n'
        f'{data.emit()["enderEmit"]["xMun"]} - {data.emit()["enderEmit"]["UF"]}\n'
        f'Fone / Fax: {data.emit()["enderEmit"].get("fone", "")}'
    )
    return string_header


def mount_list_item(item):
    item_list = [
        item["prod"]["cProd"],
        item["prod"]["xProd"],
        f'{item["prod"]["qCom"]} {item["prod"]["uCom"]}',
        item["prod"]["vUnTrib"],
        item["prod"]["vProd"]
    ]
    return item_list


def get_itens(document):
    data = document.itens()
    list_itens = []
    if isinstance(data, list):
        document.total_itens = len(data)
        for item in data:
            dict_itens = mount_list_item(item)
            list_itens.append(dict_itens)
    else:
        document.total_itens = 1
        list_itens.append(mount_list_item(data))
    return list_itens


def get_total(document):
    # document.impost()["vProd"]
    # document.impost()["vDesc"]
    # document.impost()["vFrete"]
    # document.impost()["vTotTrib"]
    # document.impost()["vNF"]
    total = f'{document.total_itens} Itens                  Total Da Nota R$ {document.impost()["vNF"]}\n'
    return total


def get_fiscal(document):
    data_obj = datetime.fromisoformat(document.fiscal()["dhEmi"])
    string_fiscal = (
        f'NFC-e Serie {document.fiscal()["serie"]}\n'
        f'N° {document.fiscal()["cNF"]}\n'
        f'Protocolo de autorizacao:\n'
        f'{document.info_nfe()["nProt"]}\n'
        f'{data_obj.strftime("%d/%m/%Y %H:%M:%S")} hs\n\n'
        f'{document.fiscal()["verProc"]}'
    )
    return string_fiscal


def get_card(banner):
    cards = {
        "01": "Visa",
        "02": "MasterCard",
        "03": "American Express",
        "04": "SoroCred",
        "05": "Diners",
        "06": "Elo",
        "07": "HiperCard",
        "08": "Aura",
        "09": "Cabal",
        "10": "Alelo",
        "11": "BanesCard",
        "12": "CalCard",
        "13": "CredZ",
        "14": "Discover",
        "15": "GoodCard",
        "16": "Gre3nCard",
        "17": "Hiper",
        "18": "JcB",
        "19": "Mais",
        "20": "MaxVan",
        "21": "PoliCard",
        "22": "RedeCompras",
        "23": "Sodexo",
        "24": "ValeCard",
        "25": "VeroCheque",
        "26": "VR",
        "27": "Ticket"
    }

    return cards.get(banner, 'Outros')


def get_payment_type(pay):
    payments_type = {
        "01": "Dinheiro",
        "02": "Cheque",
        "03": "Cartao de Credito",
        "04": "Cartao de Debito",
        "05": "Credito Loja",
        "10": "Vale Alimentacao",
        "11": "Vale Refeicao",
        "12": "Vale Presente",
        "13": "Vale Combustivel",
        "15": "Boleto Bancario",
        "16": "Deposito Bancario",
        "17": "PIX",
        "18": "Transf/Cart.Digital",
        "19": "Credito Virtual"
    }

    return payments_type.get(pay, 'Outros')


def get_nf_model(model):
    models = {
        "25": "MDF-e",
        "55": "NF-e",
        "57": "CT-e",
        "65": "NFC-e"
    }
    return models.get(model, None)


def get_payments(payments):
    new_payments = []
    payments["detPag"] = [payments["detPag"]] \
        if not isinstance(payments["detPag"], list) else payments["detPag"]
    for payment in payments["detPag"]:
        if payment.get("card"):
            payment_string = [
                f'{get_payment_type(payment["tPag"])} {get_card(payment["card"].get("tBand"))}',
                payment["vPag"]
            ]
        else:
            payment_string = [
                get_payment_type(payment["tPag"]),
                payment["vPag"]
            ]
        new_payments.append(payment_string)
    if payments.get("vTroco") and payments.get("vTroco") != '0,00':
        payment_change = [
            "Troco:",
            payments.get("vTroco")
        ]
        new_payments.append(payment_change)
    return new_payments


def make_dict(source=None, content=None):
    document = DocumentController(source, content)
    invoice_key = document.info_nfe()["chNFe"]
    document_type = get_nf_model(invoice_key[20:22])
    payments = document.payments()
    dict_details = {
        "header": {
            "logo": document.logo(),
            "issuer": get_header(document),
        },
        "products": get_itens(document),
        "totais": get_total(document),
        "payments": get_payments(payments),
        "text_url_sefaz": "Consulta pela chave de acesso em\n"
                          "www.sefaz.es.gov.br/nfce/consulta\n"
                          f"{invoice_key}\n",
        "url_sefaz": document.codes()["urlChave"] if document_type == "NFC-e" else None,
        "fiscal": get_fiscal(document),
        "complements": f"Fonte: Impostos lbpt (fonte lbpt) Tributos Totais\n"
                       f"Incidentes (Lei Federal 12.741/2012) R$ {document.impost()['vTotTrib']}\n",
        "message": document.additional_info()["infCpl"]
    }
    return dict_details
