import base64
import os
import re
import json
import math
import util
import datetime
import requests
import xmltodict
from rich import print
from time import  time
from requests import Session
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from zeep import Client, Settings, Transport
from concurrent.futures import ThreadPoolExecutor
from rsa_archer.archer_instance import ArcherInstance



load_dotenv('.env')

def adjust_date_and_time_to_arteria(date_audiencia, formato="%d/%m/%Y %H:%M"):
    given_date = datetime.datetime.strptime(date_audiencia, formato)
    final_date = given_date + datetime.timedelta(hours=3)
    return final_date.strftime("%m/%d/%Y %H:%M")


def adjust_date_to_arteria(date_audiencia, formato="%d/%m/%Y"):
    given_date = datetime.datetime.strptime(date_audiencia, formato)
    return given_date.strftime("%m/%d/%Y")


def instancia_arteria(application="", user=None, password=None):
    if 'archer_instance' not in globals():
        load_dotenv('.env')
        AMBIENTE = 'PROD_ARTERIA'#os.getenv('AMBIENTE')
        user = user if user else os.getenv(f'USER_{AMBIENTE}')
        password = password if password else os.getenv(f'PASSWORD_{AMBIENTE}')
        global archer_instance
        archer_instance = ArcherInstance("https://arteria.costaesilvaadv.com.br", "Produção", user, password)
    if application:
        archer_instance.from_application(application)
    archer_instance.application_level_id = 261
    return archer_instance

def busca_todos_campos_app(app):
    campos = instancia_arteria(app).application_fields_json
    todos_campos = campos.copy()
    for campo in campos.keys():
        if not isinstance(campo, str):
            todos_campos.pop(campo)
    return todos_campos


def cadastrar_audiencia_arteria(dados_precadastro, app, id_arteria=None, audiencia_archer_instance=None):
    if not audiencia_archer_instance:
        audiencia_archer_instance = instancia_arteria(app)
    campos = []
    for key in dados_precadastro.keys():
        if key not in archer_instance.application_fields_json.keys():
            campos.append(key)
    if campos:
        raise Exception(f"Campos {campos} não existem na aplicação {app}")
    if id_arteria:
        return archer_instance.update_content_record(dados_precadastro, id_arteria)
    else:
        return archer_instance.create_content_record(dados_precadastro)


def cadastrar_arteria(dados_precadastro, app, id_arteria=None, archer_instance=None):
    if not archer_instance:
        archer_instance = instancia_arteria(app)
    campos = []
    for key in dados_precadastro.keys():
        if key not in archer_instance.application_fields_json.keys():
            campos.append(key)
    if campos:
        raise Exception(f"Campos {campos} não existem na aplicação {app}")
    if id_arteria:
        return archer_instance.update_content_record(dados_precadastro, id_arteria)
    else:
        return archer_instance.create_content_record(dados_precadastro)


def teste333(dados, app, archer_instance=None):
    if not archer_instance:
        archer_instance = instancia_arteria(app)
    return archer_instance.create_content_record(dados)


def update_subform(dados, app, subf_field_name, record_id):

    archer_instance = instancia_arteria(app)
    return archer_instance.update_sub_record(dados, subf_field_name, record_id)


def avanca_etapa_wf(id_arteria, etapa, app):
    archer_instance = instancia_arteria(app)
    current_action = archer_instance.get_workflow_action(id_arteria)
    if current_action:
        for workflow in current_action['Actions']:
            if etapa in workflow['WorkflowTransitionName']:
                completion_code = workflow['CompletionCode']

        return archer_instance.save_workflow_action(id_arteria, current_action['WorkflowNodeId'], completion_code)


def get_record(id_arteria, fields=None):
    record_data = archer_instance.get_record(id_arteria, fields)
    # for field in record_data.json['FieldContents'].values():
    #     if 'ValuesListIds' in field['Value']:
    #         field_options = archer_instance.get_field_options('Etapa')
    #         field_options_inversed = {v: k for k, v in field_options.items()}
    #         field['Value']['ValuesListIds'] = [{x: field_options_inversed[x]} for x in field['Value']['ValuesListIds']]
    return record_data

def get_sub_record(id_arteria, sub_record_name):
    record_data = archer_instance.get_sub_record(id_arteria, sub_record_name)
    return record_data

def get_field_options(app, campo):
    archer_instance = instancia_arteria(app)
    return archer_instance.get_field_options(campo)


def cadastrar_e_vincular_subf(dados, app, subf_field_name, record_id):
    #archer_instance = instancia_arteria(app)
    record_exists = archer_instance.get_record(record_id)
    if record_exists:
        created = archer_instance.create_sub_record(dados, subf_field_name)
        if created:
            print(created)
            record = archer_instance.get_record(record_id)
            current_sub_records_ids = record.get_field_content(subf_field_name)
            if current_sub_records_ids:
                current_sub_records_ids.append(created)
                vinculo = archer_instance.update_content_record({subf_field_name: current_sub_records_ids}, record_id)
            else:
                vinculo = archer_instance.update_content_record({subf_field_name: [created]}, record_id)
            if vinculo:
                return created
            else:
                raise Exception('Não foi possível vincular o subformulário')
        else:
            raise Exception('Não foi possível criar o subformulário')


