import traceback
from rich import print
from PyPDF2 import PdfReader
from funcoes_arteria import enviar_comprovante_arteria
from auxiliares import alterar_nome_pdf, deletar_arquivos_pdf, leitura_pdf
from leitura_relatorio_arteria import get_dados_ficha_cadastral, search_xml

dados = get_dados_ficha_cadastral(search_xml)

def dividir_e_renomear_pdf_comprovante(arquivos, mes_referencia):
  erros = []
  for arquivo in arquivos:
    with open(arquivo, 'rb') as arquivo_pdf:
      leitor_pdf = PdfReader(arquivo_pdf)
      for page_num in range(len(leitor_pdf.pages)):
        leitor_pdf, page_num, nome, agencia, conta_corrente = leitura_pdf("comprovante", leitor_pdf, page_num)
        novo_nome, mes_arteria = alterar_nome_pdf(leitor_pdf, page_num, mes_referencia, nome, "comprovante")
        for dado in dados:
          try:
            if dado["Contracheque e RPA"]:
              if dado["Nome bancário"] == nome:
                for d in dado["Contracheque e RPA"]:
                  numero_conta = ''.join(filter(str.isdigit, dado['Nº da Conta'].split(':')[-1].strip()))
                  if 'Mês de Referência' in d:
                    if d['Mês de Referência'][0] == mes_arteria and d['Mês de Referência']:
                      if numero_conta == conta_corrente and dado['Agência'] == agencia:
                        enviar_comprovante_arteria(novo_nome, dado['ID do Sistema - Ficha Cadastral'], d['id'])
                      else:
                        erros.append(f"{dado['Nome']} - Número da agência ou conta não estão corretos")
                    else:
                      erros.append(f"{dado['Nome']} - Não há mês correspondente no arteria")
                  elif 'Mês de Referência' in d[0] and d[0]['Mês de Referência']:
                      if  d[0]['Mês de Referência'][0] == mes_arteria:
                        if numero_conta == conta_corrente and dado['Agência'] == agencia:
                          enviar_comprovante_arteria(novo_nome, dado['ID do Sistema - Ficha Cadastral'], d[0]['id'])
                        else:
                          erros.append(f"{dado['Nome']} - Número da agência ou conta não estão corretos")
                      else:
                        erros.append(f"{dado['Nome']} - Não há mês correspondente no arteria")
              else:
                erros.append(f"{dado['Nome']} - Nome Bancário no arteria diverge o comprovante")
          except Exception as e:
            print(f"[red]Erro -->>{e}")
            print(traceback.print_exc())
    
  deletar_arquivos_pdf()
  if erros:
      erros.append("Os outros dados foram salvos normalmente!")
      return erros, "#ff0000"
  else:
      return ["Comprovantes anexados com sucesso!"], "#32965D"
  
  
