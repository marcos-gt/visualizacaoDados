import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Graficos:
    def __init__(self,conn):
        cursor = conn.cursor()

        df_destinado = pd.read_sql("""
            select m.descricao municipio,sum(pepl) total_destinado from public.secretaria s
            left join public.municipio m on m.mun_id = s.municipio
            where cobrade like '132%' or cobrade like '12200'
            or cobrade like '12300' or cobrade like '12100'
            group by m.Descricao
            having sum(pepl)>0
            order by total_destinado desc
        """, conn)

        plt.figure(figsize=(10, 6))
        municipios = df_destinado.head(5)
        plt.bar(municipios['municipio'], municipios['total_destinado'])
        plt.xlabel('Municipio')
        plt.ylabel('Total Destinado (R$)')
        plt.title('Total Destinado a Cada Município para restaurar as casas (2020-2024)')
        plt.xticks(rotation=90)
        plt.show()

        df_desastres_mortos = pd.read_sql("""
                SELECT m.descricao,s.municipio, COUNT(*) as quantidade_desastres, SUM(s.dh_mortos) as total_mortos
                FROM Secretaria s
                left join municipio m on m.mun_id = s.municipio
                GROUP BY m.descricao,s.municipio
                ORDER BY total_mortos DESC;
        """, conn)

        df_prejuizos = pd.read_sql("""
            SELECT municipio, SUM(Pepl)+SUM(PEPR) as total_prejuizos
            FROM Secretaria
            GROUP BY municipio
            ORDER BY total_prejuizos DESC;
        """, conn)

        df_top_mortos = df_desastres_mortos.nlargest(5, 'total_mortos')
        df_top_prejuizos = df_prejuizos.nlargest(5, 'total_prejuizos')

        # Normalizar os valores
        df_top_mortos['total_mortos_normalizado'] = df_top_mortos['total_mortos'] / df_top_mortos['total_mortos'].max()
        df_top_prejuizos['total_prejuizos_normalizado'] = df_top_prejuizos['total_prejuizos'] / df_top_prejuizos[
            'total_prejuizos'].max()

        # Configurar o gráfico
        plt.figure(figsize=(12, 6))
        largura_barra = 0.35
        municipios = df_top_mortos['descricao']  # Usando os municípios dos dados de mortos
        plt.bar(municipios, df_top_mortos['total_mortos_normalizado'], width=largura_barra,
                label='Mortos (Normalizado)',
                color='skyblue', alpha=0.9, align='center')
        valorMax = str(df_top_prejuizos[
            'total_prejuizos'].max())
        # Gráfico de prejuízos normalizados (à direita, ajustando a posição com deslocamento)
        plt.bar(municipios, df_top_prejuizos['total_prejuizos_normalizado'], width=largura_barra,
                label='Prejuízos (Normalizado)',
                color='orange', alpha=0.7, align='edge')

        plt.xlabel('Município')
        plt.ylabel(f'Valor Normalizado {valorMax}')
        plt.title('Desastres, Mortos e Prejuízos Normalizados por Município (Top 3)')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()

        # FALTA ARRUMAR OUTROS GRAFICOS A PARTIR DAQUI ###

        # Filtra por ano para separar 2024

        df_misturado = cursor.execute("""select * from municipio m 
        left join secretaria s on m.mun_id = s.municipio
        where (cobrade like '132%' or cobrade like '12200')
        and extract(month s.data) = 5
        
        """,conn).fetchall()

        dados_2024 = df_misturado['data']=2024
        dados_2023 = df_misturado['data']=2023

        #
        # # Contagem de desastres por município para 2024 e anos anteriores
        # desastres_por_cidade_2024 = dados_2024['municipio'].value_counts()
        # desastres_por_cidade_anteriores = dados_anteriores['municipio'].value_counts()
        #
        # # Combina os dois em um DataFrame
        # comparacao_desastres = pd.DataFrame({
        #     '2024': desastres_por_cidade_2024,
        #     'Anteriores': desastres_por_cidade_anteriores
        # }).fillna(0)
        #
        # # Gráfico de barras para comparação
        # comparacao_desastres.plot(kind='bar', figsize=(12, 6))
        # plt.title('Quantidade de Desastres por Cidade: Comparação 2024 vs Anos Anteriores')
        # plt.xlabel('Cidade')
        # plt.ylabel('Quantidade de Desastres')
        # plt.legend(['2024', 'Anos Anteriores'])
        # plt.xticks(rotation=90)
        # plt.show()
