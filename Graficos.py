import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def gerar_subgrafico(conn):
    df_sec_filtrado_por_cobrade = pd.read_sql("""
        select m.descricao municipio,
               s.dm_valor_casas As "Dano nas casas",
               s.dm_obra_infra_valor as "Dano em Infra-publica",
               s.dm_valor_dano_publico As "Dano público",
               s.pepl as "Prejuizo público", s.pepr "Prejuizo privado",
               sum(s.dm_valor_casas + s.dm_valor_dano_publico + s.dm_obra_infra_valor + s.pepl + s.pepr) total,
               s.data
        from secretaria s
        left join municipio m on s.municipio = m.mun_id
        WHERE
            ((cobrade LIKE '13213%' OR cobrade LIKE '12300%'
            OR cobrade LIKE '13214%' OR cobrade LIKE '13211%'
            OR cobrade LIKE '12100%' OR cobrade LIKE '13212%'
            OR cobrade LIKE '13215%') and (pepl > 0 or pepr > 0))
        group by m.descricao, s.dm_valor_casas, s.dm_obra_infra_valor, s.pepl, s.pepr, s.dm_valor_dano_publico, s.data
        order by total desc
    """, conn)

    # Converter a coluna 'data' para o ano
    df_sec_filtrado_por_cobrade['data'] = pd.to_datetime(df_sec_filtrado_por_cobrade['data']).dt.year

    # Criar subgráficos
    fig = make_subplots(rows=3, cols=1,
                        subplot_titles=("Top 10 Eventos de 2020", "Top 10 Eventos de 2021", "Top 10 Eventos de 2022"))

    # Filtrar e adicionar os dados de cada ano aos subgráficos
    for i, year in enumerate([2020, 2021, 2022], start=1):
        df_year = df_sec_filtrado_por_cobrade[df_sec_filtrado_por_cobrade['data'] == year].head(10)
        df_year = df_year.drop('total', axis=1)
        df_melted = df_year.melt(id_vars=['municipio', 'data'], var_name='Categoria', value_name='Valor')

        for categoria in df_melted['Categoria'].unique():
            df_categoria = df_melted[df_melted['Categoria'] == categoria]
            fig.add_trace(
                go.Bar(x=df_categoria['municipio'], y=df_categoria['Valor'], name=categoria, showlegend=(i == 1)),
                row=i, col=1
            )

    # Ajustar layout
    fig.update_layout(
        height=1800,
        title_text="Top 10 Valores de Danos e Prejuízos por Município (2020, 2021, 2022)",
        xaxis_title="Município",
        yaxis_title="Valor (R$)",
        legend_title="Categoria",
        margin=dict(l=40, r=40, t=40, b=120),
        showlegend=True
    )

    # Mostrar o gráfico
    fig.show()

def obter_valor_original(row, col_normalized, col_original, df):
    """Busca o valor original correspondente ou retorna NaN."""
    filtro = df['municipio_id'] == row['municipio_id']
    if filtro.sum() > 0:
        return df.loc[filtro, col_original].values[0]
    return float('nan')

