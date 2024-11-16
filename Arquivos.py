from decimal import Decimal

import pandas as pd
import chardet
from unidecode import unidecode

class Arquivos:
    @staticmethod
    def retirar_notacao_cientifica(dataframe, colunas):
        for coluna in colunas:
            if coluna in dataframe.columns:  # Verifica se a coluna existe no DataFrame
                dataframe[coluna] = dataframe[coluna].apply(
                    lambda x: str(Decimal(x)) if pd.notna(x) else x
                )
            else:
                print(f"Coluna '{coluna}' não encontrada no DataFrame.")

    @staticmethod
    def remover_acentos(dataframe):
        acentos = {
            'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n',
            'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
            'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
            'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
            'Ç': 'C', 'Ñ': 'N'
        }

        def substituir_acentos(texto):
            for acento, sem_acento in acentos.items():
                texto = texto.replace(acento, sem_acento)
            return texto

        return dataframe.apply(lambda col: col.map(lambda x: substituir_acentos(str(x)) if isinstance(x, str) else x))

    @staticmethod
    def abrir_remover_acentos(data, arq_output):

        dadosRS = data[data['UF'] == 'RS']
        dadosRS.columns = [unidecode(col) for col in dadosRS.columns]

        dadosRS_sem_acentos = Arquivos.remover_acentos(dadosRS)

        new_columns = [col.replace(' (R$)', '').replace(' ', '_').replace('/', '_').replace(',', '_').replace('__', '_').replace("'s", 's')
                       for col in dadosRS_sem_acentos.columns]
        dadosRS_sem_acentos.columns = new_columns

        dadosRS_sem_acentos.to_csv(arq_output, index=False, encoding='utf-8', sep=";")
        print(arq_output, 'Salvo com sucesso!')

    @staticmethod
    def abrir_remover_reconstrucao(data, arq_output):
        colunas = ['AGREGACAO','MUNICIPIO','RECONHECIMENTO','GESTOR','TIPO','FONTE','EIXO','SUBEIXO','FINALIDADE','PAGO']
        data.columns = colunas
        data = Arquivos.remover_acentos(data)
        data.to_csv(arq_output, index=False, encoding='utf-8', sep=";")
        print(arq_output, 'Salvo com sucesso!')

    @staticmethod
    def abrir_arquivos(opc,input,output):
        colunas_valores = [
                    'PEPL_Assistencia_medica_saude_publica_e_atendimento_de_emergencias_medicas',
                    'PEPL_Abastecimento_de_agua_potavel',
                    'PEPL_Esgoto_de_aguas_pluviais_e_sistema_de_esgotos_sanitarios',
                    'PEPL_Sistema_de_limpeza_urbana_e_de_recolhimento_e_destinacao_do_lixo',
                    'PEPL_Sistema_de_desinfestacao_desinfeccao_do_habitat_controle_de_pragas_e_vetores',
                    'PEPL_Geracao_e_distribuicao_de_energia_eletrica',
                    'PEPL_Telecomunicacoes',
                    'PEPL_Transportes_locais_regionais_e_de_longo_curso',
                    'PEPL_Distribuicao_de_combustiveis_especialmente_os_de_uso_domestico',
                    'PEPL_Seguranca_publica',
                    'PEPL_Ensino'
                ]
        with open(input, 'rb') as f:
            result = chardet.detect(f.read(10000))
        data = pd.read_csv(input, encoding=result['encoding'], delimiter=";")

        if opc == 1:
            Arquivos.retirar_notacao_cientifica(data,colunas_valores)
            Arquivos.abrir_remover_acentos(data,output)
        if opc == 2:
            Arquivos.abrir_remover_reconstrucao(data,output)