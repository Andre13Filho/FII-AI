import pandas as pd
import matplotlib.pyplot as plt
from data.investment_tracker import InvestmentTracker
from agents.market_agent import BrapiAgent
from utils.helpers import format_currency, format_percentage

class InvestmentAgent:
    """
    Agente responsável por gerenciar o histórico de investimentos 
    e analisar a carteira atual do usuário.
    """
    def __init__(self):
        self.tracker = InvestmentTracker()
        self.brapi_agent = BrapiAgent()
    
    def register_investment(self, ticker, tipo, preco, quantidade, data=None):
        """
        Registra um novo investimento na carteira do usuário.
        
        Args:
            ticker (str): Ticker do FII
            tipo (str): Tipo do FII
            preco (float): Preço unitário
            quantidade (int): Quantidade de cotas
            data (str, opcional): Data da compra (formato YYYY-MM-DD)
        
        Returns:
            bool: True se o registro foi bem-sucedido
        """
        try:
            self.tracker.add_investment(ticker, tipo, preco, quantidade, data)
            return True
        except Exception as e:
            print(f"Erro ao registrar investimento: {str(e)}")
            return False
    
    def register_sale(self, ticker, quantidade, preco, data=None):
        """
        Registra a venda de cotas de um FII.
        
        Args:
            ticker (str): Ticker do FII
            quantidade (int): Quantidade de cotas vendidas
            preco (float): Preço unitário de venda
            data (str, opcional): Data da venda (formato YYYY-MM-DD)
        
        Returns:
            bool: True se a venda foi registrada com sucesso
        """
        return self.tracker.remove_investment(ticker, quantidade, preco, data)
    
    def get_current_portfolio(self):
        """
        Retorna a carteira atual do usuário.
        
        Returns:
            list: Lista de investimentos
        """
        return self.tracker.get_current_portfolio()
    
    def get_portfolio_summary(self):
        """
        Retorna um resumo da carteira atual.
        
        Returns:
            dict: Resumo da carteira
        """
        return self.tracker.get_portfolio_summary()
    
    def get_formatted_portfolio(self):
        """
        Retorna a carteira atual formatada para exibição.
        
        Returns:
            pd.DataFrame: DataFrame com a carteira formatada
        """
        portfolio = self.get_current_portfolio()
        
        if not portfolio:
            return pd.DataFrame()
        
        # Converter para DataFrame
        df = pd.DataFrame(portfolio)
        
        # Calcular valores adicionais
        df['valor_investido'] = df['quantidade'] * df['preco_medio']
        
        # Formatar para exibição
        df_display = df.copy()
        df_display['preco_medio'] = df_display['preco_medio'].apply(format_currency)
        df_display['valor_investido'] = df_display['valor_investido'].apply(format_currency)
        
        # Renomear colunas
        column_mapping = {
            'ticker': 'Ticker',
            'tipo': 'Tipo',
            'quantidade': 'Quantidade',
            'preco_medio': 'Preço Médio',
            'valor_investido': 'Valor Investido',
            'data_inicial': 'Data Inicial'
        }
        
        df_display = df_display[column_mapping.keys()].rename(columns=column_mapping)
        
        return df_display
    
    def analyze_portfolio_performance(self):
        """
        Analisa o desempenho da carteira atual com base nos preços atuais.
        
        Returns:
            tuple: (dict - análise, pd.DataFrame - detalhes formatados, fig - gráfico)
        """
        portfolio = self.get_current_portfolio()
        
        if not portfolio:
            return None, pd.DataFrame(), None
        
        # Obter preços atuais
        tickers = [inv['ticker'] for inv in portfolio]
        precos_atuais = {}
        
        for ticker in tickers:
            try:
                preco = self.brapi_agent.get_ticker_price(ticker)
                precos_atuais[ticker] = preco
            except Exception as e:
                print(f"Erro ao obter preço para {ticker}: {str(e)}")
                precos_atuais[ticker] = 0
        
        # Analisar desempenho
        performance = self.tracker.analyze_performance(precos_atuais)
        
        # Formatar detalhes para exibição
        if performance['detalhes_por_fii']:
            df_detalhes = pd.DataFrame(performance['detalhes_por_fii'])
            
            # Formatar valores
            df_display = df_detalhes.copy()
            df_display['preco_medio'] = df_display['preco_medio'].apply(format_currency)
            df_display['preco_atual'] = df_display['preco_atual'].apply(format_currency)
            df_display['valor_investido'] = df_display['valor_investido'].apply(format_currency)
            df_display['valor_atual'] = df_display['valor_atual'].apply(format_currency)
            df_display['lucro_prejuizo'] = df_display['lucro_prejuizo'].apply(format_currency)
            df_display['rentabilidade'] = df_display['rentabilidade'].apply(format_percentage)
            
            # Renomear colunas
            column_mapping = {
                'ticker': 'Ticker',
                'tipo': 'Tipo',
                'quantidade': 'Quantidade',
                'preco_medio': 'Preço Médio',
                'preco_atual': 'Preço Atual',
                'valor_investido': 'Valor Investido',
                'valor_atual': 'Valor Atual',
                'lucro_prejuizo': 'Lucro/Prejuízo',
                'rentabilidade': 'Rentabilidade'
            }
            
            df_display = df_display[column_mapping.keys()].rename(columns=column_mapping)
        else:
            df_display = pd.DataFrame()
        
        # Gerar gráfico de desempenho
        if performance['detalhes_por_fii']:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Ordenar por rentabilidade
            df_sorted = df_detalhes.sort_values('rentabilidade', ascending=False)
            
            # Usar cores diferentes para lucro/prejuízo
            colors = ['green' if r >= 0 else 'red' for r in df_sorted['rentabilidade']]
            
            # Criar gráfico de barras
            bars = ax.bar(df_sorted['ticker'], df_sorted['rentabilidade'], color=colors)
            
            # Adicionar rótulos e formatação
            ax.set_title('Rentabilidade por FII (%)')
            ax.set_ylabel('Rentabilidade (%)')
            ax.set_xlabel('FIIs')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Rotacionar rótulos do eixo x
            plt.xticks(rotation=45, ha='right')
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                if height >= 0:
                    va = 'bottom'
                    y_offset = 0.5
                else:
                    va = 'top'
                    y_offset = -0.5
                ax.text(bar.get_x() + bar.get_width()/2., height + y_offset,
                        f'{height:.1f}%',
                        ha='center', va=va, fontsize=9)
            
            plt.tight_layout()
        else:
            fig = None
        
        return performance, df_display, fig
    
    def get_portfolio_charts(self):
        """
        Gera gráficos de análise da carteira atual.
        
        Returns:
            matplotlib.figure.Figure: Figura com os gráficos
        """
        return self.tracker.generate_portfolio_charts()
    
    def get_investment_history(self, ticker=None):
        """
        Obtém o histórico de transações para um ticker específico ou toda a carteira.
        
        Args:
            ticker (str, opcional): Ticker para filtrar o histórico
        
        Returns:
            pd.DataFrame: DataFrame com o histórico de transações
        """
        portfolio = self.get_current_portfolio()
        
        if not portfolio:
            return pd.DataFrame()
        
        all_transactions = []
        
        for inv in portfolio:
            if ticker and inv['ticker'] != ticker:
                continue
                
            for transaction in inv['transacoes']:
                transaction_data = {
                    'ticker': inv['ticker'],
                    'tipo': inv['tipo'],
                    'data': transaction['data'],
                    'operacao': transaction['operacao'],
                    'quantidade': transaction['quantidade'],
                    'preco': transaction['preco'],
                    'valor_total': transaction['quantidade'] * transaction['preco']
                }
                all_transactions.append(transaction_data)
        
        if not all_transactions:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_transactions)
        
        # Ordenar por data
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data', ascending=False)
        
        # Formatar para exibição
        df_display = df.copy()
        df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
        df_display['preco'] = df_display['preco'].apply(format_currency)
        df_display['valor_total'] = df_display['valor_total'].apply(format_currency)
        
        # Renomear colunas
        column_mapping = {
            'ticker': 'Ticker',
            'tipo': 'Tipo',
            'data': 'Data',
            'operacao': 'Operação',
            'quantidade': 'Quantidade',
            'preco': 'Preço',
            'valor_total': 'Valor Total'
        }
        
        df_display = df_display[column_mapping.keys()].rename(columns=column_mapping)
        
        return df_display 