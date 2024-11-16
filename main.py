import psycopg2
from Arquivos import Arquivos
from Banco import Banco
from Graficos import Graficos
from Popula import Popula
from PreparoDados import PreparoDados


def connectar():
     conn = psycopg2.connect(database = "VizualicaoDeDados",
                                user = "postgres",
                                host = 'localhost',
                            password = "master",
                                port = 5432)
     return conn

if __name__ == "__main__":
    conexao = connectar()
    #Funções para criar os arquivos sem os acentos
    # Arquivos.abrir_arquivos(1,"C:\\Users\\Marcos\\Documents\\UFSC\\2024-2\\VisualizacaoDeDados\\Trab.Final\\Dados\\mdr_sedec_dados_informados_2020.csv","DadosRS_2020.csv")
    # Arquivos.abrir_arquivos(1,"C:\\Users\\Marcos\\Documents\\UFSC\\2024-2\\VisualizacaoDeDados\\Trab.Final\\Dados\\mdr_sedec_dados_informados_2021.csv","DadosRS_2021.csv")
    # Arquivos.abrir_arquivos(1,"C:\\Users\\Marcos\\Documents\\UFSC\\2024-2\\VisualizacaoDeDados\\Trab.Final\\Dados\\mdr_sedec_dados_informados_2022.csv","DadosRS_2022.csv")
    # Arquivos.abrir_arquivos(2,"C:\\Users\\Marcos\\Documents\\UFSC\\2024-2\\VisualizacaoDeDados\\Trab.Final\\Dados\\DadosReconstrucao.csv","Reconstrucao.csv")

    #Funções para criar as tabelas do banco
    #banco = Banco(conexao, "Secretaria")

    #Função para Popular Banco
    # Popula(conexao,1,'DadosRS_2020.csv')
    # Popula(conexao,1,'DadosRS_2021.csv')
    # Popula(conexao,1,'DadosRS_2022.csv')
    # Popula(conexao,2,'Reconstrucao.csv')
    Graficos = Graficos(conexao)
    # PreparoDados = PreparoDados(conexao)
    conexao.close()