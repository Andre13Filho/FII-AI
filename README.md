# FII AI - Recomendador de Fundos Imobiliários

FII AI é uma aplicação de trading quantitativo voltada para fundos imobiliários que utiliza inteligência artificial para recomendar uma carteira diversificada de FIIs com base no patrimônio do investidor.

## Visão Geral

A aplicação utiliza:

- **Streamlit** para a interface com o usuário
- **LangChain** para integração com modelos de linguagem (LLM)
- **API da Groq (LLaMA 3)** para processamento de linguagem natural
- **API da Brapi** para obter dados de FIIs
- **Web Scraping** do site Status Invest como fonte complementar de dados
- **Sistema de rastreamento de investimentos** para armazenar e analisar suas operações

## Funcionalidades

### Recomendação de Carteira

- Solicita ao usuário o patrimônio disponível para investimento
- Utiliza uma LLM (LLaMA 3 via Groq) para interagir com o usuário e entender o contexto
- Pesquisa os melhores fundos imobiliários de diferentes categorias:
  - Fundos de CRI
  - Fundos de Shopping
  - Fundos de Logística
  - Fundos de Escritório
  - Fundos de Renda Urbana
  - Fundos de Fundos (FoF)
- Calcula a alocação ideal da carteira seguindo uma distribuição recomendada:
  - 27% em Fundos CRI
  - 17% em Fundos de Shopping
  - 17% em Fundos de Logística
  - 16% em Fundos de Escritório
  - 9% em Renda Urbana
  - 14% em FoF
- Apresenta visualizações interativas da carteira recomendada

### Rastreamento de Investimentos

- Registra compras e vendas de FIIs na sua carteira
- Calcula preço médio e mantém histórico de transações
- Exibe a composição atual da sua carteira com visualizações
- Análise de desempenho com preços atuais do mercado
- Histórico completo de operações

### Análise Inteligente de Portfólio

- Análise do balanceamento da carteira atual
- Recomendações para rebalanceamento baseadas na alocação ideal
- Sugestões específicas de FIIs para compra
- Análise detalhada da IA sobre sua carteira atual
- Recomendações personalizadas para melhorar performance e diversificação

## Pré-requisitos

- Python 3.8+
- Bibliotecas Python (listadas em `requirements.txt`)
- Chave API da Groq (para acesso ao modelo LLaMA 3)
- Chave API da Brapi (opcional, mas recomendado)

## Instalação

1. Clone o repositório:

```
git clone https://github.com/seu-usuario/fii-ai.git
cd fii-ai
```

2. Instale as dependências:

```
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
GROQ_API_KEY=sua_chave_aqui
BRAPI_API_KEY=sua_chave_aqui  # Opcional
```

## Executando a Aplicação

Execute o aplicativo Streamlit:

```
streamlit run app.py
```

## Estrutura do Projeto

```
fii-ai/
├── app.py                # Aplicação Streamlit principal
├── requirements.txt      # Dependências do projeto
├── .env                  # Variáveis de ambiente (não versionado)
├── README.md             # Este arquivo
├── agents/               # Agentes de IA
│   ├── llm_agent.py      # Agente de linguagem natural (LLM - LLaMA 3)
│   ├── market_agent.py   # Agentes de consulta de mercado (Brapi e Status Invest)
│   ├── portfolio_agent.py # Agente de cálculo de portfólio
│   ├── investment_agent.py # Agente de rastreamento de investimentos
│   └── portfolio_analysis_agent.py # Agente de análise de portfólio
├── utils/                # Utilitários
│   ├── constants.py      # Constantes e configurações
│   └── helpers.py        # Funções auxiliares
└── data/                 # Dados e caches (gerados em tempo de execução)
    ├── __init__.py       # Arquivo de inicialização do pacote
    └── investment_tracker.py # Módulo de rastreamento de investimentos
```

## Uso da Aplicação

### Recomendação de Carteira

1. Informe seu patrimônio total disponível
2. Clique em "Analisar e Recomendar"
3. Visualize a carteira recomendada e suas métricas
4. Adicione os FIIs recomendados à sua carteira com um clique

### Gerenciamento de Investimentos

1. Acesse a aba "Meus Investimentos"
2. Registre suas operações de compra e venda
3. Visualize sua carteira atual e o histórico de operações
4. Analise o desempenho da sua carteira comparando com preços atuais

### Análise de Portfólio

1. Acesse a aba "Análise de Portfólio"
2. Solicite uma análise da sua carteira atual
3. Obtenha recomendações para rebalanceamento
4. Receba análises personalizadas da IA sobre sua estratégia

## Armazenamento de Dados

- Todos os dados são armazenados localmente em arquivos JSON
- Seu histórico de investimentos é preservado entre sessões
- Não há compartilhamento de dados com servidores externos

## Limitações e Considerações

- Esta aplicação é para fins educativos e não constitui recomendação de investimentos
- As recomendações são baseadas em dados históricos e podem não refletir o desempenho futuro
- O web scraping depende da estrutura do site Status Invest, que pode mudar ao longo do tempo
- A API da Brapi tem limitações de requisições na versão gratuita

## Próximos Passos

- Adicionar análise de risco para cada FII
- Implementar mais fontes de dados
- Criar backtesting para validar as recomendações
- Adicionar mais métricas para avaliação dos FIIs
- Implementar sincronização com corretoras
- Adicionar alertas de preço e dividendos

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

MIT
