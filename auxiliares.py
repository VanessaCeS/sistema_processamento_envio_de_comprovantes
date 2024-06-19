import os
from datetime import datetime
from PyPDF2 import  PdfWriter
from unidecode import unidecode

def remover_acentos(texto):
    return unidecode(texto).replace('  ', ' ')

def encontrar_indice_linha(linhas, texto):
  for indice, linha in enumerate(linhas):
    if texto in linha.upper().replace('  ', ' ').replace('\xa0\n',' '):
        return indice
  return None

def encontrar_indices_linha(linhas, texto):
  indices = []
  for indice, linha in enumerate(linhas):
    if texto.upper() in linha.upper().replace('  ', ' '):
        indices.append(indice)
  return indices

def converter_string_mes(string):
  if string:
    dividir_string = string.split('-')
    nome_mes = dividir_string[1]
    ano = dividir_string[0]
    dict_meses = {
    '01': 'JANEIRO',
    '02': 'FEVEREIRO',
    '03': 'MARÇO',
    '4': 'ABRIL',
    '05': 'MAIO',
    '06': 'JUNHO',
    '07': 'JULHO',
    '08': 'AGOSTO',
    '09': 'SETEMBRO',
    '10': 'OUTUBRO',
    '11': 'NOVERMBRO',
    '12': 'DEZEMBRO'
}
    for m in dict.keys(dict_meses):
      if m in nome_mes:
        mes = dict_meses[m].upper()
    return f'{mes}/{ano}'
  else: 
    return None
  
def formatar_data_padra_arteria(data):
  ano, mes, dia = data.strip().split('-')
  data_padrao_arteria = f"{mes}/{dia}/{ano}"
  return data_padrao_arteria

def data_corrente_formatada():
    data_atual = datetime.now()
    data_formatada = data_atual.strftime("%d/%m/%Y")
    return data_formatada

def deletar_arquivos_pdf():
    diretorio_pdf = os.getenv("diretorio_comprovantes")
    diretorio_txt = os.getenv("diretorio_comprovantes") + '/txts'
    # diretorio_pdfs = os.getenv("diretorio_comprovantes") + '/pdfs'
    
    diretorios = [diretorio_pdf, diretorio_txt]
    for diretorio in diretorios:
      arquivos = os.listdir(diretorio)
      for arquivo in arquivos:
          if arquivo.endswith((".pdf", ".txt")):
              caminho_arquivo = os.path.join(diretorio, arquivo)
              os.remove(caminho_arquivo)

def leitura_pdf(tipo, leitor_pdf, page_num):
  page = leitor_pdf.pages[page_num]
  text = page.extract_text()
  with open(f'txts/{tipo}_{page_num}.txt', 'w', encoding='utf-8') as f:
    f.write(text)
  if tipo == "rpas":
    nome, documento = page_num, ler_extrair_dados_txt_rpa(f'txts/{tipo}_{page_num}.txt')
    return leitor_pdf, nome, documento
  elif tipo == "contra_cheque":
    nome, documento = ler_extrair_dados_txt_cc(f'txts/{tipo}_{page_num}.txt')
    return leitor_pdf, page_num, nome, documento 
  elif tipo == "comprovante":
    nome, agencia, conta_corrente = ler_extrair_dados_txt_comprovante(f'txts/{tipo}_{page_num}.txt') 
    return leitor_pdf, page_num, nome, agencia, conta_corrente



def alterar_nome_pdf(leitor_pdf, page_num, mes_referencia, nome, tipo=None):  
  escritor_pdf = PdfWriter()
  escritor_pdf.add_page(leitor_pdf.pages[page_num])
  mes_arteria = converter_string_mes(mes_referencia)
  novo_nome = f"Comprovante de pagamento {nome} - conta salario.pdf" if tipo == "comprovante" else f"{nome} - {mes_arteria.replace('/', ' ')}.pdf"
  with open(novo_nome, 'wb') as novo_arquivo:
      escritor_pdf.write(novo_arquivo)

  return novo_nome, mes_arteria

def ler_extrair_dados_txt_rpa(arquivo_txt):
  with open(arquivo_txt, 'r', encoding='utf-8') as f:
    linhas = f.readlines()
  indice_nome = encontrar_indice_linha(linhas, 'VALOR LÍQUIDO:')
  indice_documento = encontrar_indice_linha(linhas, 'CPF:')
  nome = linhas[indice_nome + 1].split(' ', 1)[1].replace('\n', '').strip()
  documento = linhas[indice_documento].split(':')[1].strip()
  return nome, documento

def ler_extrair_dados_txt_cc(arquivo_txt):
  with open(arquivo_txt, 'r', encoding='utf-8') as f:
    linhas = f.readlines()
  indice_nome = encontrar_indice_linha(linhas, 'CÓDIGO:')
  indice_documento = encontrar_indice_linha(linhas, 'NÍVEL:')
  nome = linhas[indice_nome].split(' ', 2)[2].replace('\n', '').strip()
  documento = linhas[indice_documento].split(':',2)[1].replace('CPF', '').replace('.','').replace('-','').strip()
  return nome, documento

def ler_extrair_dados_txt_comprovante(arquivo_txt):
  with open(arquivo_txt, 'r', encoding='utf-8') as f:
      linhas = f.readlines()
  indice_nome = encontrar_indice_linha(linhas, 'NOME:')
  indice_agencia_conta = encontrar_indices_linha(linhas, "AGÊNCIA")
  nome = linhas[indice_nome].split(":")[1].strip()
  agencia = linhas[indice_agencia_conta[-1]].split(':')[1].replace("Conta corrente", "").strip()
  conta_corrente = ''.join(filter(str.isdigit, linhas[indice_agencia_conta[-1]].split(':')[-1].strip()))
  return nome, agencia, conta_corrente
