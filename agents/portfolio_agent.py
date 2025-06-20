import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.constants import FII_DIVIDEND_INFO
from utils.helpers import format_percentage
from agents.llm_agent import query_groq

class PortfolioAgent:
    """
    Agente responsável por calcular a alocação ideal da carteira de FIIs
    com base nos melhores FIIs selecionados e no patrimônio disponível.
    """
    def __init__(self, patrimonio):
        self.patrimonio = patrimonio
        # Definição das proporções de cada tipo de FII no portfólio
        self.allocations = {
            "cri": 0.27,
            "shopping": 0.17,
            "logistica": 0.17,
            "escritorio": 0.16,
            "renda_urbana": 0.09,
            "fof": 0.14
        }
        
    def calculate_portfolio(self, fiis_cri, fiis_shopping, fiis_logistica, 
                            fiis_escritorio, fiis_renda_urbana, fiis_fof):
        """
        Calcula a alocação ideal para a carteira de FIIs.
        
        Args:
            fiis_cri (list): Lista dos melhores FIIs de CRI
            fiis_shopping (list): Lista dos melhores FIIs de Shopping
            fiis_logistica (list): Lista dos melhores FIIs de Logística
            fiis_escritorio (list): Lista dos melhores FIIs de Escritório
            fiis_renda_urbana (list): Lista dos melhores FIIs de Renda Urbana
            fiis_fof (list): Lista dos melhores FIIs de FoF
            
        Returns:
            dict: Informações sobre a carteira recomendada
        """
        # 25% do patrimônio será alocado em FIIs
        investment_amount = self.patrimonio * 0.25
        
        # Calcular quanto investir em cada tipo de FII
        type_investments = {
            "cri": investment_amount * self.allocations["cri"],
            "shopping": investment_amount * self.allocations["shopping"],
            "logistica": investment_amount * self.allocations["logistica"],
            "escritorio": investment_amount * self.allocations["escritorio"],
            "renda_urbana": investment_amount * self.allocations["renda_urbana"],
            "fof": investment_amount * self.allocations["fof"]
        }
        
        # Calcular a alocação para cada FII individual dentro de cada tipo
        portfolio = self._allocate_fiis(type_investments, fiis_cri, fiis_shopping, 
                                      fiis_logistica, fiis_escritorio, 
                                      fiis_renda_urbana, fiis_fof)
        
        # Gerar explicações detalhadas para cada FII
        portfolio_with_explanations = self._generate_investment_explanations(portfolio)
        
        # Criar um resumo da alocação por tipo de FII
        allocation_summary = self._create_allocation_summary(portfolio_with_explanations)
        
        # Criar um gráfico de pizza da alocação
        allocation_chart = self._create_allocation_chart(allocation_summary)
        
        # Calcular o dividend yield médio ponderado da carteira
        portfolio_dividend_yield = self._calculate_portfolio_dividend_yield(portfolio_with_explanations)
        
        # Retornar os resultados
        return {
            "detailed_portfolio": portfolio_with_explanations,
            "allocation_summary": allocation_summary,
            "allocation_chart": allocation_chart,
            "total_investment": investment_amount,
            "patrimonio_total": self.patrimonio,
            "portfolio_dividend_yield": portfolio_dividend_yield
        }
    
    def _generate_investment_explanations(self, portfolio):
        """
        Gera explicações detalhadas sobre o motivo pelo qual o usuário deve investir em cada FII.
        
        Args:
            portfolio (list): Lista de FIIs no portfólio
            
        Returns:
            list: Lista de FIIs com explicações detalhadas
        """
        portfolio_with_explanations = []
        
        for fii in portfolio:
            try:
                # Preparar dados para a explicação
                ticker = fii["ticker"]
                fii_type = fii["type"]
                price = fii["price"]
                dividend_yield = fii["dividend_yield"]
                monthly_income = fii["monthly_income"]
                annual_income = fii["annual_income"]
                shares = fii["shares"]
                investment = fii["investment"]
                
                # Traduzir o tipo de FII para português
                fii_type_map = {
                    "cri": "Fundo de Recebíveis Imobiliários (CRI)",
                    "shopping": "Fundo de Shopping Centers",
                    "logistica": "Fundo de Galpões Logísticos",
                    "escritorio": "Fundo de Escritórios Corporativos",
                    "renda_urbana": "Fundo de Renda Urbana",
                    "fof": "Fundo de Fundos Imobiliários (FoF)"
                }
                
                fii_type_pt = fii_type_map.get(fii_type, fii_type)
                
                # Criar prompt para a IA explicar a recomendação
                prompt = f"""
                Você é um especialista em fundos imobiliários (FIIs) e precisa explicar ao investidor por que o FII {ticker} é uma boa escolha para sua carteira.
                
                Dados do FII:
                - Ticker: {ticker}
                - Tipo: {fii_type_pt}
                - Preço atual: R$ {price:.2f}
                - Dividend Yield anual: {dividend_yield * 100:.2f}%
                - Quantidade sugerida: {shares} cotas
                - Investimento total: R$ {investment:.2f}
                - Renda mensal estimada: R$ {monthly_income:.2f}
                - Renda anual estimada: R$ {annual_income:.2f}
                
                Forneça uma explicação clara e detalhada sobre:
                1. Por que este FII específico é uma boa escolha dentro da sua categoria
                2. Quais são as vantagens de investir neste tipo de FII
                3. Como ele contribui para a diversificação da carteira
                4. Perspectivas futuras para este tipo de ativo
                
                Seja específico sobre as características deste FII, baseado no seu tipo. Foque nas vantagens competitivas, rendimentos esperados e proteção contra inflação.
                
                Forneça uma resposta direta, objetiva e concisa em até 3 parágrafos.
                """
                
                # Obter explicação da IA
                explanation = query_groq(prompt, max_tokens=512)
                
                # Adicionar a explicação ao FII
                fii_with_explanation = fii.copy()
                fii_with_explanation["investment_explanation"] = explanation
                
                portfolio_with_explanations.append(fii_with_explanation)
            except Exception as e:
                print(f"Erro ao gerar explicação para {fii['ticker']}: {e}")
                # Se houver erro, adicionar sem a explicação
                portfolio_with_explanations.append(fii)
        
        return portfolio_with_explanations
    
    def _allocate_fiis(self, type_investments, fiis_cri, fiis_shopping, 
                      fiis_logistica, fiis_escritorio, fiis_renda_urbana, fiis_fof):
        """
        Aloca o investimento entre os FIIs individuais em cada categoria.
        """
        # Agrupar todos os FIIs por tipo
        all_fiis_by_type = {
            "cri": fiis_cri,
            "shopping": fiis_shopping,
            "logistica": fiis_logistica,
            "escritorio": fiis_escritorio,
            "renda_urbana": fiis_renda_urbana,
            "fof": fiis_fof
        }
        
        # Lista para armazenar o portfólio detalhado
        detailed_portfolio = []
        
        # Para cada tipo de FII
        for fii_type, fiis in all_fiis_by_type.items():
            # Verificar se temos FIIs nesta categoria
            if not fiis:
                continue
                
            # Valor total a ser investido neste tipo
            total_type_investment = type_investments[fii_type]
            
            # Número de FIIs na categoria
            num_fiis = min(len(fiis), 3)  # No máximo 3 FIIs por categoria
            
            # Distribuição do investimento entre os FIIs
            # Poderia implementar uma lógica mais sofisticada aqui
            if num_fiis > 0:
                # Selecionar os melhores FIIs (no máximo 3)
                selected_fiis = fiis[:num_fiis]
                
                # Pontuação para ponderar o investimento
                # Para simplificar, usamos índices como pontuação (melhor FII tem pontuação maior)
                scores = np.array(range(num_fiis, 0, -1))
                
                # Normalizar pontuações para que somem 1
                weights = scores / scores.sum()
                
                # Calcular valor a ser investido em cada FII
                for i, fii in enumerate(selected_fiis):
                    investment_value = total_type_investment * weights[i]
                    
                    # Calcular quantas cotas podem ser compradas
                    try:
                        # Garantir que price é um número válido
                        if "price" in fii and fii["price"] > 0:
                            price = float(fii["price"])
                        else:
                            # Preço não disponível, usar dados constantes ou um valor arbitrário
                            ticker = fii["ticker"]
                            if ticker in FII_DIVIDEND_INFO:
                                price = FII_DIVIDEND_INFO[ticker]["price"]
                            else:
                                price = 100.0
                            
                        # Obter dividend yield
                        ticker = fii["ticker"]
                        if "dividendYield" in fii and fii["dividendYield"] > 0:
                            dividend_yield = float(fii["dividendYield"])
                            last_dividend = dividend_yield * price / 12  # Estimativa mensal
                        elif ticker in FII_DIVIDEND_INFO:
                            dividend_yield = FII_DIVIDEND_INFO[ticker]["dividend_yield"]
                            last_dividend = FII_DIVIDEND_INFO[ticker]["last_dividend"]
                        else:
                            # Valores padrão se não encontrar
                            dividend_yield = 0.008  # 0.8% ao mês, ~10% ao ano
                            last_dividend = price * dividend_yield
                        
                        # Calcular número de cotas (arredondar para baixo)
                        shares = max(0, int(np.floor(investment_value / price)))
                        
                        # Valor real investido (baseado no número de cotas)
                        actual_investment = shares * price
                        
                        # Calcular rendimento mensal estimado
                        monthly_income = shares * last_dividend
                        
                        # Adicionar ao portfólio detalhado
                        detailed_portfolio.append({
                            "ticker": fii["ticker"],
                            "type": fii_type,
                            "price": price,
                            "shares": shares,
                            "investment": actual_investment,
                            "percentage": actual_investment / (self.patrimonio * 0.25) * 100 if self.patrimonio > 0 else 0,
                            "dividend_yield": dividend_yield,
                            "last_dividend": last_dividend,
                            "monthly_income": monthly_income,
                            "annual_income": monthly_income * 12
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Erro ao calcular alocação para {fii['ticker']}: {e}")
                        # Adicionar com valores padrão em caso de erro
                        detailed_portfolio.append({
                            "ticker": fii["ticker"],
                            "type": fii_type,
                            "price": 100.0,
                            "shares": 0,
                            "investment": 0.0,
                            "percentage": 0.0,
                            "dividend_yield": 0.0,
                            "last_dividend": 0.0,
                            "monthly_income": 0.0,
                            "annual_income": 0.0
                        })
        
        return detailed_portfolio
    
    def _create_allocation_summary(self, portfolio):
        """
        Cria um resumo da alocação por tipo de FII.
        """
        # Converter para DataFrame
        df = pd.DataFrame(portfolio)
        
        # Verificar se há dados para agrupar
        if df.empty:
            # Retornar um DataFrame vazio com as colunas corretas
            return pd.DataFrame(columns=[
                "Tipo de FII", "Investimento (R$)", "Quantidade de FIIs", 
                "Percentual da Carteira (%)", "Dividend Yield Médio (%)",
                "Rendimento Mensal (R$)"
            ])
        
        # Agrupar por tipo e somar investimentos
        summary = df.groupby("type").agg({
            "investment": "sum",
            "ticker": "count",
            "monthly_income": "sum"
        }).reset_index()
        
        # Calcular percentuais
        total_investment = summary["investment"].sum()
        if total_investment > 0:
            summary["percentage"] = summary["investment"] / total_investment * 100
        else:
            summary["percentage"] = 0.0
            
        # Calcular dividend yield médio por tipo
        avg_dy = []
        for fii_type in summary["type"]:
            type_fiis = df[df["type"] == fii_type]
            if type_fiis["investment"].sum() > 0:
                # Dividend yield médio ponderado pelo investimento
                weighted_dy = (type_fiis["dividend_yield"] * type_fiis["investment"]).sum() / type_fiis["investment"].sum()
                avg_dy.append(weighted_dy * 100)  # Converter para percentual
            else:
                avg_dy.append(0.0)
                
        summary["avg_dividend_yield"] = avg_dy
        
        # Renomear colunas
        summary = summary.rename(columns={
            "type": "Tipo de FII",
            "investment": "Investimento (R$)",
            "ticker": "Quantidade de FIIs",
            "percentage": "Percentual da Carteira (%)",
            "avg_dividend_yield": "Dividend Yield Médio (%)",
            "monthly_income": "Rendimento Mensal (R$)"
        })
        
        return summary
    
    def _create_allocation_chart(self, allocation_summary):
        """
        Cria um gráfico de pizza com a alocação da carteira.
        """
        # Configurar figura
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Verificar se há dados para plotar
        if allocation_summary.empty:
            ax.text(0.5, 0.5, "Sem dados para exibir", 
                    horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
            return fig
        
        # Preparar dados
        labels = allocation_summary["Tipo de FII"]
        sizes = allocation_summary["Percentual da Carteira (%)"]
        
        # Criar mapa de cores para os tipos de FIIs
        colors = {
            "cri": "#7fc97f",
            "shopping": "#beaed4",
            "logistica": "#fdc086",
            "escritorio": "#ffff99",
            "renda_urbana": "#386cb0",
            "fof": "#f0027f"
        }
        
        # Obter cores correspondentes a cada tipo
        plot_colors = [colors.get(label.lower(), "#cccccc") for label in labels]
        
        # Criar gráfico de pizza
        if sizes.sum() > 0:
            patches, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=plot_colors
            )
        else:
            ax.text(0.5, 0.5, "Sem alocação de investimento", 
                    horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
            return fig
        
        # Garantir que o gráfico seja um círculo
        ax.axis('equal')
        
        # Adicionar título
        plt.title("Distribuição do Portfólio por Tipo de FII")
        
        # Retornar figura
        return fig
        
    def _calculate_portfolio_dividend_yield(self, portfolio):
        """
        Calcula o dividend yield médio ponderado da carteira.
        
        Args:
            portfolio (list): Lista de FIIs no portfólio
            
        Returns:
            dict: Informações sobre o dividend yield da carteira
        """
        total_investment = sum(fii.get("investment", 0) for fii in portfolio)
        if total_investment == 0:
            return {
                "monthly_yield": 0.0,
                "annual_yield": 0.0,
                "monthly_income": 0.0,
                "annual_income": 0.0,
                "formatted_monthly_yield": "0,00%",
                "formatted_annual_yield": "0,00%"
            }
            
        total_monthly_income = sum(fii.get("monthly_income", 0) for fii in portfolio)
        monthly_yield = total_monthly_income / total_investment
        annual_yield = monthly_yield * 12
        
        return {
            "monthly_yield": monthly_yield,
            "annual_yield": annual_yield,
            "monthly_income": total_monthly_income,
            "annual_income": total_monthly_income * 12,
            "formatted_monthly_yield": format_percentage(monthly_yield),
            "formatted_annual_yield": format_percentage(annual_yield)
        } 