def grafico_um(conn):
    ## ESTE GRAFICO MOSTRA OS TOP 10 MUNICIPIOS COM MAIS MORTOS, FERIDOS E ENFERMOS - MAPA DE CALOR
    label_grafico = "Tragedia em numeros, resumo!"
    sql = """
           SELECT m.descricao AS municipio,
              SUM(s.dh_mortos) AS Mortos,
              SUM(s.dh_feridos) AS Feridos,
              SUM(s.dh_enfermos) AS Enfermos,
              sum(s.dh_desabrigados) as Desabrigados
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
    color_continuous_scale = [
        (0.0, 'beige'),
        (0.5, 'blue'),
        (1.0, 'purple')
    ]
    # Filtrar os top 10 municípios
    top_municipios = df.nlargest(10, ['mortos', 'feridos', 'enfermos'])
    df_melted = top_municipios.melt(id_vars=['municipio'], var_name='Categoria', value_name='Quantidade')
    fig = px.density_heatmap(df_melted, x='municipio', y='Categoria', z='Quantidade',
                             title='Resumo dano humano em numeros',
                             labels={'municipio': 'Município', 'Quantidade': 'Quantidade', 'Categoria': 'Categoria'},
                             color_continuous_scale=color_continuous_scale)

    # Ajustar layout
    fig.update_layout(
        xaxis_title='Municipio',
        yaxis_title='Categoria',
        coloraxis_colorbar=dict(title='Quantidade'),
        showlegend=False
    )
    fig.show()

def grafico_dois(conn):
    gerar_subgrafico(conn)
    df_sec_filtrado_por_cobrade = pd.read_sql("""
           select m.descricao municipio,
           s.dm_valor_casas As "Dano nas casas",
           s.dm_obra_infra_valor as "Dano em Infra-publica",
           s.dm_valor_dano_publico As "Dano público",
           s.pepl as "Prejuizo público",s.pepr "Prejuizo privado",
           sum(s.dm_valor_casas+s.dm_valor_dano_publico+s.dm_obra_infra_valor+s.pepl+s.pepr) total ,
           s.data
        from secretaria s
        left join municipio m on s.municipio =m.mun_id
        WHERE
        	((cobrade LIKE '13213%' OR cobrade LIKE '12300%'
        	OR cobrade LIKE '13214%' OR cobrade LIKE '13211%'
        	OR cobrade LIKE '12100%' OR cobrade LIKE '13212%'
        	OR cobrade LIKE '13215%') and (pepl > 0 or pepr > 0))
        	group by  m.descricao,s.dm_valor_casas,s.dm_obra_infra_valor,s.pepl,s.pepr,s.dm_valor_dano_publico,s.data
        	order by total desc                      
    """, conn)
    df_sec_filtrado_por_cobrade['data'] = pd.to_datetime(df_sec_filtrado_por_cobrade['data']).dt.year

    df_sec_filtrado_por_cobrade = df_sec_filtrado_por_cobrade.head(10)
    df_sec_filtrado_por_cobrade = df_sec_filtrado_por_cobrade.drop('total', axis=1)
    # Criar gráfico de barras interativo
    fig = px.bar(
        df_sec_filtrado_por_cobrade.melt(id_vars=['municipio', 'data'], var_name='Categoria', value_name='Valor'),
        x='municipio',
        y='Valor',
        color='Categoria',
        title='Valores de Danos e Prejuízos por Município',
        labels={'municipio': 'Município', 'Valor': 'Valor (R$)', 'Categoria': 'Categoria'},
        height=600,
        hover_data={'data': True}  # Adiciona a coluna "data" no tooltip
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
                       SUM(s.dm_valor_casas + s.dm_obra_infra_valor+s.dm_valor_dano_publico + s.pepl + s.pepr) AS gasto_anterior 
                FROM secretaria s
                LEFT JOIN municipio m ON s.municipio = m.mun_id
                WHERE ((cobrade LIKE '13213%' OR cobrade LIKE '12300%'
                       OR cobrade LIKE '13214%' OR cobrade LIKE '13211%'
                       OR cobrade LIKE '12100%' OR cobrade LIKE '13212%'
                       OR cobrade LIKE '13215%') AND (pepl > 0 OR pepr > 0)) 
                GROUP BY m.descricao
                ORDER BY gasto_anterior DESC
            """, conn)
    #######PARA MUNICIPIOS:
    df_municipios_afetados = pd.read_sql("""
               SELECT m.descricao AS municipio, 
                       sum(r.pago) AS gasto_atual 
                FROM reconstrucao r
                LEFT JOIN municipio m ON m.mun_id = r.municipio
				group by m.descricao
                order by gasto_atual desc
            """, conn)
    df_misto = pd.merge(
        df_sec_filtrado_por_cobrade_e_valor_total,
        df_municipios_afetados,
        on="municipio",
        how="inner"
    )
    # Agrupar por município e somar os valores
    df_misto_agrupado = df_misto.groupby("municipio", as_index=False)[["gasto_anterior", "gasto_atual"]].sum()

    # Recalcular a coluna "pago_total" após o agrupamento
    df_misto_agrupado["pago_total"] = df_misto_agrupado["gasto_anterior"] + df_misto_agrupado["gasto_atual"]

    # Ordenar pelo maior valor total e pegar os 10 primeiros
    df_top_10 = df_misto_agrupado.sort_values(by="gasto_atual", ascending=False).head(10)

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
    sql = """
        SELECT m.descricao AS municipio,sum(r.pago) as total
        FROM reconstrucao r
        left join municipio m on r.municipio = m.mun_id
        group by m.descricao
        order by total desc
        limit 10;               
    """
    df = pd.read_sql(sql, conn)

    # Verificar valores ausentes ou inconsistências
    print(df.isnull().sum())
    print(df[df['total'] == 0])  # Filtrar valores totais iguais a zero
    df.fillna(0, inplace=True)

    # Criar gráfico de barras
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df['municipio'], df['total'], color='skyblue')
    ax.set_title('Top 10 Municípios com Maior Valor Pago')
    ax.set_xlabel('Município')
    ax.set_ylabel('Valor Pago (R$)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()



class Graficos:
    def __init__(self,conn):
        grafico_um(conn)
        grafico_dois(conn)
        grafico_tres(conn)
        grafico_quatro(conn)
        grafico_cinco(conn)

