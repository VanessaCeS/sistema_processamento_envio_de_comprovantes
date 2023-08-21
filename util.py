import os
import re
import json
import pymssql
import shutil
import requests
import traceback
import xmltodict
from time import sleep
from pathlib import Path
from requests import Session
from docx2pdf import convert
from base64 import b64decode
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import unquote
from unicodedata import normalize
from zeep import Client, Settings, Transport


load_dotenv('.env')
base_path = os.environ.get('base_projeto')
path_arquivos = f"{base_path}robo_pagamentos\\planilhas"

server = os.getenv('db_server_dev')
database = os.getenv('db_database_dev')
username = os.getenv('db_username_dev')
password = os.getenv('db_password_dev')
# ==============================================================================
#   Funções do Banco de Dados
# ==============================================================================
def sql_integra_get(sql):
    conx = pymssql.connect(os.environ.get('db_server'),
                        os.environ.get('db_username'),
                        os.environ.get('db_password'),
                        os.environ.get('database_integra')
                        )

    cursor = conx.cursor(as_dict=True)

    cursor.execute(sql)

    dados = cursor.fetchall()

    conx.close()

    return dados


def sql_integra_exec(sql, val):
    conx = pymssql.connect(os.environ.get('db_server'),
                        os.environ.get('db_username'),
                        os.environ.get('db_password'),
                        os.environ.get('database_integra')
                        )

    cursor = conx.cursor()

    cursor.execute(sql, val)
    conx.commit()
    conx.close()

    return True

def get_token(user='integra.api'):
    sql = "SELECT token FROM archer_token WHERE users = '%s'" % user
    result = sql_integra_get(sql)
    return result[0]['token']


def execute_sql_integra(id_sistema_pagamento, dados, nomes):
    conn = pymssql.connect(server=server, database=database, user=username, password=password)
    cursor = conn.cursor()

    table_exists = "SELECT * FROM Integra.INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'comprovantes_sap'"
    cursor.execute(table_exists)

    if cursor.fetchall():
        cursor.execute("SELECT * FROM Integra.dbo.comprovantes_sap WHERE id_sistema_pagamento = %s ", (id_sistema_pagamento,))
        for i in range(len(dados)):
            if dados[i] == '':
                dados[i] = None

        id_sistema = cursor.fetchone()
        if id_sistema is not None:
            try:
                set_clause = ', '.join([f"{col} = %s" for col in nomes])
                query = f"UPDATE Integra.dbo.comprovantes_sap SET {set_clause} WHERE id_sistema_pagamento = %s"
                valores = tuple(dados) + (id_sistema_pagamento,)
                cursor.execute(query, valores)
                conn.commit()
                conn.close()
            except Exception as e:
                print("E ==>> ", e)
                print("Exec ==>> ", traceback.print_exc())

        else:
            try:
                valores = tuple(dados)
                colunas = ', '.join(nomes)
                placeholders = ', '.join(['%s' for _ in nomes])
                query = f"INSERT INTO Integra.dbo.comprovantes_sap ({colunas}) VALUES ({placeholders})"
                cursor.execute(query, valores)
                conn.commit()
                conn.close()
            except Exception as e:
                print("Error ==> ", e)
                print("Caminho ==> ", traceback.print_exc())


# ==============================================================================
#   Funções do Banco de Dados
# ==============================================================================
# ==============================================================================
#   Funções da API do ARCHER
# ==============================================================================

def extrair_doc_arteria_pag(fileId, folder, scpjud):
    # wsdl = r'C:\Users\User\PycharmProjects\migracao_peca2\wsdl-arteria.xml'
    wsdl = rf'{base_path}robo_pagamentos\\wsdl-arteria.xml'
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=wsdl, transport=Transport(timeout=15), settings=settings)

    # Para Debug
    # settings = Settings(strict=False, xml_huge_tree=True)
    # session = Session()
    # session.proxies = {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}
    # session.verify = "C:\\Users\\User\\Documents\\charles.pem"
    # client = Client(wsdl=wsdl, transport=Transport(session=session, timeout=100), settings=settings)

    search = client.service.GetAttachmentFile(sessionToken=f"{get_token()}", fileId=fileId)
    dict_search = xmltodict.parse(search)
    if dict_search['files'] is None:
        raise Exception('no_file')
    bytes = b64decode(dict_search['files']['file']['#text'], validate=True)

    aux = dict_search['files']['file']['@name'].split(".")
    tipo = aux[len(aux) - 1]

    if bytes[0:4] != b'%PDF':
        raise Exception(tipo)

    nome_arquivo = scpjud + '_' + tratar_texto(dict_search['files']['file']['@name'])

    f = open(f'{folder}\\{nome_arquivo[:54]}.pdf', 'wb')
    f.write(bytes)
    f.close()

    return nome_arquivo[:54]


