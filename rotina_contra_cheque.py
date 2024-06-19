from PyPDF2 import  PdfReader
from leitura_relatorio_arteria import get_dados_ficha_cadastral, search_xml
from funcoes_arteria import adjust_date_to_arteria, enviar_folha_pagamento_arteria
from auxiliares import alterar_nome_pdf, data_corrente_formatada, deletar_arquivos_pdf, leitura_pdf, remover_acentos

dados = get_dados_ficha_cadastral(search_xml)

def dividir_e_renomear_pdf_contra_cheque(caminho_pdf, mes_referencia):
    with open(caminho_pdf, 'rb') as arquivo_pdf:
        leitor_pdf = PdfReader(arquivo_pdf)
        for page_num in range(len(leitor_pdf.pages)):
            leitor_pdf, page_num,  nome, documento = leitura_pdf("contra_cheque", leitor_pdf, page_num)
            novo_nome, mes_arteria = alterar_nome_pdf(leitor_pdf, page_num, mes_referencia, nome)

            for dado in dados:
                if remover_acentos(dado['Nome']) == nome and dado['CPF \\ CNPJ'].replace('.','').replace('-','').strip() == documento:
                    data_upload = data_corrente_formatada()
                    data_upload = adjust_date_to_arteria(data_upload)
                    enviar_folha_pagamento_arteria(novo_nome, mes_arteria, dado['ID do Sistema - Ficha Cadastral'], data_upload)
    deletar_arquivos_pdf()       
    return ["Contra cheques anexadas com sucesso!"], "#32965D" 