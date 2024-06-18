from rich import print
from PyPDF2 import PdfReader
from auxiliares import alterar_nome_pdf, data_corrente_formatada, leitura_pdf, remover_acentos
from funcoes_arteria import adjust_date_to_arteria, enviar_comprovante_arteria, enviar_folha_pagamento_arteria
from leitura_relatorio_arteria import get_dados_ficha_cadastral, search_xml

dados = get_dados_ficha_cadastral(search_xml)

def dividir_e_renomear_pdf_comprovante(arquivos=None, mes_referencia=None):
  for arquivo in arquivos:
    with open(arquivo, 'rb') as arquivo_pdf:
      leitor_pdf = PdfReader(arquivo_pdf)
      for page_num in range(len(leitor_pdf.pages)):
        leitor_pdf, page_num,  nome, agencia, conta_corrente = leitura_pdf("comprovante", leitor_pdf, page_num)
        novo_nome, _ = alterar_nome_pdf(leitor_pdf, page_num, mes_referencia, nome, "comprovante")
        for dado in dados:
          if dado["Nome bancário"] == nome:
            numero_conta = ''.join(filter(str.isdigit, dado['Nº da Conta'].split(':')[-1].strip()))
          
            if numero_conta == conta_corrente and dado['Agência'] == agencia:
              print(dado['ID do Sistema - Ficha Cadastral'])
              enviar_comprovante_arteria(novo_nome, dado['ID do Sistema - Ficha Cadastral'])

