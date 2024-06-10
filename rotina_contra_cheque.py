from PyPDF2 import PdfWriter, PdfReader
from leitura_relatorio_arteria import get_dados_ficha_cadastral, search_xml
from funcoes_arteria import adjust_date_to_arteria, enviar_folha_pagamento_arteria
from auxiliares import converter_string_mes, data_corrente_formatada, deletar_arquivos_pdf, encontrar_indice_linha, remover_acentos

dados = get_dados_ficha_cadastral(search_xml)

def dividir_e_renomear_pdf_contra_cheque(caminho_pdf, mes_referencia):
    with open(caminho_pdf, 'rb') as arquivo_pdf:
        leitor_pdf = PdfReader(arquivo_pdf)
        for page_num in range(len(leitor_pdf.pages)):
            page = leitor_pdf.pages[page_num]
            text = page.extract_text()
            with open(f'arquivos_txt/contra_cheque_{page_num}.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            nome, documento= ler_extrair_dados_txt(f'arquivos_txt/contra_cheque_{page_num}.txt')
            escritor_pdf = PdfWriter()
            escritor_pdf.add_page(leitor_pdf.pages[page_num])
            mes_arteria = converter_string_mes(mes_referencia)
            
            novo_nome = f"{nome} - {mes_arteria.replace('/', ' ')}.pdf"
            with open(novo_nome, 'wb') as novo_arquivo:
                escritor_pdf.write(novo_arquivo)
            for dado in dados:
                if remover_acentos(dado['Nome']) == nome and dado['CPF \\ CNPJ'].replace('.','').replace('-','').strip() == documento:
                    data_upload = data_corrente_formatada()
                    data_upload = adjust_date_to_arteria(data_upload)
                    enviar_folha_pagamento_arteria(novo_nome, mes_arteria, dado['ID do Sistema - Ficha Cadastral'], data_upload)
    deletar_arquivos_pdf()        

def ler_extrair_dados_txt(arquivo_txt):
    with open(arquivo_txt, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    indice_nome = encontrar_indice_linha(linhas, 'CÓDIGO:')
    indice_documento = encontrar_indice_linha(linhas, 'NÍVEL:')
    nome = linhas[indice_nome].split(' ', 2)[2].replace('\n', '').strip()
    documento = linhas[indice_documento].split(':',2)[1].replace('CPF', '').replace('.','').replace('-','').strip()

    return nome, documento
