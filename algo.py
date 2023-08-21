from extrair import principal
from pegar_relatorio import get_dados_ficha_cadastral


def buscar_dados():
    dados = get_dados_ficha_cadastral()
    if dados:
      for dado in dados:
        analisar_documentos(dado)

def analisar_documentos(dado):
   funcionarios_ativos = 'nomes.txt'
   principal()