def get_atach_rest(atach_id, folder):
    endpoint = 'https://arteria.costaesilvaadv.com.br/RSAarcher/platformapi/core/content/attachment/' + atach_id
    s = Session()
    s.proxies = {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}
    s.verify = "C:\\Users\\User\\Documents\\charles.pem"
    s.headers = {'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
                'Authorization': 'Archer session-id=' + get_token(),
                'Content-Type': 'application/json',
                'X-Http-Method-Override': 'GET'}
    result = s.post(endpoint).json()['RequestedObject']
    bytes = b64decode(result['AttachmentBytes'], validate=True)

    if bytes[0:4] != b'%PDF':
        raise Exception(f'O Arquivo Não e um PDF extensão : {bytes[0:4]}')

    nome_arquivo = atach_id + '_' + tratar_texto(result['AttachmentName'])

    f = open(f'{folder}/{nome_arquivo}.pdf', 'wb')
    f.write(bytes)
    f.close()

    return nome_arquivo


# ==============================================================================
#   Funções da API do ARCHER
# ==============================================================================

# ==============================================================================
#   Funções Gerais
# ==============================================================================

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    COMMON = "\033[120m"
    fgGreen = "\033[32m"
    fgBrightGreen = "\033[32;1m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def cronometro(value):
    m, s = divmod(value, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def mensagens(mensagem, tipo, bold=False):
    if bold:
        mensagem = bcolors.BOLD + mensagem + bcolors.ENDC
    if tipo == "ok":
        print(bcolors.OKGREEN + mensagem + bcolors.ENDC)
    elif tipo == "ok2":
        print(bcolors.fgGreen + mensagem + bcolors.ENDC)
    elif tipo == "ok3":
        print(bcolors.OKBLUE + mensagem + bcolors.ENDC)
    elif tipo == "warning":
        print(bcolors.WARNING + mensagem + bcolors.ENDC)
    elif tipo == "fail":
        print(bcolors.FAIL + mensagem + bcolors.ENDC)
    elif tipo == "info":
        print(bcolors.COMMON + mensagem + bcolors.ENDC)


def remover_acentos(txt):
    return normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")


def tratar_texto(txt):
    return re.sub(r"[^a-zA-Z0-9]", "", remover_acentos(txt[:-4].upper()))


def download_zip_docs(docss, path):
    Path(path).mkdir(
        parents=True, exist_ok=True)
    for docs in docss:
        for doc in docs:
            try:
                extrair_doc_arteria_pag(
                    doc['id_arquivo'], Path(path), doc['scpjud'].replace(" ", "_"))
            except Exception as e:
                print(e)
    shutil.make_archive(Path(path), "zip", Path(path))
    shutil.rmtree(Path(path))


def download_zip_docs2(docs, path):
    Path(path).mkdir(
        parents=True, exist_ok=True)
    for doc in docs:
        try:
            extrair_doc_arteria_pag(
                doc['id_arquivo'], Path(path), doc['scpjud'].replace(" ", "_"))
        except Exception as e:
            print(e)
    shutil.make_archive(Path(path), "zip", Path(path))
    shutil.rmtree(Path(path))


def download_pep(id_pagamento, file_name, scpjud=False, token=get_token()):
    if file_name == 'CAPA':
        templateId = '70'
    elif file_name == 'PEP':
        templateId = '55'
    if token:
        s = Session()
        # s.verify = False
        s.headers = {'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-MicrosoftAjax': 'Delta=true',
                    'sec-ch-ua-platform': '"Linux"',
                    'Accept': '*/*',
                    'Origin': 'https://arteria.costaesilvaadv.com.br',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9'}
        # s.verify = False
        s.cookies.update({"__ArcherSessionCookie__": token})
    reports = s.post(
        f'https://arteria.costaesilvaadv.com.br/RSAarcher/GenericContent/Record.aspx?id=5855645&moduleId=445&pr=&frameWidthHeight=1600,690')

    # soup = BeautifulSoup(reports.content, 'lxml')

    s.headers.update({
        'Referer': f'https://arteria.costaesilvaadv.com.br/RSAarcher/GenericContent/Record.aspx?id'
                f'={id_pagamento}&moduleId=445&pr=&frameWidthHeight=1600,690'})

    url_export = 'https://arteria.costaesilvaadv.com.br/RSAarcher/GenericContent/ExportReportCreation.aspx?contentId' \
                f'={id_pagamento}&levelId=242&exportSourceType=RecordView&exportType=Rtf&moduleName=Pagamento&templateId={templateId}' \
                '&layoutId=531&et=0'

    get_export = s.get(url_export)
    s.headers.update({'Referer': url_export})
    soup = BeautifulSoup(get_export.content, 'lxml')
    rs = soup.find('input', id='__RS').get('value')
    selectedcontent = soup.find('input', id="SelectedContentsForExport").get('name')
    s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
    # s.post(url_export, data=data)
    if selectedcontent == "SelectedContentsForExport":
        data = f"scriptManager=ExportReportUpdatePanel%7CExportReportUpdatePanel&__RS={rs}&scriptManager_TSM=&__EVENTTARGET=ExportReportUpdatePanel&__EVENTARGUMENT=&__VIEWSTATE=&SelectedContentsForExport=&radwinman_ClientState=&__ASYNCPOST=true&"
    else:
        data = f"ctl00$DefaultContent$scriptManager=ctl00$DefaultContent$ExportReportUpdatePanel|ExportReportUpdatePanel&__RS={rs}&scriptManager_TSM=&__EVENTTARGET=ExportReportUpdatePanel&__EVENTARGUMENT=&__VIEWSTATE=&{selectedcontent}=&ctl00_DefaultContent_radwinman_ClientState=&__ASYNCPOST=true&"

    status = s.post(url_export, data=data)
    retorno = BeautifulSoup(status.content, 'lxml')
    retorno.find('Exportação concluída')
    cont_time = 0
    while 'DownloadLink' not in status.text and 'Aguarde' in status.text:
        status = s.post(url_export, data=data)
        if cont_time == 15:
            raise Exception('Falha ao tentar realiar o download da Capa ou do Pep, favor tentar novamente.')
        sleep(5)
        cont_time += 1

    soup = BeautifulSoup(status.content, 'lxml')
    download_url = f"https://arteria.costaesilvaadv.com.br/RSAarcher{soup.find('a', href=re.compile('(.*)fileId=(.*)')).attrs['href'].lstrip('.')} "
    file = s.get(download_url)
    if file.headers.get('Content-Disposition'):
        if scpjud:
            return [unquote(file.headers.get('Content-Disposition')).split('filename=')[-1], file.content]

    extension = file.headers['content-disposition'].split('.')[-1]
    file_name = file_name + '.' + extension
    open(f"documento\\{id_pagamento}\\" + file_name, 'wb').write(file.content)
    return f"documento\\{id_pagamento}\\{file_name}"


def text_ocr(id_arquivo):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'api-key': '8cb99ca8-9e55-11ed-a8fc-0242ac120002'
    }

    data = {
        'id': f'{id_arquivo}',
    }

    response = requests.post('http://187.32.116.183:9000/extract_text', headers=headers, json=data).json()
    try:
        ocr_text = "\n\n\n".join(json.loads(response['ocr_text']))
        text_pdf = "\n\n\n".join(json.loads(response['pdf_text']))
    except Exception as e:
        ''
    return f'ocr_text : {ocr_text}, pdf_text : {text_pdf}'


def convert_doc_to_pdf(doc):
    convert(doc)
    os.remove(doc)


def remover_acentos_espacos_pontos_tracos_e_barras(txt):
    return normalize("NFKD",
                    txt.replace(" ", "").replace("&", "E").replace(".", "").replace("-", "").replace("/", "").replace(
                        ",", "")).encode("ASCII", "ignore").decode("ASCII").upper()


def close_excel():
    try:
        os.system('TASKKILL /F /IM excel.exe')
    except Exception:
        print("KU")


def texto_honorario_para_resumo_capa(tipo):
    if tipo == "CAIXA SEGURADORA S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE HONORÁRIOS ADVOCATÍCIOS EM PROCESSO DA SEGURADORA ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA VIDA E PREVIDÊNCIA S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE HONORÁRIOS ADVOCATÍCIOS EM PROCESSO DA VIDA E PREVIDÊNCIA ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA CAPITALIZAÇÃO S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE HONORÁRIOS ADVOCATÍCIOS EM PROCESSO DA CAPITALIZAÇÃO ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA CONSÓRCIOS S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE HONORÁRIOS ADVOCATÍCIOS EM PROCESSO DO CONSÓRCIO ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA SEGURADORA ESPECIALIZADA EM SAÚDE":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE HONORÁRIOS ADVOCATÍCIOS EM PROCESSO DA SEGURADORA ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "XS2 VIDA & PREVIDENCIA S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE HONORÁRIOS ADVOCATÍCIOS EM PROCESSO DA XS2 VIDA E PREVIDÊNCIA " \
            "ABAIXO RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "


def texto_reembolso_para_resumo_capa(tipo):
    if tipo == "CAIXA SEGURADORA S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE REEMBOLSO EM PROCESSO DA SEGURADORA ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA VIDA E PREVIDÊNCIA S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE REEMBOLSO EM PROCESSO DA VIDA E PREVIDÊNCIA ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA CAPITALIZAÇÃO S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE REEMBOLSO EM PROCESSO DA CAPITALIZAÇÃO ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA CONSÓRCIOS S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE REEMBOLSO EM PROCESSO DO CONSÓRCIO ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "CAIXA SEGURADORA ESPECIALIZADA EM SAÚDE":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE REEMBOLSO EM PROCESSO DA SEGURADORA ABAIXO " \
            "RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
    if tipo == "XS2 VIDA & PREVIDENCIA S/A":
        return "RESUMO: REFERE-SE AO PAGAMENTO DE REEMBOLSO EM PROCESSO DA XS2 VIDA E PREVIDÊNCIA " \
            "ABAIXO RELACIONADO, DE INTERESSE DAS EMPRESAS DO GRUPO CAIXA SEGUROS. "
