import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def grafico_um(conn):
    ## ESTE GRAFICO MOSTRA OS TOP 10 MUNICIPIOS COM MAIS MORTOS, FERIDOS E ENFERMOS - MAPA DE CALOR
    label_grafico = "Tragedia em numeros, resumo!"
    sql = """
           SELECT m.descricao AS municipio,
              SUM(s.dh_mortos) AS Mortos,
              SUM(s.dh_feridos) AS Feridos,
              SUM(s.dh_enfermos) AS Enfermos
           FROM Secretaria s
           LEFT JOIN municipio m ON m.mun_id = s.municipio
          where (cobrade LIKE '13213%' OR cobrade LIKE '12300%'
                         OR cobrade LIKE '13214%' OR cobrade LIKE '13211%'
                         OR cobrade LIKE '12100%' OR cobrade LIKE '13212%'
                         OR cobrade LIKE '13215%')
           GROUP BY m.descricao
           ORDER BY m.descricao
       """
    df = pd.read_sql(sql, conn)

    # Filtrar os top 10 municípios
    top_municipios = df.nlargest(10, ['mortos', 'feridos', 'enfermos'])
    df_melted = top_municipios.melt(id_vars=['municipio'], var_name='Categoria', value_name='Quantidade')
    fig = px.density_heatmap(df_melted, x='municipio', y='Categoria', z='Quantidade',
                             title='Tragedia em numeros',
                             labels={'municipio': 'Município', 'Quantidade': 'Quantidade', 'Categoria': 'Categoria'},
                             color_continuous_scale='Viridis')

    # Ajustar layout
    fig.update_layout(
        xaxis_title='Municipio',
        yaxis_title='Categoria',
        coloraxis_colorbar=dict(title='Quantidade'),
        showlegend=False
    )
    fig.show()

def grafico_dois(conn):
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

def grafico_tres(conn):
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
    print(f'secretarias: \n {df_sec_filtrado_por_cobrade_e_valor_total.head(20)}')
    #######PARA MUNICIPIOS:
    df_municipios_afetados = pd.read_sql("""
                SELECT m.descricao AS municipio, 
                       r.pago AS pago_afetados 
                FROM reconstrucao r
                LEFT JOIN municipio m ON m.mun_id = r.municipio
                order by pago_afetados desc
            """, conn)
    print(f'municipios: \n {df_municipios_afetados.head(20)}')
    # Realizar merge entre os DataFrames, unindo pela coluna "municipio"
    # Mesclar os dois DataFrames baseando-se no nome do município
    df_misto = pd.merge(
        df_sec_filtrado_por_cobrade_e_valor_total,
        df_municipios_afetados,
        on="municipio",
        how="outer"
    )
    # Agrupar por município e somar os valores
    df_misto_agrupado = df_misto.groupby("municipio", as_index=False)[["pago", "pago_afetados"]].sum()

    # Recalcular a coluna "pago_total" após o agrupamento
    df_misto_agrupado["pago_total"] = df_misto_agrupado["pago"] + df_misto_agrupado["pago_afetados"]

    # Ordenar pelo maior valor total e pegar os 10 primeiros
    df_top_10 = df_misto_agrupado.sort_values(by="pago_total", ascending=False).head(10)

    # Exibir o resultado consolidado
    print(df_top_10)
    df_top_10 = df_top_10.drop("pago_total", axis=1)
    # Criar gráfico interativo com os valores consolidados
    fig = px.bar(
        df_top_10.melt(id_vars='municipio', var_name='Categoria', value_name='Valor'),
        x='municipio',
        y='Valor',
        color='Categoria',
        title='Top 10 Valores de Danos e Prejuízos por Município (Consolidado)',
        labels={'municipio': 'Município', 'Valor': 'Valor (R$)', 'Categoria': 'Categoria'},
        height=600
    )

    # Ajustar layout do gráfico
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Município",
        yaxis_title="Valor (R$)",
        legend_title="Categoria",
        margin=dict(l=40, r=40, t=40, b=120),
        showlegend=True
    )

    # Mostrar o gráfico
    fig.show()

def grafico_quatro(conn):
    # Consultar os dados
    dados = pd.read_sql("""
        SELECT m.descricao AS municipio, r.finalidade, r.pago
        FROM reconstrucao r
        LEFT JOIN municipio m ON r.municipio = m.mun_id
    """, conn)

    # Finalidades que queremos filtrar
    finalidades_desejadas = [
        "Abono Salarial", "FGTS - Saque Calamidade",
        "Apoio financeiro a pescadores artesanais e empregadas domesticas",
        "Antecipacao do Auxilio-Gas", "Antecipacao do Bolsa-Familia",
        "Antecipacao do Piso Nacional da Enfermagem"
    ]

    # Filtrar apenas as finalidades desejadas
    df_filtrado = dados[dados["finalidade"].isin(finalidades_desejadas)]

    # Agrupar por município e finalidade, somando os valores pagos
    df_agrupado = df_filtrado.groupby(["municipio", "finalidade"], as_index=False)["pago"].sum()

    # Selecionar os top 5 municípios com os maiores valores pagos para cada finalidade
    df_top5 = (
        df_agrupado.groupby("finalidade", group_keys=False)
        .apply(lambda x: x.nlargest(5, "pago"))
        .reset_index(drop=True)
    )

    # Criar o gráfico interativo
    fig = px.line(
        df_top5,
        x="municipio",
        y="pago",
        color="finalidade",
        title="Evolução dos Valores Pagos (Top 5 Municípios por Finalidade)",
        labels={"pago": "Valor Pago (R$)", "municipio": "Município", "finalidade": "Finalidade"},
    )

    # Ajustar layout para melhorar visualização
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(title="Município", tickangle=-45),
        yaxis=dict(title="Valor Pago (R$)"),
        legend_title="Finalidade"
    )

    # Exibir o gráfico
    fig.show()

def grafico_cinco(conn):
    ## GRAFICO PREJUIZO EM RELAÇÃO AO NUMERO DE MORTES NORMALIZADO POR MUNICIPIO
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
            color='red', alpha=0.9, align='center')
    valorMax = str(df_top_prejuizos[
                       'total_prejuizos'].max())
    # Gráfico de prejuízos normalizados (à direita, ajustando a posição com deslocamento)
    plt.bar(municipios, df_top_prejuizos['total_prejuizos_normalizado'], width=largura_barra,
            label='Prejuízos (Normalizado)',
            color='brown', alpha=0.7, align='edge')

    plt.xlabel('Município')
    plt.ylabel(f'Valor Normalizado {valorMax}')
    plt.title('Desastres, Mortos e Prejuízos Normalizados por Município (Top 3)')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.show()

class Graficos:
    def __init__(self,conn):
        # grafico_um(conn)
        # grafico_dois(conn)
        # grafico_tres(conn)
        # grafico_quatro(conn)
        grafico_cinco(conn)

