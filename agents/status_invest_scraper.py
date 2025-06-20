import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
import random

class StatusInvestScraper:
    """
    Classe para extrair dados do site Status Invest, incluindo:
    - Dados históricos de preço e dividendos
    - Notícias recentes
    - Indicadores fundamentalistas
    """
    
    def __init__(self):
        self.base_url = "https://statusinvest.com.br"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_historical_data(self, ticker, simulate=True):
        """
        Obtém dados históricos de preço e dividendos para um FII.
        
        Args:
            ticker (str): Ticker do FII
            simulate (bool): Se True, retorna dados simulados
            
        Returns:
            dict: Dados históricos do FII
        """
        if simulate:
            return self._get_simulated_historical_data(ticker)
        
        # URL para dados históricos
        url = f"{self.base_url}/fundos-imobiliarios/{ticker}"
        
        try:
            print(f"Obtendo dados históricos para {ticker} do Status Invest...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extrair dados históricos de preço usando JavaScript
            # Em uma implementação real, precisaríamos acessar a API do Status Invest
            # que fornece dados históricos, mas para simplificar, usamos dados simulados
            return self._get_simulated_historical_data(ticker)
            
        except Exception as e:
            print(f"Erro ao obter dados históricos para {ticker}: {e}")
            return self._get_simulated_historical_data(ticker)
    
    def get_news(self, ticker, simulate=True):
        """
        Obtém notícias recentes sobre o FII.
        
        Args:
            ticker (str): Ticker do FII
            simulate (bool): Se True, retorna notícias simuladas
            
        Returns:
            list: Lista de notícias
        """
        if simulate:
            return self._get_simulated_news(ticker)
        
        # URL para notícias
        url = f"{self.base_url}/fundos-imobiliarios/{ticker}/proventos"
        
        try:
            print(f"Obtendo notícias para {ticker} do Status Invest...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extrair notícias
            # (Em uma implementação real, faríamos scraping das notícias)
            # Por simplicidade, usamos dados simulados
            return self._get_simulated_news(ticker)
            
        except Exception as e:
            print(f"Erro ao obter notícias para {ticker}: {e}")
            return self._get_simulated_news(ticker)
    
    def get_fundamental_data(self, ticker, simulate=True):
        """
        Obtém dados fundamentalistas do FII.
        
        Args:
            ticker (str): Ticker do FII
            simulate (bool): Se True, retorna dados simulados
            
        Returns:
            dict: Dados fundamentalistas
        """
        if simulate:
            return self._get_simulated_fundamental_data(ticker)
        
        # URL para dados fundamentalistas
        url = f"{self.base_url}/fundos-imobiliarios/{ticker}"
        
        try:
            print(f"Obtendo dados fundamentalistas para {ticker} do Status Invest...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extrair dados fundamentalistas
            # Em uma implementação real, extrairíamos todos os indicadores
            # Por simplicidade, usamos dados simulados
            return self._get_simulated_fundamental_data(ticker)
            
        except Exception as e:
            print(f"Erro ao obter dados fundamentalistas para {ticker}: {e}")
            return self._get_simulated_fundamental_data(ticker)
    
    def _get_simulated_historical_data(self, ticker):
        """
        Gera dados históricos simulados para um FII.
        
        Args:
            ticker (str): Ticker do FII
            
        Returns:
            dict: Dados históricos simulados
        """
        # Data final (hoje)
        end_date = datetime.now()
        
        # Data inicial (1 ano atrás)
        start_date = end_date - timedelta(days=365)
        
        # Gerar datas para o período (dias úteis)
        all_dates = pd.date_range(start=start_date, end=end_date, freq="B")
        
        # Preço inicial (valor aleatório entre 80 e 120)
        initial_price = random.uniform(80, 120)
        
        # Simular série de preços com tendência e volatilidade
        # Adicionar tendência leve (positiva ou negativa)
        trend = random.uniform(-0.15, 0.15)  # Tendência anual
        daily_trend = (1 + trend) ** (1/252) - 1  # Convertendo para tendência diária
        
        # Volatilidade diária
        volatility = random.uniform(0.01, 0.02)
        
        # Gerar preços
        prices = [initial_price]
        for i in range(1, len(all_dates)):
            # Preço anterior + tendência + ruído aleatório
            new_price = prices[-1] * (1 + daily_trend + random.normalvariate(0, volatility))
            prices.append(new_price)
        
        # Gerar dividendos mensais (em datas aleatórias de cada mês)
        dividend_dates = []
        dividend_values = []
        
        # Agrupar por mês
        months = pd.Series(all_dates).dt.to_period("M").unique()
        
        for month in months:
            # Dias úteis deste mês
            month_days = [d for d in all_dates if d.month == month.month and d.year == month.year]
            
            # Escolher uma data aleatória para pagamento
            if month_days:
                payment_date = random.choice(month_days)
                dividend_dates.append(payment_date)
                
                # Valor do dividendo (entre 0.4% e 1.0% do preço)
                price_on_date = prices[all_dates.get_loc(payment_date)]
                dividend = price_on_date * random.uniform(0.004, 0.01)
                dividend_values.append(round(dividend, 2))
        
        # Converter para DataFrames
        price_df = pd.DataFrame({
            "date": all_dates,
            "price": prices
        })
        
        dividend_df = pd.DataFrame({
            "date": dividend_dates,
            "value": dividend_values
        })
        
        # Calcular métricas
        avg_price = np.mean(prices)
        price_change = (prices[-1] / prices[0] - 1) * 100  # Variação percentual
        
        annual_dividend = sum(dividend_values)
        current_dividend_yield = (annual_dividend / prices[-1]) * 100
        
        # Calcular tendência (usando regressão linear simplificada)
        days = list(range(len(prices)))
        price_trend = np.polyfit(days, prices, 1)[0] * 252  # Tendência diária x 252 dias úteis
        price_trend_pct = (price_trend / prices[0]) * 100
        
        # Retornar resultados
        return {
            "ticker": ticker,
            "price_data": price_df.to_dict("records"),
            "dividend_data": dividend_df.to_dict("records"),
            "metrics": {
                "avg_price": round(avg_price, 2),
                "price_change_pct": round(price_change, 2),
                "annual_dividend": round(annual_dividend, 2),
                "current_dividend_yield": round(current_dividend_yield, 2),
                "price_trend_pct": round(price_trend_pct, 2),
                "volatility": round(volatility * 100, 2)
            }
        }
    
    def _get_simulated_news(self, ticker):
        """
        Gera notícias simuladas para um FII.
        
        Args:
            ticker (str): Ticker do FII
            
        Returns:
            list: Lista de notícias simuladas
        """
        # Lista de possíveis títulos de notícias
        positive_titles = [
            f"{ticker} distribui dividendos acima do esperado",
            f"Gestora do {ticker} anuncia aquisição estratégica",
            f"Ocupação dos imóveis do {ticker} atinge máxima histórica",
            f"Analistas elevam recomendação para {ticker}",
            f"{ticker} renova contrato com inquilino-âncora",
            f"Resultados do {ticker} superam expectativas do mercado"
        ]
        
        neutral_titles = [
            f"{ticker} mantém distribuição de dividendos",
            f"Assembleia de cotistas do {ticker} aprova contas",
            f"Gestora do {ticker} apresenta relatório trimestral",
            f"{ticker} anuncia novas emissões de cotas",
            f"Entenda a estratégia do fundo {ticker}",
            f"{ticker} realiza ajustes na carteira de ativos"
        ]
        
        negative_titles = [
            f"{ticker} reduz distribuição de dividendos",
            f"Vacância nos imóveis do {ticker} preocupa investidores",
            f"Analistas rebaixam recomendação para {ticker}",
            f"{ticker} enfrenta dificuldades com inquilinos",
            f"Rentabilidade do {ticker} fica abaixo da média do setor",
            f"Gestora do {ticker} alerta para desafios à frente"
        ]
        
        # Escolher títulos aleatórios
        num_news = random.randint(3, 8)
        
        # Probabilidade de cada tipo de notícia
        # Mais notícias neutras (60%), seguidas de positivas (25%) e negativas (15%)
        news = []
        
        for _ in range(num_news):
            news_type = random.choices(
                ["positive", "neutral", "negative"], 
                weights=[0.25, 0.60, 0.15], 
                k=1
            )[0]
            
            if news_type == "positive":
                title = random.choice(positive_titles)
                sentiment = "positive"
            elif news_type == "neutral":
                title = random.choice(neutral_titles)
                sentiment = "neutral"
            else:
                title = random.choice(negative_titles)
                sentiment = "negative"
            
            # Data aleatória nos últimos 90 dias
            days_ago = random.randint(1, 90)
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%d/%m/%Y")
            
            news.append({
                "date": date,
                "title": title,
                "source": random.choice(["Status Invest", "InfoMoney", "Valor Econômico", "XP Research"]),
                "sentiment": sentiment
            })
        
        # Ordenar por data (mais recente primeiro)
        news.sort(key=lambda x: datetime.strptime(x["date"], "%d/%m/%Y"), reverse=True)
        
        return news
    
    def _get_simulated_fundamental_data(self, ticker):
        """
        Gera dados fundamentalistas simulados para um FII.
        
        Args:
            ticker (str): Ticker do FII
            
        Returns:
            dict: Dados fundamentalistas simulados
        """
        # Extrair tipo do FII do ticker (simplificado)
        fii_type = self._guess_fii_type_from_ticker(ticker)
        
        # Ajustar parâmetros de acordo com o tipo
        if fii_type == "cri":
            vacancia = round(random.uniform(0, 0.05), 4)  # Baixa vacância para CRIs
            num_ativos = random.randint(15, 50)
            cap_rate = round(random.uniform(0.09, 0.14), 4)
            liquidez_diaria = random.randint(500000, 5000000)
            patrimonio = random.randint(200000000, 2000000000)
            num_cotistas = random.randint(5000, 50000)
            diversificacao = random.randint(8, 15)  # Número de devedores/operações
            duracao_media = round(random.uniform(2, 8), 1)  # Anos
            
        elif fii_type in ["shopping", "logistica", "escritorio"]:
            vacancia = round(random.uniform(0.05, 0.25), 4)  # Vacância típica de imóveis
            num_ativos = random.randint(3, 20)
            cap_rate = round(random.uniform(0.07, 0.12), 4)
            liquidez_diaria = random.randint(300000, 3000000)
            patrimonio = random.randint(150000000, 1500000000)
            num_cotistas = random.randint(3000, 40000)
            diversificacao = num_ativos  # Para FIIs de tijolo, diversificação = número de imóveis
            duracao_media = round(random.uniform(3, 10), 1)  # Anos (contratos de aluguel)
            
        elif fii_type in ["renda_urbana"]:
            vacancia = round(random.uniform(0.02, 0.15), 4)
            num_ativos = random.randint(5, 25)
            cap_rate = round(random.uniform(0.08, 0.13), 4)
            liquidez_diaria = random.randint(200000, 2000000)
            patrimonio = random.randint(100000000, 1000000000)
            num_cotistas = random.randint(2000, 30000)
            diversificacao = num_ativos
            duracao_media = round(random.uniform(5, 15), 1)  # Anos (contratos atípicos são mais longos)
            
        elif fii_type == "fof":
            vacancia = 0  # FOFs não têm vacância direta
            num_ativos = random.randint(10, 30)  # Número de FIIs na carteira
            cap_rate = round(random.uniform(0.07, 0.11), 4)
            liquidez_diaria = random.randint(400000, 4000000)
            patrimonio = random.randint(100000000, 800000000)
            num_cotistas = random.randint(4000, 35000)
            diversificacao = random.randint(4, 8)  # Número de segmentos diferentes
            duracao_media = 0  # Não se aplica
        
        else:  # Padrão
            vacancia = round(random.uniform(0.05, 0.15), 4)
            num_ativos = random.randint(5, 25)
            cap_rate = round(random.uniform(0.08, 0.12), 4)
            liquidez_diaria = random.randint(300000, 2500000)
            patrimonio = random.randint(150000000, 1200000000)
            num_cotistas = random.randint(3000, 30000)
            diversificacao = random.randint(5, 12)
            duracao_media = round(random.uniform(3, 8), 1)
        
        # Gerar dados fundamentalistas
        return {
            "ticker": ticker,
            "fii_type": fii_type,
            "vacancy_rate": vacancia,
            "num_assets": num_ativos,
            "cap_rate": cap_rate,
            "daily_liquidity": liquidez_diaria,
            "equity_value": patrimonio,
            "num_shareholders": num_cotistas,
            "diversification": diversificacao,
            "average_contract_duration": duracao_media,
            "management_fee": round(random.uniform(0.6, 1.5), 2),  # Taxa de administração (%)
            "performance_fee": 20 if random.random() < 0.3 else 0  # 30% dos FIIs têm taxa de performance
        }
    
    def _guess_fii_type_from_ticker(self, ticker):
        """
        Tenta adivinhar o tipo de FII com base no ticker.
        Esta é uma simplificação, não é 100% preciso.
        
        Args:
            ticker (str): Ticker do FII
            
        Returns:
            str: Tipo estimado do FII
        """
        ticker = ticker.upper()
        
        # Padrões comuns nos nomes de FIIs
        patterns = {
            "cri": ["CR", "CRI", "NC", "REC", "KNCR", "KNIP", "KNHY"],
            "shopping": ["MALL", "SHOP", "VISC", "XPML", "HGBS"],
            "logistica": ["LOGC", "HGLG", "XPLG", "BRCO"],
            "escritorio": ["BRCR", "HGRE", "RCRB", "ALMI", "FVPQ", "JSRE"],
            "renda_urbana": ["KNRI", "RBVA", "TRXF", "LFTT"],
            "fof": ["KFOF", "RBRF", "BCIA", "HFOF"]
        }
        
        for fii_type, prefixes in patterns.items():
            for prefix in prefixes:
                if ticker.startswith(prefix):
                    return fii_type
        
        # Se não conseguir identificar, tenta adivinhar pela letra final
        last_chars = ticker[-2:] if len(ticker) >= 2 else ""
        if last_chars == "11":
            # Examinar primeiras letras
            if ticker.startswith("RB") or ticker.startswith("VG") or ticker.startswith("HG"):
                return random.choice(["cri", "logistica", "shopping"])
            
            return random.choice(["cri", "shopping", "logistica", "escritorio", "renda_urbana", "fof"])
        
        # Fallback
        return "cri" 