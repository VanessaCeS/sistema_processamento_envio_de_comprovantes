from PyPDF2 import PdfWriter, PdfReader
from leitura_relatorio_arteria import get_dados_ficha_cadastral, search_xml
from funcoes_arteria import adjust_date_to_arteria, enviar_folha_pagamento_arteria
from auxiliares import alterar_nome_pdf, converter_string_mes, data_corrente_formatada, deletar_arquivos_pdf, encontrar_indice_linha, leitura_pdf, remover_acentos, verificar_tipo_arquivo
dados = get_dados_ficha_cadastral(search_xml)

def dividir_e_renomear_pdf_rpas(arquivos, mes_referencia):
    erros = []
    for arquivo in arquivos:
        with open(arquivos, 'rb') as arquivo_pdf:
            leitor_pdf = PdfReader(arquivo_pdf)
        for page_num in range(len(leitor_pdf.pages)):
            leitor_pdf, page_num,  nome, documento, arq_txt = leitura_pdf("rpas", leitor_pdf, page_num)
            if verificar_tipo_arquivo(arq_txt, 'RECIBO DE PAGAMENTO A AUTÔNOMO - RPA'):
                novo_nome, mes_arteria = alterar_nome_pdf(leitor_pdf, page_num, mes_referencia, nome)
                for dado in dados:
                    if remover_acentos(dado['Nome']) == nome and dado['CPF \\ CNPJ'] == documento:
                        data_upload = data_corrente_formatada()
                        data_upload = adjust_date_to_arteria(data_upload)
                        enviar_folha_pagamento_arteria(novo_nome, mes_arteria, dado['ID do Sistema - Ficha Cadastral'], data_upload)
            else:
                erros.append(f"{arquivo} não é do tipo RPA")
    deletar_arquivos_pdf()       

    return erros, "#ff0000" if erros else ["RPAs anexadas com sucesso!"], "#32965D"
