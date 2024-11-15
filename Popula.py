import pandas as pd
import numpy as np

def obterproximoid(cursor, tabela, coluna_id):
    # Consulta para obter o próximo valor de chave primária para a tabela específica
    qry = f"SELECT COALESCE(MAX({coluna_id}), 0) + 1 FROM {tabela}"
    cursor.execute(qry)
    proximo_id = cursor.fetchone()[0]
    return proximo_id


def encontrarOuInserirRegistro(cursor, tabela, coluna_id, coluna_descricao, valor_descricao):
    try:
        qry = f"SELECT {coluna_id} FROM {tabela} WHERE {coluna_descricao} = %s"
        cursor.execute(qry, (valor_descricao,))
        registro = cursor.fetchone()

        if registro is None:
            proximo_id = obterproximoid(cursor, tabela, coluna_id)
            qry = f"INSERT INTO {tabela} ({coluna_id}, {coluna_descricao}) VALUES (%s, %s)"
            cursor.execute(qry, (proximo_id, valor_descricao))
            cursor.connection.commit()  # Confirma a transação após a inserção
            return proximo_id
        else:
            return registro[0]

    except Exception as e:
        print(f"Erro ao buscar ou inserir registro: {e}")
        cursor.connection.rollback()  # Realiza rollback para corrigir o estado da transação
        raise  # Preciso Relançar a exceção para tratar no nível superior

def retorna_valor_float(df, colunas):
    soma = 0
    for coluna in colunas:
        valor = df[coluna]
        soma += float(str(valor).replace(',', '.'))
    return soma

class Popula:
    def __init__(self, conn,opc, file_path):
        self.conn = conn
        self.dataFrame = pd.read_csv(file_path, delimiter=';')
        if opc == 1:
            self.populate_secretaria()
        if opc == 2:
            self.populate_reconstrucao()

    def populate_secretaria(self):
        cursor = self.conn.cursor()
        for _, row in self.dataFrame.iterrows():
            try:
                municipio = encontrarOuInserirRegistro(cursor, 'municipio', 'mun_id', 'descricao', row['Municipio'])
                id = obterproximoid(cursor, 'secretaria', 'id')
                valor = float(str(row['PEPR_Agricultura']).replace(',', '.'))
                dano_habitacionais_valor = float(str(row['DM_Unidades_Habitacionais_Valor']).replace(',', '.'))
                dano_infraestrutura_publica_Valor = float(str(row['DM_Obras_de_infraestrutura_publica_Valor']).replace(',', '.'))
                danoPepl = retorna_valor_float(row, [
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
                ])
                danoPepr = retorna_valor_float(row,['PEPR_Agricultura','PEPR_Pecuaria','PEPR_Industria','PEPR_Comercio','PEPR_Servicos'])
                query = """
                    INSERT INTO Secretaria (
                        UF, Cobrade,  DH_Mortos, DH_Feridos, DH_Enfermos,
                        DH_Desabrigados, DH_Desaparecidos, DM_Und_Casas_Destruidas,
                        Dm_Valor_Casas, Dm_Valor_Dano_Publico, Dm_Obra_infra_Valor,
                        pepl, pepr, id, municipio,data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """
                data = (
                    row['UF'], row['COBRADE'], row['DH_Mortos'], row['DH_Feridos'],
                    row['DH_Enfermos'], row['DH_Desabrigados'], row['DH_Desaparecidos'],
                    row['DM_Unidades_Habitacionais_Destruidas'], dano_habitacionais_valor,
                    dano_infraestrutura_publica_Valor, danoPepl, danoPepr, valor, id, municipio,row['Registro']
                )
                cursor.execute(query, data)

            except Exception as e:
                print(f"Erro ao inserir dados: {e}, municipio: {row['Municipio']}")
                cursor.connection.rollback()  # Rollback para corrigir a transação em caso de erro
        self.conn.commit()
        cursor.close()

    def populate_reconstrucao(self):
        cursor = self.conn.cursor()
        for _, row in self.dataFrame.iterrows():
            if pd.isna(row['MUNICIPIO']):
                continue
            id = obterproximoid(cursor, 'reconstrucao', 'id')
            municipio = encontrarOuInserirRegistro(cursor,'municipio','mun_id','descricao',row['MUNICIPIO'])
            eixo = encontrarOuInserirRegistro(cursor,'eixo', 'eixo_id','descricao',row['EIXO'])
            subeixo = encontrarOuInserirRegistro(cursor, 'subeixo', 'sub_id','descricao',row['SUBEIXO'])
            pago = row['PAGO'].replace('.', '').replace(',', '.')
            try:
                query = """
                INSERT INTO Reconstrucao (
                    id,  reconhecimento, gestor, tipo, fonte, finalidade,
                    pago, municipio, eixo, subeixo,data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """
                data = (
                    id, row['RECONHECIMENTO'], row['GESTOR'],row['TIPO'],row['FONTE'],row['FINALIDADE'],pago,municipio,eixo,subeixo,'05/01/2024'
                )
                cursor.execute(query, data)


            except Exception as e:
                print(f"Erro ao inserir dados: {e}")
        self.conn.commit()
        cursor.close()
