import os
import re
import PyPDF2
from pegar_relatorio import get_dados_ficha_cadastral, search_xml

# nomes_funcionario = get_dados_ficha_cadastral(search_xml)
# nomes = []
# for n in nomes_funcionario:
#     nomes.append(n['Nome'])



def principal(nome_arquivo, data_arquivo, tipo):
    if not os.path.exists('novos_pdfs'):
        os.makedirs('novos_pdfs')
    if not os.path.exists('arquivos_txt_contra_cheques'):
        os.makedirs('arquivos_txt_contra_cheques')

    nome_arquivo_pdf = 'C:\\Users\\Costa e Silva\\Downloads\\CONTRA CHEQUE - fevereiro.pdf'
    # nome_arquivo_pdf = 'C:\\Users\\Costa e Silva\\Downloads\\RPAS - janeiro.pdf'

    # pdf_file = open(nome_arquivo_pdf, 'rb')
    pdf_file = open(nome_arquivo, 'rb')

    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    for pagina_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(pagina_num)
        page_text = page.extractText()
        with open(f"arquivos_txt/extrair_{pagina_num}.txt", "w", encoding='utf-8') as arquivo:
            arquivo.write(page_text)
        
        if tipo == 'contra_cheque':
            dados = ler_contra_cheque(f"arquivos_txt/extrair_{pagina_num}.txt")
            nome = dados['Nome']
            cpf = dados['CPF']
            data_arquivo = '08-2023'
            print("NOme", nome)
            if nome != '' or cpf != '' or data_arquivo != '':
                novo_nome_arquivo_pdf = f"novos_pdfs/{cpf}_{nome}_{data_arquivo}.pdf"
                pdf_writer = PyPDF2.PdfFileWriter()
                pdf_writer.addPage(page)
                with open(novo_nome_arquivo_pdf, 'wb') as novo_pdf_file:
                    pdf_writer.write(novo_pdf_file)
            else: 
                pass
        else:

            dados = ler_arquivo_pdf(f"arquivos_txt/extrair_{pagina_num}.txt")
            cpf = dados['CPF']
            nome = dados['Nome']
            data_arquivo = '08-2023'
            if nome != '' or cpf != ''or data_arquivo != '':
                novo_nome_arquivo_pdf = f"novos_pdfs/{cpf}_{nome}_{data_arquivo}.pdf"
                pdf_writer = PyPDF2.PdfFileWriter()
                pdf_writer.addPage(page)
                with open(novo_nome_arquivo_pdf, 'wb') as novo_pdf_file:
                        pdf_writer.write(novo_pdf_file)
            else: 
                pass

    pdf_file.close()
    apagar_arquivos_txt()
    apagar_arquivos_pdfs()


def ler_arquivo_pdf(arquivo_txt):
    with open(arquivo_txt, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()
    indices_nome = [indice for indice, linha in enumerate(linhas) if "VALOR LÍQUIDO" in linha]
    print("nome --> ", indices_nome)
    indices_cpf = [indice for indice, linha in enumerate(linhas) if "CPF:" in linha]

    for indice_valor, indice_cpf in zip(indices_nome, indices_cpf):
        padrao = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
        cpf = re.search(padrao, linhas[indice_cpf]).group(0)
        nome = pegar_nome(linhas[indice_valor + 1].strip())
        break
    return {'CPF': cpf, 'Nome': nome}

def pegar_nome(dado):
    padrao = r'\d{1,8},\d{2} (.*)'
    correspondencia = re.search(padrao, dado)
    nome = correspondencia.group(1)
    if nome.upper() not in nomes:
        return ''
    else:
        return nome

def ler_contra_cheque(arquivo_txt):
    with open(arquivo_txt, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()
    indices_nome = [indice for indice, linha in enumerate(linhas) if "Código" in linha]
    indices_cpf = [indice for indice, linha in enumerate(linhas) if "Nível:" in linha]

    for indice_valor, indice_cpf in zip(indices_nome, indices_cpf):
        linha_cpf = linhas[indice_cpf].strip()
        padrao = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
        cpf = re.search(padrao, linha_cpf).group(0)
        cpf_formatado = re.sub(r'[.-]', '', cpf)
        nome = pegar_nome_contra_cheque(linhas[indice_valor].strip())
        nome_formatado = nome.replace(" ", "_")
        break

    return {"Nome": nome_formatado, 'CPF': cpf_formatado}
    
def pegar_nome_contra_cheque(dado):
    string = dado
    padrao = r'Código: \d{4,8} (.*)'
    correspondencia = re.search(padrao, string)
    return correspondencia.group(1)
    

def apagar_arquivos_txt():
    pasta = './arquivos_txt'
    arquivos = os.listdir(pasta) 
    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo):  
            os.remove(caminho_arquivo)

def apagar_arquivos_pdfs():
    pasta = './novos_pdfs'
    arquivos = os.listdir(pasta) 
    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo):  
            os.remove(caminho_arquivo)

principal('contra_cheque')

