import os
from datetime import datetime

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
    '01': 'Janeiro',
    '02': 'Fevereiro',
    '03': 'Março',
    '4': 'Abril',
    '05': 'Maio',
    '06': 'Junho',
    '07': 'Julho',
    '08': 'Agosto',
    '09': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
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
    diretorio_pdf = 'sistema_processamento_envio_de_comprovantes'
    diretorio_txt = 'sistema_processamento_envio_de_comprovantes' + '/arquivos_txt'
    diretorios = [diretorio_pdf, diretorio_txt]
    for diretorio in diretorios:
      arquivos = os.listdir(diretorio)
      for arquivo in arquivos:
          if arquivo.endswith((".pdf", ".txt")):
              caminho_arquivo = os.path.join(diretorio, arquivo)
              os.remove(caminho_arquivo)
