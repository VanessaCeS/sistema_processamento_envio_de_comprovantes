from rich import print
from PyPDF2 import PdfReader
from auxiliares import alterar_nome_pdf, data_corrente_formatada, deletar_arquivos_pdf, leitura_pdf, remover_acentos
from funcoes_arteria import adjust_date_to_arteria, enviar_comprovante_arteria, enviar_folha_pagamento_arteria
from leitura_relatorio_arteria import get_dados_ficha_cadastral, search_xml

dados = get_dados_ficha_cadastral(search_xml)

def dividir_e_renomear_pdf_comprovante(arquivos=None, mes_referencia=None):
  for arquivo in arquivos:
    with open(arquivo, 'rb') as arquivo_pdf:
      leitor_pdf = PdfReader(arquivo_pdf)
      for page_num in range(len(leitor_pdf.pages)):
        leitor_pdf, page_num,  nome, agencia, conta_corrente = leitura_pdf("comprovante", leitor_pdf, page_num)
        novo_nome, mes_arteria = alterar_nome_pdf(leitor_pdf, page_num, mes_referencia, nome, "comprovante")
        mes_arteria = "MAIO/2024"
        for dado in dados:
          if dado["Contracheque e RPA"] and dado["Nome bancário"] == nome:
            for d in dado["Contracheque e RPA"]:
              numero_conta = ''.join(filter(str.isdigit, dado['Nº da Conta'].split(':')[-1].strip()))
              if 'Mês de Referência' in d:
                if d['Mês de Referência'][0] == mes_arteria and d['Mês de Referência']:
                  if numero_conta == conta_corrente and dado['Agência'] == agencia:
                                      id = d['id']
                                      enviar_comprovante_arteria(novo_nome, mes_arteria, dado['ID do Sistema - Ficha Cadastral'], id)
              elif 'Mês de Referência' in d[0] and d[0]['Mês de Referência']:
                  if  d[0]['Mês de Referência'][0] == mes_arteria:
                    if numero_conta == conta_corrente and dado['Agência'] == agencia:
                      id = d[0]['id']
                      enviar_comprovante_arteria(novo_nome, mes_arteria, dado['ID do Sistema - Ficha Cadastral'], id)
                      

# dividir_e_renomear_pdf_comprovante(["pdfs/bklcom (94).pdf"], "2024-06-06")
deletar_arquivos_pdf()