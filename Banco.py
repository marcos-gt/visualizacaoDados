import psycopg2

class Banco:
    def __init__(self, conn, nome_tabela):
        """
        Inicializa a conexão com o banco de dados e verifica/cria a tabela, se necessário.

        Args:
            conn: Objeto de conexão com o banco de dados.
            nome_tabela: Nome da tabela a ser verificada ou criada.
        """
        self.conn = conn
        self.nome_tabela = nome_tabela
        self.verificar_e_criar_tabela()

    def verificar_e_criar_tabela(self):
        """
        Verifica se a tabela existe e executa os comandos SQL de criação caso ela não exista.
        """
        if not self.tabela_existe():
            self.criar_tabelas()

    def tabela_existe(self):
        """
        Verifica se a tabela especificada existe no banco de dados.

        Returns:
            bool: True se a tabela existe, False caso contrário.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
            """,
            (self.nome_tabela,)
        )
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists

    def criar_tabelas(self):
        """
        Executa os comandos SQL para criar as tabelas e suas restrições de chave estrangeira.
        """
        comandos_sql = [
            """
            CREATE TABLE Secretaria (
                UF varchar(2),
                Cobrade varchar(255),
                DH_Mortos integer,
                DH_Feridos integer,
                DH_Enfermos integer,
                DH_Desabrigados integer,
                DH_Desaparecidos integer,
                DM_Und_Casas_Destruidas integer,
                Dm_Valor_Casas float,
                Dm_Valor_Dano_Publico float,
                Dm_Obra_infra_Valor float,
                pepl float,
                pepr float,
                id integer PRIMARY KEY,
                municipio integer
            );
            """, """
            CREATE TABLE RECONSTRUCAO (
            	id integer PRIMARY KEY,
            	reconhecimento varchar(255),
            	gestor varchar(255),
            	tipo varchar(255),
            	fonte varchar(255),
            	finalidade varchar(255),
            	pago float,
            	municipio integer,
            	eixo integer,
            	subeixo integer
            );
            """, """
            CREATE TABLE eixo (
            	eixo_id integer PRIMARY KEY,
            	descricao varchar(255)
            );
            """, """
            CREATE TABLE subeixo (
            	sub_id integer PRIMARY KEY,
            	descricao varchar(255)
            );
            """, """
            CREATE TABLE municipio (
            	mun_id integer PRIMARY KEY,
            	descricao varchar(255)
            );
            """, """
            ALTER TABLE Secretaria ADD CONSTRAINT FK_Secretaria_2
            	FOREIGN KEY (municipio)
            	REFERENCES municipio (mun_id)
            	ON DELETE RESTRICT;
            """, """ 
            ALTER TABLE RECONSTRUCAO ADD CONSTRAINT FK_RECONSTRUCAO_2
            	FOREIGN KEY (municipio)
            	REFERENCES municipio (mun_id)
            	ON DELETE RESTRICT;
            """, """ 
            ALTER TABLE RECONSTRUCAO ADD CONSTRAINT FK_RECONSTRUCAO_3
            	FOREIGN KEY (eixo)
            	REFERENCES eixo (eixo_id)
            	ON DELETE RESTRICT;
            """, """ 
            ALTER TABLE RECONSTRUCAO ADD CONSTRAINT FK_RECONSTRUCAO_4
            	FOREIGN KEY (subeixo)
            	REFERENCES subeixo (sub_id)
            	ON DELETE RESTRICT;
            """
        ]

    def limparBanco(self):
        comandos_sql = [""" DROP TABLE public.eixo CASCADE;
                            DROP TABLE public.subeixo CASCADE;
                            DROP TABLE public.municipio CASCADE;
                            DROP TABLE public.RECONSTRUCAO CASCADE;
                            DROP TABLE public.Secretaria CASCADE
                        """]


        cursor = self.conn.cursor()
        for comando in comandos_sql:
            cursor.execute(comando)
        self.conn.commit()
        cursor.close()
