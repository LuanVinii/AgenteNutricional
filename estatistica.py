import math
from collections import Counter


def calcular_media(dados: list[float]) -> float:
    # Faz a conta da media somando tudo e dividindo pela quantidade
    if not dados:
        return 0.0
    return sum(dados) / len(dados)


def calcular_variancia_e_desvio(dados: list[float]) -> tuple[float, float]:
    # Calcula o quanto os numeros variam da media
    if len(dados) < 2:
        return 0.0, 0.0

    media = calcular_media(dados)

    # Soma as diferencas ao quadrado
    soma_diferencas_quadrado = sum([(x - media) ** 2 for x in dados])

    # Divide pelo total menos um
    variancia = soma_diferencas_quadrado / (len(dados) - 1)

    # Tira a raiz quadrada pra achar o desvio
    desvio_padrao = math.sqrt(variancia)

    return variancia, desvio_padrao


def calcular_moda(dados: list[float]):
    # Acha o numero que mais se repete na lista
    if not dados:
        return None

    contagem = Counter(dados)
    max_contagem = max(contagem.values())
    modas = [chave for chave, valor in contagem.items() if valor == max_contagem]

    if len(modas) == len(dados):
        return None
    return modas