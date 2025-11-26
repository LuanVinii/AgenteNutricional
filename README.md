# AgenteNutricional

Este é um projeto de Sistema Inteligente desenvolvido em Python, focado na análise e classificação do risco nutricional de alimentos com base em seus dados de composição. O sistema utiliza um Agente Baseado em Regras para determinar, em tempo real, se um alimento se enquadra nas categorias de Risco Baixo (Verde), Risco Moderado (Amarelo) ou Risco Alto (Vermelho), auxiliando na tomada de decisões alimentares.

## Componentes e Funcionalidades

A aplicação é estruturada em módulos que se integram para prover análise e persistência de dados:

- main.py: Ponto de entrada do sistema. Responsável por inicializar o banco de dados, carregar os dados de um arquivo CSV e iniciar a interface de linha de comando (CLI).

- database.py (AlimentoRepository): Camada de persistência. Gerencia a conexão com o banco de dados (SQLite) utilizando SQLAlchemy como Object-Relational Mapper (ORM). É responsável por criar o esquema e as tabelas, e fornece métodos para buscar dados nutricionais e regras de classificação.

- agente.py (AgenteDeRisco): O núcleo de inteligência. Implementa a lógica condicional (IF-THEN) que compara os nutrientes dos alimentos com limiares de classificação (sódio, gordura saturada, fibra, etc.) para atribuir a cor de risco final.

- estatistica.py: Módulo de análise estatística. Calcula medidas de dispersão (média, variância, desvio padrão) para fornecer insights sobre a distribuição global dos nutrientes na base de dados.

- cli.py: Interface de Linha de Comando que permite ao usuário interagir com o sistema, consultar alimentos e visualizar as análises estatísticas.
