import os
import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from utils.constants import FII_TYPES
from agents.status_invest_scraper import StatusInvestScraper

class BrapiAgent:
    """
    Agente especializado em obter dados de FIIs através da API da Brapi.
    Incorpora análise histórica, notícias e dados fundamentalistas.
    """
    def __init__(self):
        self.api_key = os.getenv("BRAPI_API_KEY")
        self.base_url = "https://brapi.dev/api"
        self.scraper = StatusInvestScraper()  # Inicializar o scraper para dados adicionais
        
        # Se não houver chave, usar a versão gratuita com limite de requisições
        if not self.api_key:
            print("Aviso: BRAPI_API_KEY não encontrada. Usando API com limite de requisições.")
    
    def get_best_fiis(self, fii_type):
        """
        Obtém os melhores FIIs de um determinado tipo baseado em múltiplos critérios:
        - Dividend Yield atual
        - P/VP
        - Liquidez
        - Vacância
        - Histórico de preços e dividendos
        - Análise de notícias
        - Dados fundamentalistas
        
        Args:
            fii_type (str): Tipo de FII (cri, shopping, logistica, escritorio)
            
        Returns:
            list: Lista dos 5 melhores FIIs do tipo especificado
        """
        # Mapear o tipo de FII para os tickers correspondentes
        fii_tickers = self._get_fii_tickers_by_type(fii_type)
        
        print(f"\n=== Iniciando análise completa de FIIs do tipo {fii_type.upper()} ===")
        
        # Tentar obter dados reais da API
        fiis_data = []
        try:
            for ticker in fii_tickers:
                print(f"\nAnalisando {ticker}...")
                # 1. Obter dados básicos da API
                fii_data = self._get_fii_data(ticker)
                
                if fii_data:
                    # 2. Enriquecer com dados históricos
                    historical_data = self.scraper.get_historical_data(ticker)
                    
                    # 3. Obter notícias recentes
                    news_data = self.scraper.get_news(ticker)
                    
                    # 4. Obter dados fundamentalistas
                    fundamental_data = self.scraper.get_fundamental_data(ticker)
                    
                    # 5. Combinar todos os dados
                    fii_data.update({
                        "historical": historical_data.get("metrics", {}),
                        "news": self._analyze_news(news_data),
                        "fundamentals": fundamental_data
                    })
                    
                    fiis_data.append(fii_data)
                else:
                    print(f"Sem dados básicos disponíveis para {ticker}, usando dados simulados")
                    # Criar um conjunto completo de dados simulados
                    sim_data = self._create_complete_simulated_data(ticker, fii_type)
                    fiis_data.append(sim_data)
            
            # Se não conseguiu obter dados da API, usar dados simulados para todos os tickers
            if not fiis_data:
                print(f"Não foi possível obter dados reais para {fii_type}. Usando dados simulados para todos.")
                for ticker in fii_tickers:
                    sim_data = self._create_complete_simulated_data(ticker, fii_type)
                    fiis_data.append(sim_data)
                    
        except Exception as e:
            print(f"Erro ao acessar API Brapi: {e}. Usando dados simulados para todos.")
            for ticker in fii_tickers:
                sim_data = self._create_complete_simulated_data(ticker, fii_type)
                fiis_data.append(sim_data)
        
        # Filtrar e ordenar os FIIs por critérios avançados (análise completa)
        sorted_fiis = self._sort_fiis_by_advanced_criteria(fiis_data, fii_type)
        
        print(f"\n=== Resultado da análise de FIIs do tipo {fii_type.upper()} ===")
        for i, fii in enumerate(sorted_fiis[:5], 1):
            print(f"{i}. {fii['ticker']} - Score: {fii.get('final_score', 0):.2f}")
        
        # Retornar os 5 melhores
        return sorted_fiis[:5]
    
    def _get_fii_tickers_by_type(self, fii_type):
        """
        Retorna uma lista de tickers de FIIs com base no tipo especificado.
        Na implementação real, isso poderia ser uma chamada à API ou usar
        uma base de dados local.
        """
        # Nesta versão simplificada, usamos um dicionário predefinido
        return FII_TYPES.get(fii_type, [])
    
    def _get_dummy_fii_data(self, tickers, fii_type):
        """
        Gera dados de exemplo para os FIIs, como uma alternativa à API real.
        
        Args:
            tickers (list): Lista de tickers de FIIs
            fii_type (str): Tipo de FII
            
        Returns:
            list: Lista de dicionários com dados de FIIs
        """
        result = []
        
        # Parâmetros de exemplo para cada tipo
        params = {
            "cri": {
                "dividend_yield_range": (0.08, 0.12),  # 8% a 12%
                "price_range": (80, 120),
                "p_vp_range": (0.85, 1.15)
            },
            "shopping": {
                "dividend_yield_range": (0.06, 0.1),   # 6% a 10%
                "price_range": (90, 130),
                "p_vp_range": (0.8, 1.1)
            },
            "logistica": {
                "dividend_yield_range": (0.07, 0.11),  # 7% a 11%
                "price_range": (85, 125),
                "p_vp_range": (0.75, 1.05)
            },
            "escritorio": {
                "dividend_yield_range": (0.065, 0.095), # 6.5% a 9.5%
                "price_range": (75, 115),
                "p_vp_range": (0.7, 1.0)
            },
            "renda_urbana": {
                "dividend_yield_range": (0.075, 0.105), # 7.5% a 10.5%
                "price_range": (95, 140),
                "p_vp_range": (0.9, 1.2)
            },
            "fof": {
                "dividend_yield_range": (0.07, 0.1),    # 7% a 10%
                "price_range": (90, 135),
                "p_vp_range": (0.95, 1.25)
            }
        }
        
        # Usar parâmetros do tipo especificado ou padrão se não existir
        type_params = params.get(fii_type, params["cri"])
        
        # Gerar dados para cada ticker
        for i, ticker in enumerate(tickers):
            # Aleatorizar dados realistas para cada FII
            dy_range = type_params["dividend_yield_range"]
            price_range = type_params["price_range"]
            pvp_range = type_params["p_vp_range"]
            
            dividend_yield = round(np.random.uniform(dy_range[0], dy_range[1]), 4)
            price = round(np.random.uniform(price_range[0], price_range[1]), 2)
            priceToBookRatio = round(np.random.uniform(pvp_range[0], pvp_range[1]), 2)
            
            # Dados de exemplo para um FII
            fii_data = {
                "ticker": ticker,
                "name": f"FII {ticker}",
                "price": price,
                "dividendYield": dividend_yield,
                "priceToBookRatio": priceToBookRatio,
                "liquidity": round(np.random.uniform(50000, 500000), 2),
                "sector": fii_type.capitalize()
            }
            
            result.append(fii_data)
        
        return result
    
    def _get_fii_data(self, ticker):
        """
        Obtém dados reais de um FII através da API Brapi.
        
        Args:
            ticker (str): Ticker do FII
            
        Returns:
            dict: Dados do FII ou None em caso de erro
        """
        # Construir a URL correta para FIIs na B3
        endpoint = f"/quote/{ticker}.SA"  # Adiciona .SA ao ticker para o formato correto
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if self.api_key:
            params["token"] = self.api_key
            
        try:
            print(f"Buscando dados para {ticker} em: {url}")
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lança exceção para erros HTTP
            
            data = response.json()
            
            # Verificar se a resposta tem o formato esperado
            if "results" in data and len(data["results"]) > 0:
                fii_data = data["results"][0]
                
                # Extrair dados relevantes
                extracted_data = {
                    "ticker": ticker,
                    "name": fii_data.get("longName", f"FII {ticker}"),
                    "price": fii_data.get("regularMarketPrice", 0.0),
                    "dividendYield": fii_data.get("dividendYield", 0.0) / 100 if "dividendYield" in fii_data else 0.0,
                    "priceToBookRatio": fii_data.get("priceToBook", 0.0),
                    "liquidity": fii_data.get("regularMarketVolume", 0.0)
                }
                
                print(f"Dados obtidos com sucesso para {ticker}")
                return extracted_data
            else:
                print(f"Formato de dados inesperado para {ticker}")
                return None
                
        except Exception as e:
            print(f"Erro ao obter dados para {ticker}: {e}")
            return None
    
    def _sort_fiis_by_criteria(self, fiis_data, fii_type):
        """
        Ordena os FIIs com base em critérios específicos para cada tipo,
        utilizando uma análise mais completa e ponderada de múltiplos fatores.
        """
        if not fiis_data:
            return []
            
        # Converter para DataFrame para facilitar a manipulação
        df = pd.DataFrame(fiis_data)
        
        # Verificar se temos as colunas mínimas necessárias
        required_columns = ["ticker", "price"]
        if not all(col in df.columns for col in required_columns):
            print(f"Dados insuficientes para análise completa de {fii_type}")
            return fiis_data
        
        # Garantir que temos colunas numéricas com valores padrão se necessário
        if "dividendYield" not in df.columns:
            df["dividendYield"] = 0.0
        if "priceToBookRatio" not in df.columns:
            df["priceToBookRatio"] = 1.0
        if "liquidity" not in df.columns:
            df["liquidity"] = 0.0
            
        # Adicionar métricas calculadas para análise mais completa
        
        # 1. Normalizar métricas para comparação justa (escala 0-1)
        # Dividend Yield - maior é melhor
        if df["dividendYield"].max() > df["dividendYield"].min():
            df["dy_norm"] = (df["dividendYield"] - df["dividendYield"].min()) / (df["dividendYield"].max() - df["dividendYield"].min())
        else:
            df["dy_norm"] = df["dividendYield"] / df["dividendYield"].max() if df["dividendYield"].max() > 0 else 0
            
        # P/VP - menor é melhor, mas não muito baixo (pode indicar problemas)
        # Valores ideais entre 0.7 e 1.1
        df["pvp_ideal"] = df["priceToBookRatio"].apply(
            lambda x: 1.0 if 0.7 <= x <= 1.1 else max(0, 1 - abs(x - 0.9) / 0.5)
        )
        
        # Liquidez - maior é melhor
        if df["liquidity"].max() > df["liquidity"].min():
            df["liq_norm"] = (df["liquidity"] - df["liquidity"].min()) / (df["liquidity"].max() - df["liquidity"].min())
        else:
            df["liq_norm"] = df["liquidity"] / df["liquidity"].max() if df["liquidity"].max() > 0 else 0
            
        # 2. Calcular pontuações específicas por tipo de FII
        if fii_type == "cri":
            # FIIs de CRI: foco em rendimento e consistência
            # Pesos: 60% DY, 20% P/VP ideal, 20% Liquidez
            df["score"] = (
                0.60 * df["dy_norm"] + 
                0.20 * df["pvp_ideal"] + 
                0.20 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de CRI:")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
                
        elif fii_type == "shopping":
            # FIIs de Shopping: foco em valor patrimonial e potencial de valorização
            # Pesos: 40% P/VP ideal, 30% DY, 30% Liquidez
            df["score"] = (
                0.40 * df["pvp_ideal"] + 
                0.30 * df["dy_norm"] + 
                0.30 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de Shopping:")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
            
        elif fii_type == "logistica":
            # FIIs de Logística: equilíbrio entre valor e rendimento
            # Pesos: 40% DY, 40% P/VP ideal, 20% Liquidez
            df["score"] = (
                0.40 * df["dy_norm"] + 
                0.40 * df["pvp_ideal"] + 
                0.20 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de Logística:")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
            
        elif fii_type == "escritorio":
            # FIIs de Escritório: mais conservador, foco em valor
            # Pesos: 50% P/VP ideal, 30% DY, 20% Liquidez
            df["score"] = (
                0.50 * df["pvp_ideal"] + 
                0.30 * df["dy_norm"] + 
                0.20 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de Escritório:")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
            
        elif fii_type == "renda_urbana":
            # FIIs de Renda Urbana: foco em rendimento consistente
            # Pesos: 50% DY, 30% P/VP ideal, 20% Liquidez
            df["score"] = (
                0.50 * df["dy_norm"] + 
                0.30 * df["pvp_ideal"] + 
                0.20 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de Renda Urbana:")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
            
        elif fii_type == "fof":
            # FIIs de Fundos: diversificação e valor
            # Pesos: 40% DY, 40% P/VP ideal, 20% Liquidez
            df["score"] = (
                0.40 * df["dy_norm"] + 
                0.40 * df["pvp_ideal"] + 
                0.20 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de Fundos (FOF):")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
        
        else:
            # Caso padrão: equilíbrio entre rendimento e valor
            df["score"] = (
                0.45 * df["dy_norm"] + 
                0.35 * df["pvp_ideal"] + 
                0.20 * df["liq_norm"]
            )
            
            print(f"Análise de FIIs de tipo {fii_type}:")
            for _, row in df.sort_values(by="score", ascending=False).head().iterrows():
                print(f"{row['ticker']}: Score={row['score']:.2f}, DY={row['dividendYield']*100:.2f}%, P/VP={row['priceToBookRatio']:.2f}")
        
        # Ordenar por pontuação e retornar como dicionários
        return df.sort_values(by="score", ascending=False).to_dict("records")

    def _create_complete_simulated_data(self, ticker, fii_type):
        """
        Cria um conjunto completo de dados simulados para um FII.
        
        Args:
            ticker (str): Ticker do FII
            fii_type (str): Tipo do FII
            
        Returns:
            dict: Dados completos simulados
        """
        # 1. Obter dados básicos simulados
        basic_data = self._get_dummy_fii_data([ticker], fii_type)[0]
        
        # 2. Obter dados históricos simulados
        historical_data = self.scraper.get_historical_data(ticker)
        
        # 3. Obter notícias simuladas
        news_data = self.scraper.get_news(ticker)
        
        # 4. Obter dados fundamentalistas simulados
        fundamental_data = self.scraper.get_fundamental_data(ticker)
        
        # 5. Combinar todos os dados
        basic_data.update({
            "historical": historical_data.get("metrics", {}),
            "news": self._analyze_news(news_data),
            "fundamentals": fundamental_data
        })
        
        return basic_data
    
    def _analyze_news(self, news_data):
        """
        Analisa o sentimento e a relevância das notícias.
        
        Args:
            news_data (list): Lista de notícias
            
        Returns:
            dict: Análise das notícias
        """
        if not news_data:
            return {
                "sentiment_score": 0.0,
                "recent_sentiment": "neutral",
                "news_count": 0
            }
        
        # Contar notícias por sentimento
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        # Pesos para recência das notícias (mais recentes têm mais peso)
        recency_weights = []
        
        for i, news in enumerate(news_data):
            sentiment = news.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1
            
            # Peso de recência (decai exponencialmente)
            recency_weight = np.exp(-i * 0.3)  # Aproximadamente 1.0, 0.74, 0.55, 0.41, 0.30, ...
            recency_weights.append((sentiment, recency_weight))
        
        # Calcular pontuação de sentimento (de -1 a 1)
        total_news = len(news_data)
        sentiment_score = (
            sentiment_counts["positive"] - sentiment_counts["negative"]
        ) / total_news if total_news > 0 else 0.0
        
        # Determinar sentimento recente (das 3 notícias mais recentes)
        recent_sentiments = [s for s, _ in recency_weights[:3]]
        if recent_sentiments.count("positive") > recent_sentiments.count("negative"):
            recent_sentiment = "positive"
        elif recent_sentiments.count("negative") > recent_sentiments.count("positive"):
            recent_sentiment = "negative"
        else:
            recent_sentiment = "neutral"
        
        return {
            "sentiment_score": sentiment_score,
            "recent_sentiment": recent_sentiment,
            "news_count": total_news
        }

    def _sort_fiis_by_advanced_criteria(self, fiis_data, fii_type):
        """
        Ordena os FIIs com base em critérios avançados, incluindo:
        - Métricas atuais (DY, P/VP, liquidez)
        - Histórico de preços e dividendos
        - Análise de notícias
        - Dados fundamentalistas
        
        Esta análise é muito mais completa que a anterior e considera
        o desempenho histórico e perspectivas futuras.
        """
        if not fiis_data:
            return []
            
        # Converter para DataFrame para facilitar a manipulação
        df = pd.DataFrame(fiis_data)
        
        # Verificar se temos as colunas mínimas necessárias
        required_columns = ["ticker"]
        if not all(col in df.columns for col in required_columns):
            print(f"Dados insuficientes para análise completa de {fii_type}")
            return fiis_data
        
        # Criar colunas para todas as métricas que queremos analisar
        # 1. Métricas básicas
        self._ensure_numeric_columns(df, [
            "dividendYield", "priceToBookRatio", "liquidity", "price"
        ])
        
        # 2. Extrair métricas históricas
        df["price_trend"] = df.apply(lambda x: 
            x.get("historical", {}).get("price_trend_pct", 0), axis=1)
            
        df["price_volatility"] = df.apply(lambda x: 
            x.get("historical", {}).get("volatility", 10), axis=1)
            
        df["dividend_consistency"] = df.apply(lambda x: 
            x.get("historical", {}).get("current_dividend_yield", 0) / 
            (x.get("dividendYield", 0.01) * 100) if x.get("dividendYield", 0) > 0 else 0, 
            axis=1)
            
        # 3. Métricas de notícias
        df["news_sentiment"] = df.apply(lambda x: 
            x.get("news", {}).get("sentiment_score", 0), axis=1)
            
        df["recent_sentiment"] = df.apply(lambda x: 
            1 if x.get("news", {}).get("recent_sentiment", "neutral") == "positive" else
            -1 if x.get("news", {}).get("recent_sentiment", "neutral") == "negative" else 0,
            axis=1)
            
        # 4. Métricas fundamentalistas
        df["vacancy_rate"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("vacancy_rate", 0.1), axis=1)
            
        df["diversification"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("diversification", 5), axis=1)
            
        df["cap_rate"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("cap_rate", 0.08), axis=1)
            
        df["contract_duration"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("average_contract_duration", 5), axis=1)
            
        # Normalizar todas as métricas para uma escala de 0-1
        metrics_to_normalize = {
            # Métricas onde maior é melhor
            "higher_better": [
                "dividendYield", "liquidity", "price_trend", "dividend_consistency",
                "news_sentiment", "recent_sentiment", "diversification", "cap_rate",
                "contract_duration"
            ],
            # Métricas onde menor é melhor
            "lower_better": [
                "price_volatility", "vacancy_rate"
            ],
            # Métricas com valor ideal (nem muito alto nem muito baixo)
            "ideal_value": {
                "priceToBookRatio": 0.9  # Valor ideal para P/VP
            }
        }
        
        # Normalizar métricas
        for metric in metrics_to_normalize["higher_better"]:
            if metric in df.columns and df[metric].max() > df[metric].min():
                df[f"{metric}_norm"] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
            else:
                df[f"{metric}_norm"] = df[metric] / df[metric].max() if df[metric].max() > 0 else 0
        
        for metric in metrics_to_normalize["lower_better"]:
            if metric in df.columns and df[metric].max() > df[metric].min():
                df[f"{metric}_norm"] = 1 - (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
            else:
                df[f"{metric}_norm"] = 1 - (df[metric] / df[metric].max()) if df[metric].max() > 0 else 0
        
        for metric, ideal in metrics_to_normalize["ideal_value"].items():
            if metric in df.columns:
                df[f"{metric}_norm"] = 1 - abs(df[metric] - ideal) / max(abs(df[metric].max() - ideal), abs(df[metric].min() - ideal))
        
        # Definir pesos diferentes para cada tipo de FII
        weights = self._get_weights_by_fii_type(fii_type)
        
        # Calcular pontuação final combinando todas as métricas normalizadas
        df["final_score"] = 0
        
        for metric, weight in weights.items():
            norm_metric = f"{metric}_norm"
            if norm_metric in df.columns:
                df["final_score"] += df[norm_metric] * weight
        
        # Mostrar detalhes da análise para os melhores FIIs
        print("\n==== Detalhes da Análise Avançada ====")
        for _, row in df.sort_values(by="final_score", ascending=False).head().iterrows():
            ticker = row["ticker"]
            score = row["final_score"]
            
            # Formatar métricas principais para exibição
            dy = row.get("dividendYield", 0) * 100 if "dividendYield" in row else 0
            pvp = row.get("priceToBookRatio", 0) if "priceToBookRatio" in row else 0
            price_trend = row.get("price_trend", 0)
            sentiment = row.get("news_sentiment", 0)
            
            print(f"\n{ticker} - Score: {score:.2f}")
            print(f"DY: {dy:.2f}% | P/VP: {pvp:.2f} | Tendência: {price_trend:.2f}% | Sentimento: {sentiment:.2f}")
            
            # Mostrar pontos fortes e fracos
            strengths = []
            weaknesses = []
            
            for metric, weight in weights.items():
                norm_metric = f"{metric}_norm"
                if norm_metric in df.columns and weight > 0.02:  # Mostrar apenas métricas relevantes
                    norm_value = row.get(norm_metric, 0)
                    if norm_value > 0.7:
                        strengths.append(f"{metric} ({norm_value:.2f})")
                    elif norm_value < 0.3:
                        weaknesses.append(f"{metric} ({norm_value:.2f})")
            
            print("Pontos fortes: " + ", ".join(strengths[:3]) if strengths else "Nenhum ponto forte destacado")
            print("Pontos fracos: " + ", ".join(weaknesses[:3]) if weaknesses else "Nenhum ponto fraco destacado")
        
        # Ordenar por pontuação e retornar como dicionários
        sorted_df = df.sort_values(by="final_score", ascending=False)
        
        # Adicionar coluna de ranking
        sorted_df["ranking"] = range(1, len(sorted_df) + 1)
        
        return sorted_df.to_dict("records")
    
    def _ensure_numeric_columns(self, df, columns):
        """
        Garante que as colunas especificadas sejam numéricas,
        convertendo-as ou preenchendo com valores padrão.
        """
        for col in columns:
            if col not in df.columns:
                df[col] = 0.0
            else:
                # Converter para numérico com valor padrão para erros
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    
    def _get_weights_by_fii_type(self, fii_type):
        """
        Retorna os pesos para cada métrica de acordo com o tipo de FII.
        
        Estes pesos definem a importância relativa de cada fator na
        pontuação final. Os pesos são baseados em práticas comuns de
        avaliação para cada tipo de fundo.
        """
        if fii_type == "cri":
            return {
                "dividendYield": 0.20,            # Rendimento atual
                "priceToBookRatio": 0.10,         # Valor patrimonial
                "liquidity": 0.05,                # Liquidez (menos importante para renda fixa)
                "price_trend": 0.05,              # Tendência de preço
                "price_volatility": 0.10,         # Volatilidade (menor é melhor)
                "dividend_consistency": 0.15,     # Consistência dos dividendos
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.00,             # Não se aplica a CRIs
                "diversification": 0.15,          # Diversificação de devedores
                "cap_rate": 0.10,                 # Taxa de retorno
                "contract_duration": 0.00         # Não relevante para CRIs
            }
        
        elif fii_type == "shopping":
            return {
                "dividendYield": 0.15,            # Rendimento atual
                "priceToBookRatio": 0.15,         # Valor patrimonial (importante para imóveis)
                "liquidity": 0.05,                # Liquidez
                "price_trend": 0.10,              # Tendência de preço
                "price_volatility": 0.05,         # Volatilidade
                "dividend_consistency": 0.10,     # Consistência dos dividendos
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.15,             # Vacância (crítico para shoppings)
                "diversification": 0.05,          # Diversificação de ativos
                "cap_rate": 0.05,                 # Taxa de retorno
                "contract_duration": 0.05         # Duração média dos contratos
            }
        
        elif fii_type == "logistica":
            return {
                "dividendYield": 0.15,            # Rendimento atual
                "priceToBookRatio": 0.15,         # Valor patrimonial
                "liquidity": 0.05,                # Liquidez
                "price_trend": 0.10,              # Tendência de preço
                "price_volatility": 0.05,         # Volatilidade
                "dividend_consistency": 0.10,     # Consistência dos dividendos
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.15,             # Vacância (crítico para galpões)
                "diversification": 0.05,          # Diversificação geográfica
                "cap_rate": 0.05,                 # Taxa de retorno
                "contract_duration": 0.05         # Duração média dos contratos
            }
        
        elif fii_type == "escritorio":
            return {
                "dividendYield": 0.10,            # Rendimento atual
                "priceToBookRatio": 0.15,         # Valor patrimonial
                "liquidity": 0.05,                # Liquidez
                "price_trend": 0.10,              # Tendência de preço
                "price_volatility": 0.05,         # Volatilidade
                "dividend_consistency": 0.10,     # Consistência dos dividendos
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.20,             # Vacância (crítico para escritórios)
                "diversification": 0.05,          # Diversificação
                "cap_rate": 0.05,                 # Taxa de retorno
                "contract_duration": 0.05         # Duração média dos contratos
            }
        
        elif fii_type == "renda_urbana":
            return {
                "dividendYield": 0.15,            # Rendimento atual
                "priceToBookRatio": 0.10,         # Valor patrimonial
                "liquidity": 0.05,                # Liquidez
                "price_trend": 0.05,              # Tendência de preço
                "price_volatility": 0.05,         # Volatilidade
                "dividend_consistency": 0.15,     # Consistência dos dividendos (importante)
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.10,             # Vacância
                "diversification": 0.05,          # Diversificação
                "cap_rate": 0.10,                 # Taxa de retorno
                "contract_duration": 0.10         # Duração média dos contratos (contratos atípicos)
            }
        
        elif fii_type == "fof":
            return {
                "dividendYield": 0.15,            # Rendimento atual
                "priceToBookRatio": 0.15,         # Valor patrimonial
                "liquidity": 0.10,                # Liquidez (mais importante para FoFs)
                "price_trend": 0.10,              # Tendência de preço
                "price_volatility": 0.10,         # Volatilidade
                "dividend_consistency": 0.15,     # Consistência dos dividendos
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.00,             # Não se aplica diretamente
                "diversification": 0.15,          # Diversificação (crítico para FoFs)
                "cap_rate": 0.00,                 # Não se aplica diretamente
                "contract_duration": 0.00         # Não se aplica
            }
        
        else:  # Tipo genérico/desconhecido
            return {
                "dividendYield": 0.15,
                "priceToBookRatio": 0.15,
                "liquidity": 0.10,
                "price_trend": 0.10,
                "price_volatility": 0.05,
                "dividend_consistency": 0.10,
                "news_sentiment": 0.05,
                "recent_sentiment": 0.05,
                "vacancy_rate": 0.10,
                "diversification": 0.05,
                "cap_rate": 0.05,
                "contract_duration": 0.05
            }


class StatusInvestAgent:
    """
    Agente especializado em obter dados de FIIs através de web scraping do Status Invest.
    Incorpora análise histórica, notícias e dados fundamentalistas.
    """
    def __init__(self):
        self.base_url = "https://statusinvest.com.br"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.scraper = StatusInvestScraper()  # Inicializar o scraper para dados adicionais
    
    def get_best_fiis(self, fii_type):
        """
        Obtém os melhores FIIs de um tipo específico via web scraping.
        Incorpora análise histórica, notícias e dados fundamentalistas.
        
        Args:
            fii_type (str): Tipo de FII (renda_urbana, fof)
            
        Returns:
            list: Lista dos 5 melhores FIIs do tipo especificado
        """
        print(f"\n=== Iniciando análise completa de FIIs do tipo {fii_type.upper()} (Status Invest) ===")
        
        # Obter lista de FIIs do tipo especificado
        fii_list = self._get_fii_list_by_type(fii_type)
        
        # Obter dados detalhados para cada FII
        fiis_data = []
        for ticker in fii_list:
            print(f"\nAnalisando {ticker}...")
            
            # Criar dados completos para o FII
            fii_data = self._create_complete_simulated_data(ticker, fii_type)
            fiis_data.append(fii_data)
                
        # Ordenar FIIs conforme critérios avançados
        sorted_fiis = self._sort_fiis_by_advanced_criteria(fiis_data, fii_type)
        
        print(f"\n=== Resultado da análise de FIIs do tipo {fii_type.upper()} (Status Invest) ===")
        for i, fii in enumerate(sorted_fiis[:5], 1):
            print(f"{i}. {fii['ticker']} - Score: {fii.get('final_score', 0):.2f}")
        
        # Retornar os 5 melhores
        return sorted_fiis[:5]
    
    def _get_fii_list_by_type(self, fii_type):
        """
        Obtém a lista de tickers de FIIs do tipo especificado.
        
        Na implementação real, isso faria uma requisição à página de filtro
        do Status Invest e extrairia os tickers através de web scraping.
        """
        # Versão simplificada - em produção, faria scraping real
        # Nesta versão dummy, usamos o dicionário predefinido
        return FII_TYPES.get(fii_type, [])
    
    def _create_complete_simulated_data(self, ticker, fii_type):
        """
        Cria um conjunto completo de dados simulados para um FII.
        
        Args:
            ticker (str): Ticker do FII
            fii_type (str): Tipo do FII
            
        Returns:
            dict: Dados completos simulados
        """
        # 1. Obter dados básicos simulados
        basic_data = self._get_dummy_fii_details(ticker, fii_type)
        
        # 2. Obter dados históricos simulados
        historical_data = self.scraper.get_historical_data(ticker)
        
        # 3. Obter notícias simuladas
        news_data = self.scraper.get_news(ticker)
        
        # 4. Obter dados fundamentalistas simulados
        fundamental_data = self.scraper.get_fundamental_data(ticker)
        
        # 5. Combinar todos os dados
        basic_data.update({
            "historical": historical_data.get("metrics", {}),
            "news": self._analyze_news(news_data),
            "fundamentals": fundamental_data
        })
        
        return basic_data
    
    def _get_dummy_fii_details(self, ticker, fii_type):
        """
        Gera dados de exemplo para um FII específico.
        
        Args:
            ticker (str): Ticker do FII
            fii_type (str): Tipo do FII
            
        Returns:
            dict: Dicionário com dados do FII
        """
        # Parâmetros específicos para cada tipo de FII
        params = {
            "renda_urbana": {
                "dy_range": (0.075, 0.11),   # 7.5% a 11%
                "price_range": (95, 150),
                "pvp_range": (0.9, 1.2),
                "liquidity_range": (100000, 800000)
            },
            "fof": {
                "dy_range": (0.07, 0.10),    # 7% a 10%
                "price_range": (85, 135),
                "pvp_range": (0.95, 1.15),
                "liquidity_range": (150000, 1000000)
            }
        }
        
        # Obter parâmetros para o tipo específico ou usar padrão
        type_params = params.get(fii_type, params["fof"])
        
        # Gerar valores aleatórios dentro das faixas definidas
        dy = round(np.random.uniform(type_params["dy_range"][0], type_params["dy_range"][1]), 4)
        price = round(np.random.uniform(type_params["price_range"][0], type_params["price_range"][1]), 2)
        pvp = round(np.random.uniform(type_params["pvp_range"][0], type_params["pvp_range"][1]), 2)
        liquidity = round(np.random.uniform(type_params["liquidity_range"][0], type_params["liquidity_range"][1]), 2)
        
        # Compor dados do FII
        return {
            "ticker": ticker,
            "name": f"FII {ticker}",
            "price": price,
            "dividendYield": dy,
            "priceToBookRatio": pvp,
            "liquidity": liquidity,
            "sector": fii_type.replace("_", " ").title()
        }
    
    def _analyze_news(self, news_data):
        """
        Analisa o sentimento e a relevância das notícias.
        
        Args:
            news_data (list): Lista de notícias
            
        Returns:
            dict: Análise das notícias
        """
        if not news_data:
            return {
                "sentiment_score": 0.0,
                "recent_sentiment": "neutral",
                "news_count": 0
            }
        
        # Contar notícias por sentimento
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        # Pesos para recência das notícias (mais recentes têm mais peso)
        recency_weights = []
        
        for i, news in enumerate(news_data):
            sentiment = news.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1
            
            # Peso de recência (decai exponencialmente)
            recency_weight = np.exp(-i * 0.3)  # Aproximadamente 1.0, 0.74, 0.55, 0.41, 0.30, ...
            recency_weights.append((sentiment, recency_weight))
        
        # Calcular pontuação de sentimento (de -1 a 1)
        total_news = len(news_data)
        sentiment_score = (
            sentiment_counts["positive"] - sentiment_counts["negative"]
        ) / total_news if total_news > 0 else 0.0
        
        # Determinar sentimento recente (das 3 notícias mais recentes)
        recent_sentiments = [s for s, _ in recency_weights[:3]]
        if recent_sentiments.count("positive") > recent_sentiments.count("negative"):
            recent_sentiment = "positive"
        elif recent_sentiments.count("negative") > recent_sentiments.count("positive"):
            recent_sentiment = "negative"
        else:
            recent_sentiment = "neutral"
        
        return {
            "sentiment_score": sentiment_score,
            "recent_sentiment": recent_sentiment,
            "news_count": total_news
        }
    
    # Reutilizar os mesmos métodos do BrapiAgent para análise avançada
    def _sort_fiis_by_advanced_criteria(self, fiis_data, fii_type):
        """
        Ordena os FIIs com base em critérios avançados, incluindo:
        - Métricas atuais (DY, P/VP, liquidez)
        - Histórico de preços e dividendos
        - Análise de notícias
        - Dados fundamentalistas
        
        Esta análise é muito mais completa que a anterior e considera
        o desempenho histórico e perspectivas futuras.
        """
        if not fiis_data:
            return []
            
        # Converter para DataFrame para facilitar a manipulação
        df = pd.DataFrame(fiis_data)
        
        # Verificar se temos as colunas mínimas necessárias
        required_columns = ["ticker"]
        if not all(col in df.columns for col in required_columns):
            print(f"Dados insuficientes para análise completa de {fii_type}")
            return fiis_data
        
        # Criar colunas para todas as métricas que queremos analisar
        # 1. Métricas básicas
        self._ensure_numeric_columns(df, [
            "dividendYield", "priceToBookRatio", "liquidity", "price"
        ])
        
        # 2. Extrair métricas históricas
        df["price_trend"] = df.apply(lambda x: 
            x.get("historical", {}).get("price_trend_pct", 0), axis=1)
            
        df["price_volatility"] = df.apply(lambda x: 
            x.get("historical", {}).get("volatility", 10), axis=1)
            
        df["dividend_consistency"] = df.apply(lambda x: 
            x.get("historical", {}).get("current_dividend_yield", 0) / 
            (x.get("dividendYield", 0.01) * 100) if x.get("dividendYield", 0) > 0 else 0, 
            axis=1)
            
        # 3. Métricas de notícias
        df["news_sentiment"] = df.apply(lambda x: 
            x.get("news", {}).get("sentiment_score", 0), axis=1)
            
        df["recent_sentiment"] = df.apply(lambda x: 
            1 if x.get("news", {}).get("recent_sentiment", "neutral") == "positive" else
            -1 if x.get("news", {}).get("recent_sentiment", "neutral") == "negative" else 0,
            axis=1)
            
        # 4. Métricas fundamentalistas
        df["vacancy_rate"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("vacancy_rate", 0.1), axis=1)
            
        df["diversification"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("diversification", 5), axis=1)
            
        df["cap_rate"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("cap_rate", 0.08), axis=1)
            
        df["contract_duration"] = df.apply(lambda x: 
            x.get("fundamentals", {}).get("average_contract_duration", 5), axis=1)
            
        # Normalizar todas as métricas para uma escala de 0-1
        metrics_to_normalize = {
            # Métricas onde maior é melhor
            "higher_better": [
                "dividendYield", "liquidity", "price_trend", "dividend_consistency",
                "news_sentiment", "recent_sentiment", "diversification", "cap_rate",
                "contract_duration"
            ],
            # Métricas onde menor é melhor
            "lower_better": [
                "price_volatility", "vacancy_rate"
            ],
            # Métricas com valor ideal (nem muito alto nem muito baixo)
            "ideal_value": {
                "priceToBookRatio": 0.9  # Valor ideal para P/VP
            }
        }
        
        # Normalizar métricas
        for metric in metrics_to_normalize["higher_better"]:
            if metric in df.columns and df[metric].max() > df[metric].min():
                df[f"{metric}_norm"] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
            else:
                df[f"{metric}_norm"] = df[metric] / df[metric].max() if df[metric].max() > 0 else 0
        
        for metric in metrics_to_normalize["lower_better"]:
            if metric in df.columns and df[metric].max() > df[metric].min():
                df[f"{metric}_norm"] = 1 - (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
            else:
                df[f"{metric}_norm"] = 1 - (df[metric] / df[metric].max()) if df[metric].max() > 0 else 0
        
        for metric, ideal in metrics_to_normalize["ideal_value"].items():
            if metric in df.columns:
                df[f"{metric}_norm"] = 1 - abs(df[metric] - ideal) / max(abs(df[metric].max() - ideal), abs(df[metric].min() - ideal))
        
        # Definir pesos diferentes para cada tipo de FII
        weights = self._get_weights_by_fii_type(fii_type)
        
        # Calcular pontuação final combinando todas as métricas normalizadas
        df["final_score"] = 0
        
        for metric, weight in weights.items():
            norm_metric = f"{metric}_norm"
            if norm_metric in df.columns:
                df["final_score"] += df[norm_metric] * weight
        
        # Mostrar detalhes da análise para os melhores FIIs
        print("\n==== Detalhes da Análise Avançada (Status Invest) ====")
        for _, row in df.sort_values(by="final_score", ascending=False).head().iterrows():
            ticker = row["ticker"]
            score = row["final_score"]
            
            # Formatar métricas principais para exibição
            dy = row.get("dividendYield", 0) * 100 if "dividendYield" in row else 0
            pvp = row.get("priceToBookRatio", 0) if "priceToBookRatio" in row else 0
            price_trend = row.get("price_trend", 0)
            sentiment = row.get("news_sentiment", 0)
            
            print(f"\n{ticker} - Score: {score:.2f}")
            print(f"DY: {dy:.2f}% | P/VP: {pvp:.2f} | Tendência: {price_trend:.2f}% | Sentimento: {sentiment:.2f}")
            
            # Mostrar pontos fortes e fracos
            strengths = []
            weaknesses = []
            
            for metric, weight in weights.items():
                norm_metric = f"{metric}_norm"
                if norm_metric in df.columns and weight > 0.02:  # Mostrar apenas métricas relevantes
                    norm_value = row.get(norm_metric, 0)
                    if norm_value > 0.7:
                        strengths.append(f"{metric} ({norm_value:.2f})")
                    elif norm_value < 0.3:
                        weaknesses.append(f"{metric} ({norm_value:.2f})")
            
            print("Pontos fortes: " + ", ".join(strengths[:3]) if strengths else "Nenhum ponto forte destacado")
            print("Pontos fracos: " + ", ".join(weaknesses[:3]) if weaknesses else "Nenhum ponto fraco destacado")
        
        # Ordenar por pontuação e retornar como dicionários
        sorted_df = df.sort_values(by="final_score", ascending=False)
        
        # Adicionar coluna de ranking
        sorted_df["ranking"] = range(1, len(sorted_df) + 1)
        
        return sorted_df.to_dict("records")
    
    def _ensure_numeric_columns(self, df, columns):
        """
        Garante que as colunas especificadas sejam numéricas,
        convertendo-as ou preenchendo com valores padrão.
        """
        for col in columns:
            if col not in df.columns:
                df[col] = 0.0
            else:
                # Converter para numérico com valor padrão para erros
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    
    def _get_weights_by_fii_type(self, fii_type):
        """
        Retorna os pesos para cada métrica de acordo com o tipo de FII.
        
        Estes pesos definem a importância relativa de cada fator na
        pontuação final. Os pesos são baseados em práticas comuns de
        avaliação para cada tipo de fundo.
        """
        if fii_type == "renda_urbana":
            return {
                "dividendYield": 0.15,            # Rendimento atual
                "priceToBookRatio": 0.10,         # Valor patrimonial
                "liquidity": 0.05,                # Liquidez
                "price_trend": 0.05,              # Tendência de preço
                "price_volatility": 0.05,         # Volatilidade
                "dividend_consistency": 0.15,     # Consistência dos dividendos (importante)
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.10,             # Vacância
                "diversification": 0.05,          # Diversificação
                "cap_rate": 0.10,                 # Taxa de retorno
                "contract_duration": 0.10         # Duração média dos contratos (contratos atípicos)
            }
        
        elif fii_type == "fof":
            return {
                "dividendYield": 0.15,            # Rendimento atual
                "priceToBookRatio": 0.15,         # Valor patrimonial
                "liquidity": 0.10,                # Liquidez (mais importante para FoFs)
                "price_trend": 0.10,              # Tendência de preço
                "price_volatility": 0.10,         # Volatilidade
                "dividend_consistency": 0.15,     # Consistência dos dividendos
                "news_sentiment": 0.05,           # Sentimento das notícias
                "recent_sentiment": 0.05,         # Notícias recentes
                "vacancy_rate": 0.00,             # Não se aplica diretamente
                "diversification": 0.15,          # Diversificação (crítico para FoFs)
                "cap_rate": 0.00,                 # Não se aplica diretamente
                "contract_duration": 0.00         # Não se aplica
            }
        
        else:  # Tipo genérico/desconhecido
            return {
                "dividendYield": 0.15,
                "priceToBookRatio": 0.15,
                "liquidity": 0.10,
                "price_trend": 0.10,
                "price_volatility": 0.05,
                "dividend_consistency": 0.10,
                "news_sentiment": 0.05,
                "recent_sentiment": 0.05,
                "vacancy_rate": 0.10,
                "diversification": 0.05,
                "cap_rate": 0.05,
                "contract_duration": 0.05
            } 