import io
import base64
from PIL import Image
from datetime import datetime
from pyprinter.controllers.text_controller import format_cpf_cnpj
from pyprinter.controllers.document_controller import DocumentController


def base64_img(file_path):
    img = Image.open(file_path)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
    return f'data:image/png;base64,{img_base64}'


def get_header(data):
    complement_address = data.emit()["enderEmit"].get("xCpl")
    zip_code = data.emit()["enderEmit"].get("CEP")
    string_header = (
        f'CNPJ: {format_cpf_cnpj(data.emit()["CNPJ"])}\n'
        f'{data.emit()["xNome"]}\n'
        f'{data.emit()["enderEmit"]["xLgr"]}, {data.emit()["enderEmit"].get("nro", "s/n")}\n'
        # f'{data.emit()["enderEmit"]["xLgr"]}, {data.emit()["enderEmit"].get("nro", "s/n")}{", " + zip_code if zip_code else ""}\n'
        # f'{data.emit()["enderEmit"]["xBairro"]} - {data.emit()["enderEmit"]["CEP"]},'
        f'{complement_address + ", " if complement_address  else ""}{data.emit()["enderEmit"]["xBairro"]}\n'
        # f'{data.emit()["enderEmit"].get("xCpl", "")}\n'
        # f'{data.emit()["enderEmit"]["xMun"]} - {data.emit()["enderEmit"]["UF"]}\n'
        f'{data.emit()["enderEmit"]["xMun"]} - {data.emit()["enderEmit"]["UF"]}\n'
        f'Fone: {data.emit()["enderEmit"].get("fone", "")}'
    )
    return string_header


def mount_list_item(item):
    info_add_product = item.get("infAdProd", "")
    item_list = [
        item["prod"]["cProd"],
        f'{item["prod"]["xProd"]} {info_add_product.lower()}',
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
    # document.impost()["vTotTrib"]
    # document.impost()["vNF"]
    max_line_width = 48
    items_str = f'{document.total_itens} Itens'
    value_str = f'Total Da Nota R$ {document.impost()["vNF"]}'
    available_items_width = max_line_width - len(value_str)
    items_str = items_str[:available_items_width]
    total_str = f'{items_str:<{available_items_width}}{value_str:>}'
    return total_str


def get_fiscal(document, emission_type):
    dh_final = (
        datetime.fromisoformat(document.identification_nfe()["dhEmi"])
        if emission_type.upper() == 'CONTINGENCIA'
        else datetime.fromisoformat(document.info_nfe().get("dhRecbto"))
    )
    protocol = document.info_nfe().get("nProt")
    authorization_text = f'Protocolo de autorizacao:\n{protocol}\n' if protocol else ''
    contingency_message = (
        'Via do Consumidor\nEMITIDA EM CONTINGENCA\nPendente de Autorizacao\n'
        if emission_type.upper() == 'CONTINGENCIA' else ''
    )
    extra_info = (
        'emissao'
        if emission_type.upper() == 'CONTINGENCIA'
        else 'autorizacao'
    )
    string_fiscal = (
        f'NFC-e Serie {document.identification_nfe()["serie"]}\n'
        f'N° {document.identification_nfe()["nNF"]}\n'
        f'{authorization_text}'
        f'Data da {extra_info}\n'
        f'{dh_final.strftime("%d/%m/%Y %H:%M:%S")} hs\n'
        f'{contingency_message}'
        f'{document.identification_nfe()["verProc"]}'
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


def make_dict(source=None, content=None, logo=None):
    document = DocumentController(source, content)
    logo_path = document.logo(logo_path=logo) or document.logo()
    emission = document.identification_nfe()["tpEmis"]
    ambient_type = document.identification_nfe()["tpAmb"]
    invoice_key = document.info_nfe()["chNFe"]
    document_type = get_nf_model(invoice_key[20:22])
    split_invoice_key = ' '.join(invoice_key[i:i+4] for i in range(0, len(invoice_key), 4))
    emission_type = "normal" if emission == "1" else "contingencia"
    payments = document.payments()
    dict_details = {
        "header": {
            "logo": logo_path,
            "issuer": get_header(document),
        },
        "ambient": "producao" if ambient_type == "1" else "homologacao",
        "emission_type": emission_type,
        "products": get_itens(document),
        "totais": get_total(document),
        "payments": get_payments(payments),
        "consumer": document.dest(),
        "text_url_sefaz": "Consulta pela chave de acesso em\n"
                          "www.sefaz.es.gov.br/nfce/consulta\n"
                          f"{split_invoice_key}",
        "url_sefaz": document.codes()["urlChave"] if document_type == "NFC-e" else None,
        "qrcode": document.codes()["qrCode"],
        "fiscal": get_fiscal(document, emission_type),
        "complements": f"Fonte: Impostos lbpt (fonte lbpt) Tributos Totais\n"
                       f"Incidentes (Lei Federal 12.741/2012) R$ {document.impost()['vTotTrib']}",
        "message": document.additional_info().get("infCpl", "")
    }
    return dict_details
