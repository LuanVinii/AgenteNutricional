import csv
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, select, insert

# Configura os metadados e as tabelas do banco
metadata = MetaData()

# Define como e a tabela de alimentos
tabela_alimentos = Table(
    "Alimentos", metadata,
    Column('id', Integer, primary_key=True),
    Column('nome_alimento', String, unique=True, nullable=False),
    Column('sodio', Float, nullable=False),
    Column('gordura_saturada', Float, nullable=False),
    Column('fibra', Float, nullable=False),
    Column('proteina', Float, nullable=False),
    Column('carboidrato', Float, nullable=False)
)

# Define como e a tabela de regras
tabela_regras = Table(
    "Regras", metadata,
    Column('id', Integer, primary_key=True),
    Column('nivel_risco', String, nullable=False),
    Column('descricao_regra', String, nullable=False)
)


class AlimentoRepository:
    # Classe que controla tudo que entra e sai do banco de dados

    def __init__(self, nome_bd="agente_nutricional.db"):
        # Cria a conexao com o arquivo do banco sqlite
        self.engine = create_engine(f"sqlite:///{nome_bd}")
        self.connection = self.engine.connect()

    def criar_esquema(self):
        # Cria as tabelas no banco se elas nao existirem
        metadata.create_all(self.engine)
        print("Tabelas sendo criadas...")

    def inserir_regras(self):
        # Coloca as regras de risco no banco se ele estiver vazio
        s = select(tabela_regras)

        if not self.connection.execute(s).fetchone():
            print("Inserindo regras iniciais...")
            regras = [
                # Regras de risco alto vermelho
                {"nivel_risco": "VERMELHO", "descricao_regra": "ALTO RISCO: Alto Sódio e Alta Gordura Saturada"},
                {"nivel_risco": "VERMELHO",
                 "descricao_regra": "ALTO RISCO: Alto Sódio e Alto Carboidrato com Baixa Fibra"},
                {"nivel_risco": "VERMELHO",
                 "descricao_regra": "ALTO RISCO: Alta Gordura Saturada e Alto Carboidrato com Baixa Fibra"},

                # Regras de risco moderado amarelo
                {"nivel_risco": "AMARELO",
                 "descricao_regra": "MODERADO: Alto em Carboidratos, mas quase sem Fibras (oferece muita energia, mas poucos benefícios à saúde)"},
                {"nivel_risco": "AMARELO",
                 "descricao_regra": "MODERADO: Apresenta um fator de risco isolado (Alto Sódio OU Alta Gordura), mas o restante da composição é equilibrada"},
                {"nivel_risco": "AMARELO",
                 "descricao_regra": "MODERADO: Alto Carboidrato, mas parcialmente compensado por Proteína ou Fibra"},

                # Regras de risco baixo verde
                {"nivel_risco": "VERDE",
                 "descricao_regra": "BAIXO RISCO: Todos os fatores críticos (Sódio/Gordura/Carboidrato) abaixo dos limites"},
                {"nivel_risco": "VERDE",
                 "descricao_regra": "BAIXO RISCO: Níveis de risco controlados E Fibra OU Proteína alta (Perfil Ideal)"},
            ]
            self.connection.execute(insert(tabela_regras), regras)
            self.connection.commit()
            print("Regras inseridas.")

    def inserir_alimento(self, nome, sodio, gordura, fibra, proteina, carboidrato):
        # Tenta gravar um alimento novo no banco
        try:
            inserindo = insert(tabela_alimentos).values(
                nome_alimento=nome, sodio=sodio, gordura_saturada=gordura,
                fibra=fibra, proteina=proteina, carboidrato=carboidrato
            )
            self.connection.execute(inserindo)
            self.connection.commit()
        except Exception:
            pass

    def inserir_dados_csv(self, caminho_arquivo):
        # Le o arquivo csv e grava todos os alimentos no banco
        try:
            with open(caminho_arquivo, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                print(f"Lendo dados do arquivo '{caminho_arquivo}'...")
                for linha in reader:
                    if len(linha) == 6:
                        try:
                            self.inserir_alimento(linha[0], float(linha[1]), float(linha[2]), float(linha[3]),
                                                  float(linha[4]), float(linha[5]))
                        except ValueError as e:
                            print(f"Erro de conversão na linha: {linha}. Erro: {e}")
            print("Dados do CSV inseridos.")
        except FileNotFoundError:
            print(f"Erro: Arquivo {caminho_arquivo} não encontrado.")
        except Exception as e:
            print(f"Erro durante a leitura do CSV: {e}")

    def obter_dados_nutricionais(self, nome_alimento):
        # Busca os nutrientes de um alimento especifico
        stmt = select(
            tabela_alimentos.c.sodio, tabela_alimentos.c.gordura_saturada,
            tabela_alimentos.c.fibra, tabela_alimentos.c.proteina, tabela_alimentos.c.carboidrato
        ).where(tabela_alimentos.c.nome_alimento == nome_alimento)
        return self.connection.execute(stmt).fetchone()

    def obter_todos_alimentos(self):
        # Pega a lista com o nome de todos os alimentos
        selecao = select(tabela_alimentos.c.nome_alimento).order_by(tabela_alimentos.c.nome_alimento)
        return [row[0] for row in self.connection.execute(selecao)]

    def obter_valores_coluna(self, nome_coluna: str) -> list[float]:
        # Pega todos os numeros de uma coluna especifica tipo so o sodio de todos
        coluna = getattr(tabela_alimentos.c, nome_coluna, None)

        if coluna is None:
            print(f"A coluna {nome_coluna} não foi encontrada na tabela Alimentos.")
            return []

        selecao = select(coluna)

        return [float(row[0]) for row in self.connection.execute(selecao).fetchall()]

    def obter_dados_relatorio(self):
        # Pega tudo do banco para gerar o relatorio
        selecao = select(
            tabela_alimentos.c.nome_alimento, tabela_alimentos.c.sodio,
            tabela_alimentos.c.gordura_saturada, tabela_alimentos.c.fibra,
            tabela_alimentos.c.proteina, tabela_alimentos.c.carboidrato
        )
        return self.connection.execute(selecao).fetchall()

    def fechar_conexao(self):
        # Encerra a comunicacao com o banco
        self.connection.close()