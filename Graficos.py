import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

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
        ## para mapear evento de maio 2024
        df_sec_filtrado_por_cobrade = pd.read_sql("""
                        select m.descricao municipio,s.dm_valor_casas As "Dano nas casas",s.dm_obra_infra_valor as "Dano em Infra-publica",s.pepl as "Prejuizo público",s.pepr "Prejuizo privado",sum(s.dm_valor_casas+s.dm_obra_infra_valor+s.pepl+s.pepr) total from secretaria s
                         left join municipio m on s.municipio =m.mun_id
                    WHERE
                    ((cobrade LIKE '13213%' OR cobrade LIKE '12300%'
                     OR cobrade LIKE '13214%' OR cobrade LIKE '13211%'
                     OR cobrade LIKE '12100%' OR cobrade LIKE '13212%'
                     OR cobrade LIKE '13215%') and (pepl > 0 or pepr > 0))
                     group by  m.descricao,s.dm_valor_casas,s.dm_obra_infra_valor,s.pepl,s.pepr
                     order by total desc                     
                """, conn)
        df_sec_filtrado_por_cobrade = df_sec_filtrado_por_cobrade.head(10)
        df_sec_filtrado_por_cobrade = df_sec_filtrado_por_cobrade.drop('total', axis=1)
        # Criar gráfico de barras interativo
        fig = px.bar(
            df_sec_filtrado_por_cobrade.melt(id_vars='municipio', var_name='Categoria', value_name='Valor'),
            x='municipio',
            y='Valor',
            color='Categoria',
            title='Valores de Danos e Prejuízos por Município',
            labels={'municipio': 'Município', 'Valor': 'Valor (R$)', 'Categoria': 'Categoria'},
            height=600
        )
        # Ajustar layout
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="Município",
            yaxis_title="Valor (R$)",
            legend_title="Categoria",
            margin=dict(l=40, r=40, t=40, b=120),
            showlegend=True
        )
        fig.show()

        ###############  PARA SECRETARIA:
        df_sec_filtrado_por_cobrade_e_valor_total = pd.read_sql("""
            SELECT m.descricao AS municipio, 
                   SUM(s.dm_valor_casas + s.dm_obra_infra_valor + s.pepl + s.pepr) AS pago 
            FROM secretaria s
            LEFT JOIN municipio m ON s.municipio = m.mun_id
            WHERE ((cobrade LIKE '13213%' OR cobrade LIKE '12300%'
                   OR cobrade LIKE '13214%' OR cobrade LIKE '13211%'
                   OR cobrade LIKE '12100%' OR cobrade LIKE '13212%'
                   OR cobrade LIKE '13215%') AND (pepl > 0 OR pepr > 0)) 
            GROUP BY m.descricao
            ORDER BY pago DESC
        """, conn)
        df_sec_filtrado_por_cobrade_e_valor_total = df_sec_filtrado_por_cobrade_e_valor_total.head(10)
        print(df_sec_filtrado_por_cobrade_e_valor_total)

        #######PARA MUNICIPIOS:
        df_municipios_afetados = pd.read_sql("""
            SELECT m.descricao AS municipio, 
                   r.pago AS pago_afetados 
            FROM reconstrucao r
            LEFT JOIN municipio m ON m.mun_id = r.municipio
            order by pago_afetados desc
        """, conn)
        df_municipios_afetados = df_municipios_afetados.head(10)
        print(df_municipios_afetados)

        # Fazer o merge
        df_misto = df_municipios_afetados.merge(
            df_sec_filtrado_por_cobrade_e_valor_total,
            on='municipio',
            how='inner'
        )

        # Criar uma nova coluna com a soma dos valores pagos
        if 'pago' in df_misto.columns and 'pago_afetados' in df_misto.columns:
            df_misto['pago_total'] = df_misto['pago'] + df_misto['pago_afetados']
        else:
            print("As colunas 'pago' ou 'pago_afetados' estão ausentes no DataFrame resultante.")

        # Gerar gráfico interativo
        fig = px.bar(
            df_misto.melt(id_vars='municipio', var_name='Categoria', value_name='Valor'),
            x='municipio',
            y='Valor',
            color='Categoria',
            title='Valores de Danos e Prejuízos por Município (Soma dos Dados)',
            labels={'municipio': 'Município', 'Valor': 'Valor (R$)', 'Categoria': 'Categoria'},
            height=600
        )

        # Ajustar layout
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="Município",
            yaxis_title="Valor (R$)",
            legend_title="Categoria",
            margin=dict(l=40, r=40, t=40, b=120),
            showlegend=True
        )

        fig.show()

