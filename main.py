import os
import csv
import sys
# Importa as classes e funcoes dos modulos
from database import AlimentoRepository
from agente import AgenteDeRisco
from cli import menu_principal, limpar_tela, Cor


# Funcao para criar o arquivo de dados inicial
def criar_arquivo_dados_csv():
    # Cria o arquivo CSV inicial com 50 alimentos
    caminho = "dados_alimentos.csv"

    # Valores por 100g: Sodio(mg), Gordura Saturada(g), Fibra(g), Proteina(g), Carboidrato(g)
    dados = [
        ("Bacon Frito", 1500, 15.0, 0.0, 37.0, 0.0), ("Salgadinho Queijo", 850, 6.0, 1.0, 10.0, 55.0),
        ("Queijo Mussarela", 718, 11.2, 0.0, 24.0, 1.0), ("Mortadela", 1200, 10.3, 0.0, 14.0, 1.0),
        ("Azeite de Oliva", 2, 14.0, 0.0, 0.0, 0.0), ("Pao Integral", 450, 0.7, 6.9, 9.0, 45.0),
        ("Iogurte Natural Integral", 60, 4.5, 0.0, 4.5, 6.0), ("Biscoito Maizena", 150, 3.0, 1.0, 7.0, 75.0),
        ("Amendoim Torrado", 5, 7.0, 9.0, 25.0, 16.0), ("Salmao Grelhado", 46, 3.1, 0.0, 20.0, 0.0),
        ("Banana Prata", 1, 0.1, 2.0, 1.3, 27.0), ("Feijao Cozido", 235, 0.3, 8.5, 9.0, 14.0),
        ("Peito de Frango", 95, 1.2, 0.0, 31.0, 0.0), ("Brocolis Cozido", 10, 0.2, 3.0, 2.8, 6.0),
        ("Arroz Branco Cozido", 1, 0.1, 1.0, 2.5, 28.0), ("Refrigerante Cola", 10, 0.0, 0.0, 0.0, 38.0),
        ("Leite Integral", 45, 2.0, 0.0, 3.2, 4.7), ("Batata Doce", 15, 0.1, 2.6, 1.6, 20.0),
        ("Chocolate ao Leite", 75, 10.0, 2.0, 7.0, 55.0), ("Cenoura Cozida", 35, 0.1, 2.6, 0.6, 9.0),
        ("Hamburguer Industrial", 600, 7.0, 1.0, 18.0, 15.0), ("Gelatina", 50, 0.0, 0.0, 1.5, 15.0),
        ("Pao Frances", 550, 0.5, 1.5, 8.0, 55.0), ("Mel", 4, 0.0, 0.0, 0.1, 82.0),
        ("Manga", 2, 0.1, 1.6, 0.8, 15.0), ("Pipoca (Oleo e Sal)", 300, 2.5, 12.0, 11.0, 65.0),
        ("Bolo Simples", 250, 4.0, 0.5, 5.0, 40.0), ("Atum em Oleo (Drenado)", 380, 1.5, 0.0, 25.0, 0.0),
        ("Ovo Cozido", 133, 3.7, 0.0, 13.0, 0.6), ("Lentilha Cozida", 200, 0.1, 7.9, 9.0, 20.0),
        ("Abacaxi", 1, 0.0, 1.4, 0.5, 13.0), ("Abacate", 10, 2.0, 6.7, 2.0, 8.5),
        ("Alface", 1, 0.0, 2.0, 1.2, 3.0), ("Aveia", 7, 1.4, 10.6, 17.0, 66.0),
        ("Beterraba Cozida", 70, 0.1, 2.8, 1.6, 10.0), ("Cebola Cozida", 4, 0.0, 1.7, 1.1, 7.0),
        ("Cerveja Lager", 10, 0.0, 0.0, 0.5, 3.5), ("Champignon", 5, 0.1, 1.0, 3.0, 3.5),
        ("Couve Flor", 30, 0.1, 2.0, 1.9, 5.0), ("Doce de Leite", 90, 4.5, 0.0, 6.0, 56.0),
        ("Goiaba", 2, 0.1, 5.4, 2.5, 14.0), ("Hamburguer Caseiro", 90, 4.0, 0.5, 25.0, 0.0),
        ("Kiwi", 3, 0.1, 3.0, 1.1, 15.0), ("Maionese Industrial", 750, 6.0, 0.0, 0.5, 0.5),
        ("Mandioca Cozida", 5, 0.1, 1.8, 1.0, 30.0), ("Milho Cozido", 15, 0.6, 2.4, 3.2, 21.0),
        ("Nescau", 300, 1.5, 1.0, 5.0, 80.0), ("Ostra Crua", 300, 1.0, 0.0, 9.0, 4.0),
        ("Pera", 1, 0.1, 3.1, 0.4, 15.0), ("Tofu", 7, 0.8, 0.5, 10.0, 1.9),
    ]

    if not os.path.exists(caminho):
        try:
            with open(caminho, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["nome_alimento", "sodio", "gordura_saturada", "fibra", "proteina", "carboidrato"])
                writer.writerows(dados)
            print(f"Arquivo '{caminho}' criado com alimentos iniciais.")
        except Exception as e:
            print(f"Erro ao criar o arquivo CSV inicial: {e}")
    else:
        print(f"Arquivo '{caminho}' ja existe.")


def inicializar_projeto():
    # Prepara o banco de dados e carrega as informacoes
    repo = AlimentoRepository()

    print("\n--- INICIALIZACAO DO SISTEMA ---")
    repo.criar_esquema()
    repo.inserir_regras()
    criar_arquivo_dados_csv()
    repo.inserir_dados_csv("dados_alimentos.csv")
    print("--- BANCO DE DADOS PRONTO ---\n")
    return repo


if __name__ == '__main__':
    limpar_tela()
    repo = None
    try:
        # 1. Inicia o banco de dados
        repo = inicializar_projeto()

        # 2. Cria a inteligencia do agente de risco
        agente = AgenteDeRisco(repo)

        # 3. Inicia o menu do programa
        menu_principal(agente, repo)

    except Exception as e:
        # Mostra um erro critico se algo der muito errado
        print(f"{Cor.VERMELHO}ERRO CRÍTICO NA EXECUCAO:{Cor.RESET} {e}", file=sys.stderr)

    finally:
        # 4. Garante que a conexao com o banco seja fechada no final
        if repo:
            repo.fechar_conexao()