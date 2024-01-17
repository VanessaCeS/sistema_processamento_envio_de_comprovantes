from auxiliares import remover_acentos
from funcoes_arteria import search

search_xml = """<SearchReport id="17093" name="rel_ficha_cadastral">
  <DisplayFields>
    <DisplayField>17963</DisplayField>
    <DisplayField>17976</DisplayField>
    <DisplayField>17960</DisplayField>
    <DisplayField>22104</DisplayField>
  </DisplayFields>
  <PageSize>15000</PageSize>
  <IsResultLimitPercent>False</IsResultLimitPercent>
  <Criteria>
    <Keywords />
    <Filter>
      <OperatorLogic />
      <Conditions>
        <ValueListFilterCondition>
          <Field>18050</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value>71001</Value>
          </Values>
        </ValueListFilterCondition>
      </Conditions>
    </Filter>
    <ModuleCriteria>
      <Module>464</Module>
      <IsKeywordModule>True</IsKeywordModule>
      <BuildoutRelationship>Union</BuildoutRelationship>
      <SortFields>
        <SortField>
          <Field>17963</Field>
          <SortType>Ascending</SortType>
        </SortField>
      </SortFields>
    </ModuleCriteria>
  </Criteria>
</SearchReport>
"""

def get_dados_ficha_cadastral(search_xml):
    dados = search(search_xml)
    return dados

