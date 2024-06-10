import os
from datetime import datetime
from unidecode import unidecode

def remover_acentos(texto):
    return unidecode(texto).replace('  ', ' ')

def encontrar_indice_linha(linhas, texto):
  for indice, linha in enumerate(linhas):
    if texto in linha.upper().replace('  ', ' ').replace('\xa0\n',' '):
        return indice
  return None

def converter_string_mes(string):
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
    diretorio_txt = os.getenv("diretorio_comprovantes") + '/arquivos_txt'
    diretorio_pdfs = os.getenv("diretorio_comprovantes") + '/pdfs'
    
    diretorios = [diretorio_pdf, diretorio_txt, diretorio_pdfs]
    for diretorio in diretorios:
      arquivos = os.listdir(diretorio)
      for arquivo in arquivos:
          if arquivo.endswith((".pdf", ".txt")):
              caminho_arquivo = os.path.join(diretorio, arquivo)
              os.remove(caminho_arquivo)

