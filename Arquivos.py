import pandas as pd
import chardet
from unidecode import unidecode

class Arquivos:
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
    def abrir_remover_acentos(caminho, arq_output):
        with open(caminho, 'rb') as f:
            result = chardet.detect(f.read(10000))

        data = pd.read_csv(caminho, encoding=result['encoding'], delimiter=";")
        dadosRS = data[data['UF'] == 'RS']
        dadosRS.columns = [unidecode(col) for col in dadosRS.columns]

        dadosRS_sem_acentos = Arquivos.remover_acentos(dadosRS)

        new_columns = [col.replace(' (R$)', '').replace(' ', '_').replace('/', '_').replace(',', '_').replace('__', '_').replace("'s", 's')
                       for col in dadosRS_sem_acentos.columns]
        dadosRS_sem_acentos.columns = new_columns

        dadosRS_sem_acentos.to_csv(arq_output, index=False, encoding='utf-8', sep=";")
        print(arq_output, 'Salvo com sucesso!')

    @staticmethod
    def abrir_remover_reconstrucao(caminho, arq_output):
        with open(caminho, 'rb') as f:
            result = chardet.detect(f.read(10000))

        data = pd.read_csv(caminho, encoding=result['encoding'], delimiter=";")
        colunas = ['AGREGACAO','MUNICIPIO','RECONHECIMENTO','GESTOR','TIPO','FONTE','EIXO','SUBEIXO','FINALIDADE','PAGO']
        data.columns = colunas
        data = Arquivos.remover_acentos(data)
        data.to_csv(arq_output, index=False, encoding='utf-8', sep=";")
        print(arq_output, 'Salvo com sucesso!')

    @staticmethod
    def abrir_arquivos(opc,input,output):
        if opc == 1:
            Arquivos.abrir_remover_acentos(input,output)
        if opc == 2:
            Arquivos.abrir_remover_reconstrucao(input,output)