def marcar_audiencia_agendada(record_id):
    load_dotenv('./.env')
    AMBIENTE = os.getenv('AMBIENTE')
    url_ambiente = os.getenv(f'URL_{AMBIENTE}')
    req_body = {
                "Content": {
                    "Id": record_id,
                    "LevelId": "243",
                    "FieldContents": {
                        "20031": {
                            "Type": 4,
                            "FieldId": 20031,
                            "Value": {
                                "ValuesListIds": [84363]
                            }
                        }
                    }
                }
            }
    req_header = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q =0.9,*/*;q=0.8",
        "Content-type": "application/json",
        "Authorization": "Archer session-id={0}".format(util.get_token(os.getenv(f'USER_{AMBIENTE}'), os.getenv(f'AMBIENTE_{AMBIENTE}')))}
    update_request = requests.put(url_ambiente + '/RSAarcher/api/core/content/', json=req_body, headers=req_header)
    if update_request.status_code == 200:
        return record_id


def testes_de_app(app):
    dado = archer_instance.find_grc_endpoint_url(app)
    print(dado)

############################################################################
# FUNÇOES NOVAS
############################################################################

def xml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    records = []
    for record in root.find('Metadata').find('Records'):
        record_dict = {}
        for field in record:
            record_dict[field.get('alias')] = field.text
        records.append(record_dict)
    return json.dumps({'records': records})


def old_extrai_dados(campos, dado):
    lista = {}
    for key in campos.values():
        if key['guid'] == dado['@guid']:
            if dado['@type'] in ['1', '2', '3', '6', '21', '22']:
                if '#text' in dado:
                    lista[key['alias']] = dado['#text']
                else:
                    lista[key['alias']] = ''
            elif dado['@type'] in ['4']:
                if 'ListValues' in dado:
                    lista[key['alias']] = {}
                    if 'ListValue' in dado['ListValues']:
                        if '@id' in dado['ListValues']['ListValue']:
                            lista[key['alias']][0] = {}
                            lista[key['alias']][0]['id'] = dado['ListValues']['ListValue']['@id']
                            lista[key['alias']][0]['displayName'] = dado['ListValues']['ListValue']['@displayName']
                        else:
                            h = 0
                            for m in dado['ListValues']['ListValue']:
                                lista[key['alias']][h] = {}
                                lista[key['alias']][h]['id'] = m['@id']
                                lista[key['alias']][h]['displayName'] = m['@displayName']
                                h += 1
                    else:
                        lista[key['alias']] = "ListValue com mais de um valor selecionando."
                        print("ListValue com mais de um valor selecionando.")
                else:
                    lista[key['alias']] = ''
            elif dado['@type'] in ['9', '23']:
                lista[key["alias"]] = {}
                if 'Reference' in dado:
                    if '@id' in dado['Reference']:
                        lista[key["alias"]][0] = {}
                        lista[key['alias']][0]['id'] = dado['Reference']['@id']
                        lista[key['alias']][0]['texto'] = dado['Reference']['#text']
                    else:
                        cont = 0
                        for ref in dado['Reference']:
                            if '@contentId' in ref:
                                lista[key['alias']][cont] = {}
                                lista[key['alias']][cont]['id'] = ref['@id']
                                lista[key['alias']][cont]['texto'] = ref['#text']
                                cont += 1
            elif dado['@type'] in ['11']:
                lista[key['alias']] = {}
                if 'File' in dado:
                    if '@id' in dado['File']:
                        lista[key["alias"]][0] = {}
                        lista[key['alias']][0]['id'] = dado['File']['@id']
                        lista[key['alias']][0]['nome'] = dado['File']['#text']
                    else:
                        cont = 0
                        for d in dado['File']:
                            if '@id' in d:
                                lista[key['alias']][cont] = {}
                                lista[key['alias']][cont]['id'] = d['@id']
                                lista[key['alias']][cont]['nome'] = d['#text']
                                cont += 1
                            else:
                                lista[key['alias']] = ''
            elif dado['@type'] in ['24']:
                lista[key["alias"]] = {}
                if 'Subform' in dado:
                    if '@contentId' in dado['Subform']:
                        lista[key["alias"]][0] = {}
                        lista[key['alias']][0]['id'] = dado['Subform']['@contentId']
                        if '#text' in dado['Subform']['Field']:
                            lista[key['alias']][0]['texto'] = dado['Subform']['Field']['#text']
                        else:
                            for b in dado['Subform']['Field']:
                                d = extrai_dados(campos, b)
                                for chave, valor in d.items():
                                    lista[key['alias']][0][chave] = valor
                    else:
                        cont = 0
                        for sub in dado['Subform']:
                            if '@contentId' in sub:
                                lista[key['alias']][cont] = {}
                                lista[key['alias']][cont]['id'] = sub['@contentId']
                                if '#text' in sub['Field']:
                                    lista[key['alias']][cont]['texto'] = sub['Field']['#text']
                                else:
                                    for b in sub['Field']:
                                        d = extrai_dados(campos, b)
                                        for chave, valor in d.items():
                                            lista[key['alias']][cont][chave] = valor
                                cont += 1
            elif dado['@type'] in ['8']:
                lista[key["alias"]] = {}
                if 'Users' in dado.keys():
                    lista[key["alias"]]['Users'] = []
                    if dado['Users']:
                        for user in dado['Users'].values():
                            lista[key["alias"]]['Users'].append(
                                {'id': user['@id'], 'firstName': user['@firstName'], 'middleName': user['@middleName'],
                                 'lastName': user['@lastName'], 'username': user['#text']})
                    lista[key["alias"]]['Users'] = dado['Users']
                if 'Groups' in dado.keys():
                    lista[key["alias"]]['Groups'] = []
                    if dado['Groups']:
                        for group in dado['Groups'].values():
                            if isinstance(group, dict):
                                group = [group]
                            for g in group:
                                lista[key["alias"]]['Groups'].append({'id': g['@id'], 'nome': g['#text']})

            else:
                print(dado['@type'])

            return lista


def old_extrai_dados(campos, dado):
    lista = {}
    for key in campos.values():
        if key['guid'] == dado['@guid']:
            if dado['@type'] in ['1', '2', '3', '6', '21', '22']:
                if '#text' in dado:
                    lista[key['alias']] = dado['#text']
                else:
                    lista[key['alias']] = ''
            elif dado['@type'] in ['4']:
                if 'ListValues' in dado:
                    lista[key['alias']] = {}
                    if 'ListValue' in dado['ListValues']:
                        if '@id' in dado['ListValues']['ListValue']:
                            lista[key['alias']][0] = {}
                            lista[key['alias']][0]['id'] = dado['ListValues']['ListValue']['@id']
                            lista[key['alias']][0]['displayName'] = dado['ListValues']['ListValue']['@displayName']
                        else:
                            h = 0
                            for m in dado['ListValues']['ListValue']:
                                lista[key['alias']][h] = {}
                                lista[key['alias']][h]['id'] = m['@id']
                                lista[key['alias']][h]['displayName'] = m['@displayName']
                                h += 1
                    else:
                        lista[key['alias']] = "ListValue com mais de um valor selecionando."
                        print("ListValue com mais de um valor selecionando.")
                else:
                    lista[key['alias']] = ''
            elif dado['@type'] in ['9', '23']:
                lista[key["alias"]] = {}
                if 'Reference' in dado:
                    if '@id' in dado['Reference']:
                        lista[key["alias"]][0] = {}
                        lista[key['alias']][0]['id'] = dado['Reference']['@id']
                        lista[key['alias']][0]['texto'] = dado['Reference']['#text']
                    else:
                        cont = 0
                        for ref in dado['Reference']:
                            if '@contentId' in ref:
                                lista[key['alias']][cont] = {}
                                lista[key['alias']][cont]['id'] = ref['@id']
                                lista[key['alias']][cont]['texto'] = ref['#text']
                                cont += 1
            elif dado['@type'] in ['11']:
                lista[key['alias']] = {}
                if 'File' in dado:
                    if '@id' in dado['File']:
                        lista[key["alias"]][0] = {}
                        lista[key['alias']][0]['id'] = dado['File']['@id']
                        if '#text' in dado['File']:
                            lista[key['alias']][0]['nome'] = dado['File']['#text']
                        else:
                            lista[key['alias']][0]['nome'] = ''
                    else:
                        cont = 0
                        for d in dado['File']:
                            if '@id' in d:
                                lista[key['alias']][cont] = {}
                                lista[key['alias']][cont]['id'] = d['@id']
                                lista[key['alias']][cont]['nome'] = d['#text']
                                cont += 1
                            else:
                                lista[key['alias']] = ''
            elif dado['@type'] in ['24']:
                lista[key["alias"]] = {}
                if 'Subform' in dado:
                    if '@contentId' in dado['Subform']:
                        lista[key["alias"]][0] = {}
                        lista[key['alias']][0]['id'] = dado['Subform']['@contentId']
                        if '#text' in dado['Subform']['Field']:
                            lista[key['alias']][0]['texto'] = dado['Subform']['Field']['#text']
                        else:
                            for b in dado['Subform']['Field']:
                                d = extrai_dados(campos, b)
                                for chave, valor in d.items():
                                    lista[key['alias']][0][chave] = valor
                    else:
                        cont = 0
                        for sub in dado['Subform']:
                            if '@contentId' in sub:
                                lista[key['alias']][cont] = {}
                                lista[key['alias']][cont]['id'] = sub['@contentId']
                                if '#text' in sub['Field']:
                                    lista[key['alias']][cont]['texto'] = sub['Field']['#text']
                                else:
                                    for b in sub['Field']:
                                        d = extrai_dados(campos, b)
                                        for chave, valor in d.items():
                                            lista[key['alias']][cont][chave] = valor
                                cont += 1
            elif dado['@type'] in ['8']:
                lista[key["alias"]] = {}
                if 'Groups' in dado:
                    if dado['Groups'] is not None:
                        if 'Group' in dado['Groups']:
                            if '#text' in dado['Groups']['Group']:
                                lista[key["alias"]][0] = {}
                                lista[key['alias']][0]['id'] = dado['Groups']['Group']['@id']
                                lista[key['alias']][0]['name'] = dado['Groups']['Group']['#text']
                            else:
                                for group in dado['Groups']['Group']:
                                    m = 0
                                    if '#text' in group:
                                        lista[key["alias"]][m] = {}
                                        lista[key['alias']][m]['id'] = group['@id']
                                        lista[key['alias']][m]['name'] = group['#text']
                                        m += 1
                if 'Users' in dado:
                    if dado['Users'] is not None:
                        if 'User' in dado['Users']:
                            if '#text' in dado['Users']['User']:
                                lista[key["alias"]][0] = {}
                                lista[key['alias']][0]['id'] = dado['Users']['User']['@id']
                                lista[key['alias']][0]['name'] = dado['Users']['User']['#text']
                            else:
                                print(dado['Users'])
            else:
                print(dado)

            return lista


def extrai_dados(campos, dado):
    lista = {}

    if dado['@type'] in ['1', '2', '3', '6', '21', '22']:
        if '#text' in dado:
            value = dado['#text']
        else:
            value = ''
    elif dado['@type'] == '4':
        value = extract_list_values(dado)
    elif dado['@type'] in ['9', '23']:
        value = extract_references(dado)
    elif dado['@type'] == '11':
        value = extract_files(dado)
    elif dado['@type'] == '24':
        value = extract_subform(dado, campos)
    elif dado['@type'] == '8':
        value = extract_groups_and_users(dado)

    for key in campos.values():
        if key['guid'] == dado['@guid']:
            lista_alias = key['alias']
            lista[lista_alias] = value
            break

    return lista


def extract_list_values(dado):
    if 'ListValues' not in dado:
        return []

    if 'ListValue' in dado['ListValues']:
        if '@id' in dado['ListValues']['ListValue']:
            dado['ListValues']['ListValue'] = [dado['ListValues']['ListValue']]
            # return dado['ListValues']['ListValue']['@displayName']
        # else:
        return [extract_list_value(x) for x in dado['ListValues']['ListValue']]

    return "ListValue com mais de um valor selecionando."


def extract_list_value(data):
    return data['@displayName']


def extract_references(dado):
    if 'Reference' not in dado:
        return []
    if '@id' in dado['Reference']:
        dado['Reference'] = [dado['Reference']]
        # return [{
        #     'id': dado['Reference']['@id'],
        #     'texto': dado['Reference']['#text']
        # }]
    return [extract_reference(x) for x in dado['Reference']]


def extract_reference(data):
    return {
        'id': data['@id'],
        'texto': data['#text']
    }


def extract_files(dado):
    if 'File' not in dado:
        return []
    if '@id' in dado['File']:
        dado['File'] = [dado['File']]
        # if '#text' in dado['File']:
        #     return [{
        #         'id': dado['File']['@id'],
        #         'nome': dado['File']['#text']
        #     }]
        # else:
        #     return [{
        #         'id': dado['File']['@id'],
        #         'nome': ''
        #     }]
    return [extract_file(x) for x in dado['File']]


def extract_file(data):
    return {
        'id': data['@id'],
        'nome': data['#text'] if '#text' in data else ''
    }


def extract_subform(dado, campos):
    if 'Subform' not in dado:
        if 'Field' in dado:
            dado = {'Subform': dado}
        else:
            return []
    if '@contentId' in dado['Subform']:
        subform_data = extract_subform_field(dado['Subform']['Field'], campos)
        return [{
            'id': dado['Subform']['@contentId'],
            **subform_data
        }]
    return [extract_subform(x, campos) for x in dado['Subform']]


def extract_subform_field(field, campos):
    subform_data = {}
    if '#text' in field:
        field = [field]
        # subform_data = {
        #     'texto': field['#text']
        # }
    # else:
    for f in field:
        subfield_data = extrai_dados(campos, f)
        for k, v in subfield_data.items():
            subform_data[k] = v
    return subform_data


def extract_groups_and_users(dado):
    if 'Groups' not in dado and 'Users' not in dado:
        return ''
    groups_data, users_data = [], []
    if 'Groups' in dado and dado['Groups'] is not None and 'Group' in dado['Groups']:
        groups_data = extract_groups(dado['Groups']['Group'])
    if 'Users' in dado and dado['Users'] is not None and 'User' in dado['Users']:
        users_data = extract_users(dado['Users']['User'])
    return groups_data + users_data


def extract_groups(groups):
    if '#text' in groups:
        return [{
            'id': groups['@id'],
            'name': groups['#text']
        }]
    return [extract_group(x) for x in groups]


def extract_group(group):
    return {
        'id': group['@id'],
        'name': group['#text']
    }


def extract_users(users):
    if '#text' in users:
        return [{
            'id': users['@id'],
            'name': users['#text']
        }]
    return [extract_user(x) for x in users]


def extract_user(user):
    return {
        'id': user['@id'],
        'name': user['#text']
    }


# def search_old(xml_search, token=util.get_token(), page_number=1, quantidade=False):
#     load_dotenv('./.env')
#     settings = Settings(strict=False, xml_huge_tree=True)

#     AMBIENTE = os.getenv('AMBIENTE')

#     wsdl = f'{os.getenv(f"URL_{AMBIENTE}")}/RSAarcher/ws/search.asmx?wsdl'

#     client = Client(wsdl=wsdl, settings=settings)

#     search_result = client.service.ExecuteSearch(sessionToken=token, searchOptions=xml_search, pageNumber=page_number)
#     dict_search = xmltodict.parse(search_result)

#     if quantidade:
#         return int(dict_search['Records']['@count'])

#     campos = {}
#     cont_campo = 0
#     for dado in dict_search['Records']['Metadata']['FieldDefinitions']['FieldDefinition']:
#         campos[cont_campo] = {
#             'guid': dado['@guid'],
#             'alias': dado['@name']
#         }
#         cont_campo += 1

#     records = []
#     if 'Record' in dict_search['Records']['Record']:
#         colunas = {}
#         if 'Field' in dict_search['Records']['Record']:
#             if '@guid' in dict_search['Records']['Record']['Field']:
#                 colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Field']))
#             else:
#                 for dado in dict_search['Records']['Record']['Field']:
#                     colunas.update(extrai_dados(campos, dado))
#         if 'Record' in dict_search['Records']['Record']:
#             if type(dict_search['Records']['Record']['Record']) is list:
#                 for dado in dict_search['Records']['Record']['Record']:
#                     if 'Field' in dado:
#                         if '@guid' in dado['Field']:
#                             to_update = extrai_dados(campos, dado['Field'])
#                             for k, v in to_update.items():
#                                 if k not in colunas:
#                                     colunas[k] = []
#                                 colunas[k].append(v)
#                             # colunas.update(extrai_dados(campos, dado['Field']))
#                         else:
#                             for d in dado['Field']:
#                                 to_update = extrai_dados(campos, d)
#                                 for k, v in to_update.items():
#                                     if k not in colunas:
#                                         colunas[k] = []
#                                     colunas[k].append(v)
#                                 # colunas.update(extrai_dados(campos, d))
#             else:
#                 if 'Field' in dict_search['Records']['Record']['Record']:
#                     if '@guid' in dict_search['Records']['Record']['Record']['Field']:
#                         colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Record']['Field']))
#                     else:
#                         for dado in dict_search['Records']['Record']['Record']['Field']:
#                             colunas.update(extrai_dados(campos, dado))
#         records.append(colunas)
#     else:
#         if type(dict_search['Records']['Record']) is list:
#             for register in dict_search['Records']['Record']:
#                 colunas = {}
#                 if 'Field' in register:
#                     if '@guid' in register['Field']:
#                         to_update = extrai_dados(campos, register['Field'])
#                         for k, v in to_update.items():
#                             if k not in colunas:
#                                 colunas[k] = []
#                             colunas[k].append(v)
#                         # colunas.update(extrai_dados(campos, register['Field']))
#                     else:
#                         for d in register['Field']:
#                             to_update = extrai_dados(campos, d)
#                             for k, v in to_update.items():
#                                 if k not in colunas:
#                                     colunas[k] = []
#                                 colunas[k].append(v)
#                             # colunas.update(extrai_dados(campos, d))
#                     # records.append(colunas)
#                 if 'Record' in register:
#                     if 'Field' in register['Record']:
#                         if '@guid' in register['Record']['Field']:
#                             to_update = extrai_dados(campos, register['Record']['Field'])
#                             for k, v in to_update.items():
#                                 if k not in colunas:
#                                     colunas[k] = []
#                                 colunas[k].append(v)
#                             # colunas.update(extrai_dados(campos, register['Record']['Field']))
#                         else:
#                             for d in register['Record']['Field']:
#                                 to_update = extrai_dados(campos, d)
#                                 for k, v in to_update.items():
#                                     if k not in colunas:
#                                         colunas[k] = []
#                                     colunas[k].append(v)
#                                 # colunas.update(extrai_dados(campos, d))
#                         # records.append(colunas)
#                     else:
#                         for dado in register['Record']:
#                             if 'Field' in dado:
#                                 if '@guid' in dado['Field']:
#                                     to_update = extrai_dados(campos, dado['Field'])
#                                     for k, v in to_update.items():
#                                         if k not in colunas:
#                                             colunas[k] = []
#                                         colunas[k].append(v)
#                                     # colunas.update(extrai_dados(campos, dado['Field']))
#                                 else:
#                                     for d in dado['Field']:
#                                         to_update = extrai_dados(campos, d)
#                                         for k, v in to_update.items():
#                                             if k not in colunas:
#                                                 colunas[k] = []
#                                             colunas[k].append(v)
#                                         # colunas.update(extrai_dados(campos, d))
#                 records.append(colunas)
#         else:
#             colunas = {}
#             if 'Field' in dict_search['Records']['Record']:
#                 if '@guid' in dict_search['Records']['Record']['Field']:
#                     colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Field']))
#                 else:
#                     for dado in dict_search['Records']['Record']['Field']:
#                         colunas.update(extrai_dados(campos, dado))
#                 records.append(colunas)
#     return records


def search_(search, page=1):
    wsdl = 'https://arteria.costaesilvaadv.com.br/RSAarcher/ws/search.asmx?wsdl'
    # wsdl = 'https://att.costaesilvaadv.com.br/RSAarcher/ws/search.asmx?wsdl'


    settings = Settings(strict=False, xml_huge_tree=True)

    client = Client(wsdl=wsdl, settings=settings)

    inicio = time()

    search = client.service.ExecuteSearch(sessionToken=f"{banco_de_dados.get_token('robo02', 'Produção')}",
                                          searchOptions=search,
                                          pageNumber=page)

    fim = time()

    dict_search = xmltodict.parse(search)

    util.mensagens(f"{dict_search['Records']['@count']} registros encontrados",
              'ok', bold=True)
    campos = {}
    cont_campo = 0
    for dado in dict_search['Records']['Metadata']['FieldDefinitions']['FieldDefinition']:
        campos[cont_campo] = {
            'guid': dado['@guid'],
            'alias': dado['@id'] + "_" + dado['@name']
        }
        cont_campo += 1

    records = []
    if 'Record' in dict_search['Records']['Record']:
        colunas = {}
        if 'Field' in dict_search['Records']['Record']:
            if '@guid' in dict_search['Records']['Record']['Field']:
                colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Field']))
            else:
                for dado in dict_search['Records']['Record']['Field']:
                    colunas.update(extrai_dados(campos, dado))
        if 'Record' in dict_search['Records']['Record']:
            if type(dict_search['Records']['Record']['Record']) is list:
                for dado in dict_search['Records']['Record']['Record']:
                    if 'Field' in dado:
                        if '@guid' in dado['Field']:
                            colunas.update(extrai_dados(campos, dado['Field']))
                        else:
                            for d in dado['Field']:
                                colunas.update(extrai_dados(campos, d))
            else:
                if 'Field' in dict_search['Records']['Record']['Record']:
                    if '@guid' in dict_search['Records']['Record']['Record']['Field']:
                        colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Record']['Field']))
                    else:
                        for dado in dict_search['Records']['Record']['Record']['Field']:
                            colunas.update(extrai_dados(campos, dado))
        records.append(colunas)
    else:
        if type(dict_search['Records']['Record']) is list:
            for register in dict_search['Records']['Record']:
                colunas = {}
                if 'Field' in register:
                    if '@guid' in register['Field']:
                        colunas.update(extrai_dados(campos, register['Field']))
                    else:
                        for d in register['Field']:
                            colunas.update(extrai_dados(campos, d))
                    # records.append(colunas)
                if 'Record' in register:
                    if 'Record' in register['Record']:
                        if type(register['Record']['Record']) is list:
                            a = []
                            for aux_register in register['Record']['Record']:
                                au_reg = {}
                                if 'Field' in aux_register:
                                    if '@guid' in aux_register['Field']:
                                        colunas.update(extrai_dados(campos, aux_register['Field']))
                                    else:
                                        for d in aux_register['Field']:
                                            au_reg.update(extrai_dados(campos, d))
                                    # records.append(colunas)
                                else:
                                    for dado in aux_register:
                                        if 'Field' in dado:
                                            if '@guid' in dado['Field']:
                                                colunas.update(extrai_dados(campos, dado['Field']))
                                            else:
                                                for d in dado['Field']:
                                                    colunas.update(extrai_dados(campos, d))
                                a.append(au_reg)
                            colunas.update({aux_register['@levelId']: a})
                    if 'Field' in register['Record']:
                        if '@guid' in register['Record']['Field']:
                            colunas.update(extrai_dados(campos, register['Record']['Field']))
                        else:
                            for d in register['Record']['Field']:
                                colunas.update(extrai_dados(campos, d))
                        # records.append(colunas)
                    else:
                        for dado in register['Record']:
                            if 'Field' in dado:
                                if '@guid' in dado['Field']:
                                    colunas.update(extrai_dados(campos, dado['Field']))
                                else:
                                    for d in dado['Field']:
                                        colunas.update(extrai_dados(campos, d))
                            if 'Record' in dado:
                                if '@guid' in dado['Record']:
                                    colunas.update(extrai_dados(campos, dado['Field']))
                                else:
                                    b = []
                                    for e in dado['Record']:
                                        au_reg = {}
                                        if 'Field' in e:
                                            if type(e) is str:
                                                pass
                                            else:
                                                if '@guid' in e['Field']:
                                                    au_reg.update(extrai_dados(campos, e['Field']))
                                                else:
                                                    for d in e['Field']:
                                                        au_reg.update(extrai_dados(campos, d))
                                                    b.append(au_reg)
                                                colunas.update({e['@levelId']: b})
                records.append(colunas)
        else:
            colunas = {}
            if 'Field' in dict_search['Records']['Record']:
                if '@guid' in dict_search['Records']['Record']['Field']:
                    colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Field']))
                else:
                    for dado in dict_search['Records']['Record']['Field']:
                        colunas.update(extrai_dados(campos, dado))
                records.append(colunas)
    return records


def bbb_search(search, page=1):
    wsdl = 'https://arteria.costaesilvaadv.com.br/RSAarcher/ws/search.asmx?wsdl'
    # wsdl = 'https://att.costaesilvaadv.com.br/RSAarcher/ws/search.asmx?wsdl'

    # Para Debug
    # settings = Settings(strict=False, xml_huge_tree=True)
    session = Session()
    session.verify = False
    # session.proxies = {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=wsdl, transport=Transport(session=session), settings=settings)
    # client = Client(wsdl=wsdl, settings=settings)

    inicio = time()

    search = client.service.ExecuteSearch(sessionToken=f"{banco_de_dados.get_token('robo02', 'Produção')}",
                                          searchOptions=search,
                                          pageNumber=page)

    fim = time()

    dict_search = xmltodict.parse(search)

    mensagens(f"{dict_search['Records']['@count']} registros encontrados",
              'ok', bold=True)
    campos = {}
    cont_campo = 0
    for dado in dict_search['Records']['Metadata']['FieldDefinitions']['FieldDefinition']:
        campos[cont_campo] = {
            'guid': dado['@guid'],
            'alias': dado['@id'] + "_" + dado['@name']
        }
        cont_campo += 1

    records = []
    if 'Record' in dict_search['Records']['Record']:
        colunas = {}
        if 'Field' in dict_search['Records']['Record']:
            if '@guid' in dict_search['Records']['Record']['Field']:
                colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Field']))
            else:
                for dado in dict_search['Records']['Record']['Field']:
                    colunas.update(extrai_dados(campos, dado))
        if 'Record' in dict_search['Records']['Record']:
            if type(dict_search['Records']['Record']['Record']) is list:
                for dado in dict_search['Records']['Record']['Record']:
                    if 'Field' in dado:
                        if '@guid' in dado['Field']:
                            colunas.update(extrai_dados(campos, dado['Field']))
                        else:
                            for d in dado['Field']:
                                colunas.update(extrai_dados(campos, d))
            else:
                if 'Field' in dict_search['Records']['Record']['Record']:
                    if '@guid' in dict_search['Records']['Record']['Record']['Field']:
                        colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Record']['Field']))
                    else:
                        for dado in dict_search['Records']['Record']['Record']['Field']:
                            colunas.update(extrai_dados(campos, dado))
        records.append(colunas)
    else:
        if type(dict_search['Records']['Record']) is list:
            for register in dict_search['Records']['Record']:
                colunas = {}
                if 'Field' in register:
                    if '@guid' in register['Field']:
                        colunas.update(extrai_dados(campos, register['Field']))
                    else:
                        for d in register['Field']:
                            colunas.update(extrai_dados(campos, d))
                    # records.append(colunas)
                if 'Record' in register:
                    if 'Record' in register['Record']:
                        if type(register['Record']['Record']) is list:
                            a = []
                            for aux_register in register['Record']['Record']:
                                au_reg = {}
                                if 'Field' in aux_register:
                                    if '@guid' in aux_register['Field']:
                                        colunas.update(extrai_dados(campos, aux_register['Field']))
                                    else:
                                        for d in aux_register['Field']:
                                            au_reg.update(extrai_dados(campos, d))
                                    # records.append(colunas)
                                else:
                                    for dado in aux_register:
                                        if 'Field' in dado:
                                            if '@guid' in dado['Field']:
                                                colunas.update(extrai_dados(campos, dado['Field']))
                                            else:
                                                for d in dado['Field']:
                                                    colunas.update(extrai_dados(campos, d))
                                a.append(au_reg)
                            colunas.update({aux_register['@levelId']: a})
                    if 'Field' in register['Record']:
                        if '@guid' in register['Record']['Field']:
                            colunas.update(extrai_dados(campos, register['Record']['Field']))
                        else:
                            for d in register['Record']['Field']:
                                colunas.update(extrai_dados(campos, d))
                        # records.append(colunas)
                    else:
                        for dado in register['Record']:
                            if 'Field' in dado:
                                if '@guid' in dado['Field']:
                                    colunas.update(extrai_dados(campos, dado['Field']))
                                else:
                                    for d in dado['Field']:
                                        colunas.update(extrai_dados(campos, d))
                            if 'Record' in dado:
                                if '@guid' in dado['Record']:
                                    colunas.update(extrai_dados(campos, dado['Field']))
                                else:
                                    b = []
                                    for e in dado['Record']:
                                        au_reg = {}
                                        if 'Field' in e:
                                            if type(e) is str:
                                                pass
                                            else:
                                                if '@guid' in e['Field']:
                                                    au_reg.update(extrai_dados(campos, e['Field']))
                                                else:
                                                    for d in e['Field']:
                                                        au_reg.update(extrai_dados(campos, d))
                                                    b.append(au_reg)
                                                colunas.update({e['@levelId']: b})
                records.append(colunas)
        else:
            colunas = {}
            if 'Field' in dict_search['Records']['Record']:
                if '@guid' in dict_search['Records']['Record']['Field']:
                    colunas.update(extrai_dados(campos, dict_search['Records']['Record']['Field']))
                else:
                    for dado in dict_search['Records']['Record']['Field']:
                        colunas.update(extrai_dados(campos, dado))
                records.append(colunas)
    return records


def search(search_xml, page=1, quantidade=False):
    wsdl = 'https://arteria.costaesilvaadv.com.br/RSAarcher/ws/search.asmx?wsdl'
    # wsdl = 'https://att.costaesilvaadv.com.br/RSAarcher/ws/search.asmx?wsdl'


    # Para Debug
    # settings = Settings(strict=False, xml_huge_tree=True)
    session = Session()
    session.verify = False
    # session.proxies = {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=wsdl, transport=Transport(session=session), settings=settings)
    # client = Client(wsdl=wsdl, settings=settings)

    inicio = time()

    search = client.service.ExecuteSearch(sessionToken=f"{util.get_token()}", searchOptions=search_xml,
                                          pageNumber=page)

    fim = time()

    if search is None:
        return []

    dict_search = xmltodict.parse(search)

    count = dict_search['Records']['@count']

    if quantidade:
        return int(count)

    # util.mensagens(f"{count} registros encontrados", 'ok', bold=True)
    level_names = get_level_names()
    campos = {}
    for i, dado in enumerate(dict_search['Records']['Metadata']['FieldDefinitions']['FieldDefinition']):
        campos[i] = {'guid': dado['@guid'], 'alias': dado['@name']}
    records = []
    if 'Record' in dict_search['Records']:
        for record in get_records(dict_search['Records']['Record'], campos, level_names):
            records.append(record)
        return records

    return []


def get_records(records, campos, level_names):
    if isinstance(records, dict):
        records = [records]
    for record in records:
        colunas = {}
        if 'Field' in record:
            if isinstance(record['Field'], dict):
                fields = [record['Field']]
            else:
                fields = record['Field']
            for field in fields:
                colunas.update(extrai_dados(campos, field))
        if 'Record' in record:
            for level, subrecords in group_subrecords(record['Record']):
                colunas.update(
                    {f'{level_names[int(level)]}': [_ for _ in get_records(subrecords, campos, level_names)]})
        yield colunas


def get_level_names():
    s = Session()
    s.headers.update({'Content-Type': 'application/json'})
    s.cookies.update({'__ArcherSessionCookie__': util.get_token()})
    r = s.get('https://arteria.costaesilvaadv.com.br/RSAarcher/api/core/system/level')
    # r = s.get('https://att.costaesilvaadv.com.br/RSAarcher/api/core/system/level')

    return {level['RequestedObject']['Id']: level['RequestedObject']['Name'] for level in r.json()}


def group_subrecords(records):
    levels = {}
    if isinstance(records, dict):
        records = [records]
    for record in records:
        level_id = record['@levelId']
        if level_id not in levels:
            levels[level_id] = []
        levels[level_id].append(record)
    return levels.items()


def search_all_pages(xml_search):
    original_page_size = xml_search[xml_search.find('<PageSize>') + 10:xml_search.find('</PageSize>')]
    xml_search_info = re.sub(r'<PageSize>.*</PageSize>', f'<PageSize>0</PageSize>', xml_search)
    quantidade = search(xml_search_info, page=1, quantidade=True)

    # for page in range(1, math.ceil(quantidade / int(original_page_size)) + 1):
    #     yield search(xml_search, page=page)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(search, xml_search, page) for page in
                   range(1, math.ceil(quantidade / int(original_page_size)) + 1)]
        for future in futures:
            yield future.result()


def cadastrar_e_vincular_subform(dados, app, subf_field_name, record_id=None, id_pap=None):
    archer_instance = instancia_arteria(app)
    if record_id:
        archer_instance.create_sub_record(dados, subf_field_name, record_id)
        if not record_id:
            raise Exception('Não foi possível atualizar o subformulário')
    else:
        record_id = archer_instance.create_sub_record(dados, subf_field_name)
        if not record_id:
            raise Exception('Não foi possível criar o subformulário')
        record = archer_instance.get_record(id_pap)
        current_sub_records_ids = record.get_field_content(subf_field_name)
        if current_sub_records_ids:
            if record_id not in current_sub_records_ids:
                current_sub_records_ids.append(record_id)
            vinculo = archer_instance.update_content_record({subf_field_name: current_sub_records_ids}, id_pap)
        else:
            vinculo = archer_instance.update_content_record({subf_field_name: [record_id]}, id_pap)
        if vinculo:
            return record_id
        else:
            raise Exception('Não foi possível vincular o subformulário')


def excluir_registro(app, record_id):
    archer_instance = instancia_arteria(app)
    if record_id:
        return archer_instance.delete_record(record_id)


def get_history(app, record_id, field_name):
    archer_instance = instancia_arteria(app)
    if record_id:
        return archer_instance.get_history_register_by_field(record_id, field_name)


def get_relacionamento_processo(app, record_id, subf_field_name):
    archer_instance = instancia_arteria(app)
    if record_id:
        record = archer_instance.get_record(record_id)
        return record.get_field_content(subf_field_name)
    
def enviar_comprovante_arteria(id_sistema_pagamento, solicitante_id,  id_proceso, name, ramo):
        nome = name.replace(" ", '')
        base_projeto = os.environ.get('base_projeto')
        load_dotenv('.env')

        diretorio =  f'{base_projeto}SAP\\SAP GUI'
        nome_arquivo = pegar_arquivo(nome,diretorio)

        arquivo = f"{diretorio}\\{nome_arquivo}"
        arquivo_base_64 = transformar_arquivo_para_base64(arquivo)
        id = archer_instance.post_attachment(arquivo, arquivo_base_64)
        dados_update = {"Solicitante": {"GroupList": [{'Id': f'{solicitante_id}'}]}, 
                                            "Responsável Pagamento no CS": {"UserList": [{'Id': '3560'}]},
                                            "Processo" : [f"{id_proceso}"],
                                            "Anexo Recibo/Guia": [f"{id}"],
                                            "Pagamento": f"{id_sistema_pagamento}"
                                            }
        cadastrar_arteria(dados_update, "Recibo")
        if ramo != '66 - HABITACIONAL':
            avanca_etapa_wf(id_sistema_pagamento,"Próxima Etapa",'Recibo')

def pegar_arquivo(nome,diretorio):
    prefixo = nome
    arquivos = os.listdir(diretorio)
    arquivos_filtrados = [arquivo for arquivo in arquivos if arquivo.startswith(prefixo)]
    if arquivos_filtrados:
        arquivo_mais_novo = max(arquivos_filtrados, key=lambda arquivo: os.path.getmtime(os.path.join(diretorio, arquivo)))
        print("Arquivo mais novo:", arquivo_mais_novo)
        return arquivo_mais_novo
        
def transformar_arquivo_para_base64(nome_arquivo):
        with open(nome_arquivo, "rb") as arquivo:
            dados = arquivo.read()
            dados_base64 = base64.b64encode(dados)
            return dados_base64.decode("utf-8") 

def enviar_folha_pagamento_arteria(arquivo_pdf, mes, id_sistema, data):
    instancia_arteria('Ficha Cadastral')
    arquivo_base_64 = transformar_arquivo_para_base64(arquivo_pdf)
    id = archer_instance.post_attachment(arquivo_pdf,arquivo_base_64)
    data_sub = {'Mês de Referência': [mes], 'Contracheque \ RPA': [f'{id}']}
    cadastrar_e_vincular_subf(data_sub , 'Ficha Cadastral', 'Contracheque e RPA', id_sistema)
    dado_update = {'Atualização Recibo': data}
    cadastrar_arteria(dado_update , 'Ficha Cadastral', id_sistema)

def enviar_comprovante_arteria(arquivo_pdf, id_sistema, id_recibo):
    instancia_arteria('Ficha Cadastral')
    arquivo_base_64 = transformar_arquivo_para_base64(arquivo_pdf)
    id = archer_instance.post_attachment(arquivo_pdf,arquivo_base_64)
    data_sub = {'Transferência de Conta Bancária': [f'{id}']}
    id_arteria = archer_instance.update_sub_record(data_sub,  'Contracheque e RPA', id_recibo)
    print(f"[red bold italic]--->>> {id_arteria}")
    cadastrar_arteria({} , 'Ficha Cadastral', id_sistema)

