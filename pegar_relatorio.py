from funcoes_arteria import search

search_xml = """<SearchReport id="16119" name="rel_ficha_cadastral">
  <DisplayFields>
    <DisplayField name="Nome">17963</DisplayField>
    <DisplayField name="CPF \ CNPJ">17976</DisplayField>
    <DisplayField name="ID de rastreamento">17960</DisplayField>
    <DisplayField name="ID do Sistema - Ficha Cadastral">22104</DisplayField>
    <DisplayField name="Processo Seletivo">18011</DisplayField>
    <DisplayField name="Contar Recibo">24730</DisplayField>
    <DisplayField name="Mês Referencia - Recibo">26213</DisplayField>
    <DisplayField name="Atualização Recibo">24733</DisplayField>
    <DisplayField name="Status Contratação">18050</DisplayField>
  </DisplayFields>
  <PageSize>1500</PageSize>
  <IsResultLimitPercent>False</IsResultLimitPercent>
  <Criteria>
    <Keywords />
    <Filter>
      <OperatorLogic />
      <Conditions>
        <ValueListFilterCondition>
          <Field name="Status Contratação">18050</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value name="Contratado">71001</Value>
          </Values>
        </ValueListFilterCondition>
      </Conditions>
    </Filter>
    <ModuleCriteria>
      <Module name="Ficha Cadastral">464</Module>
      <IsKeywordModule>True</IsKeywordModule>
      <BuildoutRelationship>Union</BuildoutRelationship>
      <SortFields>
        <SortField>
          <Field name="Nome">17963</Field>
          <SortType>Ascending</SortType>
        </SortField>
        <SortField>
          <Field name="Atualização Recibo">24733</Field>
          <SortType>Ascending</SortType>
        </SortField>
      </SortFields>
    </ModuleCriteria>
  </Criteria>
</SearchReport>
"""

def get_dados_ficha_cadastral(search_xml):
    dados = search(search_xml, page=1, quantidade=False)
    # for i in range(len(dados)):
    #     print(dados[i]['Nome'])
    #     nomes = f" {dados[i]['Nome']} ,"
    #     with open(f"nomes.txt", "a", encoding='utf-8') as arquivo:
    #         arquivo.write(nomes)
    return dados

get_dados_ficha_cadastral(search_xml)
