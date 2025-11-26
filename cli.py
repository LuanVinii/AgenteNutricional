import os
import csv
import sys
from database import AlimentoRepository
from agente import AgenteDeRisco
from estatistica import calcular_media, calcular_variancia_e_desvio


class Cor:
    # Define as cores para usar no texto do terminal
    RESET = '\033[0m'
    VERMELHO = '\033[91m'
    AMARELO = '\033[93m'
    VERDE = '\033[92m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CINZA = '\033[90m'


def limpar_tela():
    # Limpa a tela do terminal dependendo do sistema operacional
    os.system('cls' if os.name == 'nt' else 'clear')


def formatar_alerta(risco: str, classificacao: str) -> str:
    # Coloca cor na mensagem de risco
    cor = {
        "VERMELHO": Cor.VERMELHO,
        "AMARELO": Cor.AMARELO,
        "VERDE": Cor.VERDE,
        "CINZA": Cor.CINZA
    }.get(risco, Cor.RESET)

    return f"{cor}>>> {risco} - {classificacao} <<<{Cor.RESET}"


def exibir_menu():
    # Mostra as opcoes principais pro usuario
    limpar_tela()
    print(f"{Cor.AZUL}========================================={Cor.RESET}")
    print(f"{Cor.MAGENTA}     AGENTE DE ALERTA NUTRICIONAL {Cor.RESET}")
    print(f"{Cor.AZUL}========================================={Cor.RESET}")
    print(f"{Cor.VERDE}1{Cor.RESET}. Analisar um Alimento (Decisão do Agente)")
    print(f"{Cor.VERDE}2{Cor.RESET}. Listar Alimentos Disponíveis")
    print(f"{Cor.VERDE}3{Cor.RESET}. Exportar Relatório CSV (Dados Brutos)")
    print(f"{Cor.VERDE}4{Cor.RESET}. Análise Estatística (Média, Desvio Padrão)")
    print(f"{Cor.VERMELHO}5{Cor.RESET}. Sair")
    print(f"{Cor.AZUL}-----------------------------------------{Cor.RESET}")
    return input("Escolha uma opção: ")


def exibir_analise(agente: AgenteDeRisco):
    # Tela onde o usuario digita o alimento e ve o resultado
    limpar_tela()
    print(f"{Cor.AZUL}--- ANÁLISE NUTRICIONAL ---\n{Cor.RESET}")

    nome_digitado = input("Digite o nome do alimento para análise: ").strip()
    if not nome_digitado:
        return

    # Arruma o nome para ficar igual ao que esta no banco com a primeira letra maiuscula
    nome_padronizado = nome_digitado.title()

    # Pede pro agente analisar esse alimento
    resultado = agente.analisar_alimento(nome_padronizado)

    risco, classificacao, descricao, sodio, gordura, fibra, proteina, carboidrato = resultado

    print(f"\nAlimento Analisado: {Cor.AZUL}{nome_padronizado.upper()}{Cor.RESET}")
    print(f"-----------------------------------------")
    print(formatar_alerta(risco, classificacao))
    print(f"Regra Ativada: {descricao}")
    print(f"-----------------------------------------")

    # Mostra os numeros brutos
    print(f"{Cor.MAGENTA}DADOS POR 100g (Valores no BD):{Cor.RESET}")
    print(f"  > Sódio: {sodio:.2f} mg")
    print(f"  > Gordura Saturada: {gordura:.2f} g")
    print(f"  > Carboidrato: {carboidrato:.2f} g")
    print(f"  > Fibra: {fibra:.2f} g")
    print(f"  > Proteína: {proteina:.2f} g")

    input(f"\nPressione {Cor.AZUL}ENTER{Cor.RESET} para continuar...")


def listar_alimentos(repo: AlimentoRepository):
    # Mostra todos os nomes de alimentos que estao no banco
    limpar_tela()
    print(f"{Cor.AZUL}--- ALIMENTOS DISPONÍVEIS ---\n{Cor.RESET}")

    alimentos = repo.obter_todos_alimentos()

    if not alimentos:
        print(f"{Cor.VERMELHO}Nenhum alimento encontrado no banco de dados.{Cor.RESET}")
        return

    # Organiza a lista em colunas para ficar bonito
    max_len = max(len(a) for a in alimentos) if alimentos else 0
    cols = 3
    for i, alimento in enumerate(alimentos):
        print(f"{alimento:<{max_len + 3}}", end="")
        if (i + 1) % cols == 0:
            print()

    print("\n")
    input(f"Pressione {Cor.AZUL}ENTER{Cor.RESET} para continuar...")


def exportar_relatorio_csv(repo: AlimentoRepository):
    # Cria um arquivo csv com todos os dados
    caminho_saida = "relatorio_nutricional.csv"
    dados = repo.obter_dados_relatorio()

    cabecalho = ["Nome_Alimento", "Sodio", "Gordura_Saturada", "Fibra", "Proteina", "Carboidrato"]

    try:
        with open(caminho_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(cabecalho)
            writer.writerows(dados)
        print(f"\n{Cor.VERDE}SUCESSO:{Cor.RESET} Relatório exportado para {caminho_saida}")
    except Exception as e:
        print(f"\n{Cor.VERMELHO}ERRO:{Cor.RESET} Não foi possível exportar o arquivo: {e}")

    input(f"\nPressione {Cor.AZUL}ENTER{Cor.RESET} para continuar...")


def exibir_estatisticas(repo: AlimentoRepository):
    # Calcula e mostra media e variacao dos nutrientes
    limpar_tela()
    print(f"{Cor.AZUL}--- ANÁLISE ESTATÍSTICA NUTRICIONAL (DISPERSÃO) ---\n{Cor.RESET}")
    alimentos = repo.obter_todos_alimentos()
    print(f"{Cor.MAGENTA}Cálculos baseados em {len(alimentos)} alimentos do BD.{Cor.RESET}\n")

    colunas_analise = ["sodio", "gordura_saturada", "fibra", "proteina", "carboidrato"]

    print(f"{'NUTRIENTE':<20}{'MÉDIA':>10}{'VAR.':>10}{'DESV. PADRÃO':>15}")
    print("=" * 55)

    for coluna in colunas_analise:
        # Busca todos os valores daquela coluna no banco
        dados = repo.obter_valores_coluna(coluna)

        # Faz as contas matematicas
        media = calcular_media(dados)
        variancia, desvio_padrao = calcular_variancia_e_desvio(dados)

        print(f"{coluna.upper():<20}{media:>10.2f}{variancia:>10.2f}{desvio_padrao:>15.2f}")

    print("\n*Unidades: Sódio (mg), Outros (g).")
    input(f"\nPressione {Cor.AZUL}ENTER{Cor.RESET} para continuar...")


def menu_principal(agente: AgenteDeRisco, repo: AlimentoRepository):
    # Mantem o programa rodando ate a pessoa escolher sair
    while True:
        opcao = exibir_menu()

        if opcao == '1':
            exibir_analise(agente)
        elif opcao == '2':
            listar_alimentos(repo)
        elif opcao == '3':
            exportar_relatorio_csv(repo)
        elif opcao == '4':
            exibir_estatisticas(repo)
        elif opcao == '5':
            print(f"{Cor.AZUL}\nEncerrando o Agente Nutricional. Até mais!{Cor.RESET}")
            break
        else:
            print(f"{Cor.VERMELHO}Opção inválida. Tente novamente.{Cor.RESET}")
            input(f"\nPressione {Cor.AZUL}ENTER{Cor.RESET} para continuar...")


def criar_arquivo_dados_csv():
    # Cria o arquivo com os alimentos iniciais se ele nao existir
    caminho = "dados_alimentos.csv"

    # Lista com os dados prontos pra gravar
    dados = [
        ("Bacon Frito", 1500, 15.0, 0.0, 37.0, 0.0), ("Salgadinho Queijo", 850, 6.0, 1.0, 10.0, 55.0),
        ("Queijo Mussarela", 718, 11.2, 0.0, 24.0, 1.0), ("Mortadela", 1200, 10.3, 0.0, 14.0, 1.0),
        ("Azeite de Oliva", 2, 14.0, 0.0, 0.0, 0.0), ("Pão Integral", 450, 0.7, 6.9, 9.0, 45.0),
        ("Iogurte Natural Integral", 60, 4.5, 0.0, 4.5, 6.0), ("Biscoito Maizena", 150, 3.0, 1.0, 7.0, 75.0),
        ("Amendoim Torrado", 5, 7.0, 9.0, 25.0, 16.0), ("Salmão Grelhado", 46, 3.1, 0.0, 20.0, 0.0),
        ("Banana Prata", 1, 0.1, 2.0, 1.3, 27.0), ("Feijão Cozido", 235, 0.3, 8.5, 9.0, 14.0),
        ("Peito de Frango", 95, 1.2, 0.0, 31.0, 0.0), ("Brócolis Cozido", 10, 0.2, 3.0, 2.8, 6.0),
        ("Arroz Branco Cozido", 1, 0.1, 1.0, 2.5, 28.0), ("Refrigerante Cola", 10, 0.0, 0.0, 0.0, 38.0),
        ("Leite Integral", 45, 2.0, 0.0, 3.2, 4.7), ("Batata Doce", 15, 0.1, 2.6, 1.6, 20.0),
        ("Chocolate ao Leite", 75, 10.0, 2.0, 7.0, 55.0), ("Cenoura Cozida", 35, 0.1, 2.6, 0.6, 9.0),
        ("Hamburguer Industrial", 600, 7.0, 1.0, 18.0, 15.0), ("Gelatina", 50, 0.0, 0.0, 1.5, 15.0),
        ("Pão Francês", 550, 0.5, 1.5, 8.0, 55.0), ("Mel", 4, 0.0, 0.0, 0.1, 82.0),
        ("Manga", 2, 0.1, 1.6, 0.8, 15.0), ("Pipoca (Óleo e Sal)", 300, 2.5, 12.0, 11.0, 65.0),
        ("Bolo Simples", 250, 4.0, 0.5, 5.0, 40.0), ("Atum em Óleo (Drenado)", 380, 1.5, 0.0, 25.0, 0.0),
        ("Ovo Cozido", 133, 3.7, 0.0, 13.0, 0.6), ("Lentilha Cozida", 200, 0.1, 7.9, 9.0, 20.0),
        ("Abacaxi", 1, 0.0, 1.4, 0.5, 13.0), ("Abacate", 10, 2.0, 6.7, 2.0, 8.5),
        ("Alface", 1, 0.0, 2.0, 1.2, 3.0), ("Aveia", 7, 1.4, 10.6, 17.0, 66.0),
        ("Beterraba Cozida", 70, 0.1, 2.8, 1.6, 10.0), ("Cebola Cozida", 4, 0.0, 1.7, 1.1, 7.0),
        ("Cerveja Lager", 10, 0.0, 0.0, 0.5, 3.5), ("Champignon", 5, 0.1, 1.0, 3.0, 3.5),
        ("Couve Flor", 30, 0.1, 2.0, 1.9, 5.0), ("Doce de Leite", 90, 4.5, 0.0, 6.0, 56.0),
        ("Goiaba", 2, 0.1, 5.4, 2.5, 14.0), ("Hambúrguer Caseiro", 90, 4.0, 0.5, 25.0, 0.0),
        ("Kiwi", 3, 0.1, 3.0, 1.1, 15.0), ("Maionese Industrial", 750, 6.0, 0.0, 0.5, 0.5),
        ("Mandioca Cozida", 5, 0.1, 1.8, 1.0, 30.0), ("Milho Cozido", 15, 0.6, 2.4, 3.2, 21.0),
        ("Nescau", 300, 1.5, 1.0, 5.0, 80.0), ("Ostra Crua", 300, 1.0, 0.0, 9.0, 4.0),
        ("Pêra", 1, 0.1, 3.1, 0.4, 15.0), ("Tofu", 7, 0.8, 0.5, 10.0, 1.9),
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
        print(f"Arquivo '{caminho}' já existe.")


def inicializar_projeto():
    # Prepara tudo cria as tabelas e carrega os dados do arquivo
    repo = AlimentoRepository()

    print("\n--- INICIALIZAÇÃO DO SISTEMA ---")
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
        # 1. Liga o repositorio e o banco
        repo = inicializar_projeto()

        # 2. Cria a inteligencia do agente
        agente = AgenteDeRisco(repo)

        # 3. Abre o menu pro usuario
        menu_principal(agente, repo)

    except Exception as e:
        print(f"{Cor.VERMELHO}ERRO CRÍTICO NA EXECUÇÃO:{Cor.RESET} {e}", file=sys.stderr)

    finally:
        # 4. Fecha a conexao com o banco no final
        if repo:
            repo.fechar_conexao()