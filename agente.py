# agente.py

from database import AlimentoRepository, tabela_regras
from sqlalchemy import select, func


class AgenteDeRisco:
    # Implementa a inteligencia do sistema aplicando regras para classificar o risco dos alimentos

    # Define os valores limites para considerar um nutriente alto ou baixo
    LIMITE_GORDURA_ALTA = 5.0
    LIMITE_SODIO_ALTO = 400.0
    LIMITE_FIBRA_BAIXA = 3.0
    LIMITE_PROTEINA_ALTA = 10.0
    LIMITE_CARBOIDRATO_ALTO = 30.0

    def __init__(self, repo: AlimentoRepository):
        # Recebe o repositorio para poder acessar os dados do banco
        self.repo = repo

    def _limpar_string(self, texto: str) -> str:
        # Remove pontuacoes e deixa o texto em minusculo para facilitar a busca
        texto = texto.lower().replace(':', '').replace('.', '').replace('(', '').replace(')', '').replace(',',
                                                                                                          '').strip()
        return texto

    def _buscar_descricao_regra(self, nivel_risco: str, padrao_regra: str):
        # Procura no banco de dados a descricao da regra que foi ativada
        try:
            # Limpa o texto de busca para evitar erros de formatacao
            padrao_busca_agente = self._limpar_string(padrao_regra)

            with self.repo.engine.connect() as connection:
                # Prepara a consulta no banco usando busca que ignora maiusculas e minusculas
                stmt = select(tabela_regras.c.descricao_regra).where(
                    (tabela_regras.c.nivel_risco == nivel_risco) &
                    (func.lower(tabela_regras.c.descricao_regra).like(f"%{padrao_busca_agente}%"))
                ).limit(1)

                resultado = connection.execute(stmt).fetchone()

                # Se nao encontrar de primeira tenta buscar apenas pela palavra energia
                if not resultado and padrao_busca_agente == "muita energia":
                    stmt = select(tabela_regras.c.descricao_regra).where(
                        (tabela_regras.c.nivel_risco == nivel_risco) &
                        (func.lower(tabela_regras.c.descricao_regra).like(f"%{self._limpar_string('energia')}%"))
                    ).limit(1)
                    resultado = connection.execute(stmt).fetchone()

                return resultado[
                    0] if resultado else f"[ERRO] Descrição da regra '{padrao_regra}' não encontrada no DB para o risco {nivel_risco}"
        except Exception as e:
            # Retorna mensagem de erro caso a consulta falhe
            return f"[ERRO INTERNO NO DB] Falha ao consultar: {e}"

    def analisar_alimento(self, nome_alimento: str) -> tuple:
        # Aplica as regras de classificacao verde amarelo ou vermelho no alimento

        dados = self.repo.obter_dados_nutricionais(nome_alimento)

        if not dados:
            return "CINZA", "Não Encontrado", "Dados do alimento não encontrados no sistema.", 0.0, 0.0, 0.0, 0.0, 0.0

        sodio, gordura, fibra, proteina, carboidrato = dados

        # Verifica se cada nutriente esta acima ou abaixo dos limites definidos
        is_sodio_alto = sodio > self.LIMITE_SODIO_ALTO
        is_gordura_alta = gordura > self.LIMITE_GORDURA_ALTA
        is_fibra_baixa = fibra < self.LIMITE_FIBRA_BAIXA
        is_proteina_alta = proteina > self.LIMITE_PROTEINA_ALTA
        is_carboidrato_alto = carboidrato > self.LIMITE_CARBOIDRATO_ALTO

        # Comeca a verificar as regras de decisao

        # Regras para risco vermelho
        # Caso critico com muito sodio e muita gordura
        if is_sodio_alto and is_gordura_alta:
            risco = "VERMELHO"
            classificacao = "Risco Crítico (Múltiplos Fatores)"
            padrao_regra = "Alto Sódio e Alta Gordura Saturada"

        # Caso com muito sodio muito carboidrato e pouca fibra
        elif is_sodio_alto and is_carboidrato_alto and is_fibra_baixa:
            risco = "VERMELHO"
            classificacao = "Risco Crítico (Sódio e Carboidratos)"
            padrao_regra = "Alto Sódio e Alto Carboidrato com Baixa Fibra"

        # Caso com muita gordura muito carboidrato e pouca fibra
        elif is_gordura_alta and is_carboidrato_alto and is_fibra_baixa:
            risco = "VERMELHO"
            classificacao = "Risco Crítico (Gordura e Carboidratos)"
            padrao_regra = "Alta Gordura Saturada e Alto Carboidrato com Baixa Fibra"

        # Regras para risco amarelo

        # Alimento com energia vazia muito carboidrato pouca fibra e sem proteina
        elif is_carboidrato_alto and is_fibra_baixa and not is_proteina_alta:
            risco = "AMARELO"
            classificacao = "Risco Moderado (Carboidratos Sem Benefício)"
            # Chave unica para busca no banco
            padrao_regra = "muita energia"

        # Alimento com muito carboidrato mas compensado por fibra ou proteina
        elif is_carboidrato_alto and (not is_fibra_baixa or is_proteina_alta):
            risco = "AMARELO"
            classificacao = "Risco Moderado (Alto Carboidrato Compensado)"
            padrao_regra = "parcialmente compensado"

        # Alimento com apenas um fator de risco isolado como so sodio ou so gordura
        elif (is_sodio_alto and not is_gordura_alta and not is_carboidrato_alto and not is_fibra_baixa) or \
                (is_gordura_alta and not is_sodio_alto and not is_carboidrato_alto and not is_fibra_baixa):
            risco = "AMARELO"
            classificacao = "Risco Moderado (Fator Isolado)"
            padrao_regra = "Apresenta um fator de risco isolado"

        # Regras para risco verde

        # Perfil ideal com riscos controlados e bons nutrientes
        elif not is_sodio_alto and not is_gordura_alta and not is_carboidrato_alto and (
                is_fibra_baixa or is_proteina_alta):
            risco = "VERDE"
            classificacao = "Risco Baixo (Perfil Ideal)"
            padrao_regra = "Fibra OU Proteína alta"

        # Todos os fatores de risco estao baixos
        elif not is_sodio_alto and not is_gordura_alta and not is_carboidrato_alto:
            risco = "VERDE"
            classificacao = "Risco Baixo (Fatores Controlados)"
            padrao_regra = "Todos os fatores críticos"

        # Caso nao caia em nenhuma regra anterior mantem verde
        else:
            risco = "VERDE"
            classificacao = "Risco Baixo (Outros Fatores)"
            padrao_regra = "Todos os fatores críticos"

        # Busca o texto completo da regra no banco de dados para exibir ao usuario
        descricao = self._buscar_descricao_regra(risco, padrao_regra)

        return risco, classificacao, descricao, sodio, gordura, fibra, proteina, carboidrato