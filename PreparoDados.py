import pandas as pd
import numpy as np

def municipios_secretaria(conn):
    return pd.read_sql(""" select distinct s.municipio from secretaria s
                       where cobrade like '13213%' or cobrade like '12300%'
                                                   or cobrade like '13214%'
                                                   or cobrade like '13211%'
                                                   or cobrade like '12100%'
                                                   or cobrade like '13212%'
                                                   or cobrade like '13215%'
                    """, con=conn)

def municipios_reconstrucao(conn):
    return pd.read_sql(""" select distinct s.municipio from reconstrucao s""", con=conn)



class PreparoDados:
    def __init__(self,conn):
        df_sec = municipios_secretaria(conn)
        df_rec = municipios_reconstrucao(conn)

        municipios_em_comun = pd.merge(df_sec, df_rec, on='municipio', how='inner')
        print("Municípios em comum:")
        for row in municipios_em_comun.iterrows():
            print(row)