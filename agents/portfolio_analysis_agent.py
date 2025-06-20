import pandas as pd
import numpy as np
from agents.llm_agent import query_groq
from agents.investment_agent import InvestmentAgent
from agents.market_agent import BrapiAgent
from utils.helpers import format_currency, format_percentage

class PortfolioAnalysisAgent:
    """
    Agente responsável por analisar a carteira atual do usuário e sugerir
    novos investimentos com base na análise de desempenho e diversificação.
    """
    def __init__(self):
        self.investment_agent = InvestmentAgent()
        self.brapi_agent = BrapiAgent()
    
    def analyze_portfolio_balance(self):
        """
        Analisa o equilíbrio da carteira atual em termos de diversificação.
        
        Returns:
            dict: Análise do equilíbrio da carteira
        """
        portfolio_summary = self.investment_agent.get_portfolio_summary()
        
        # Se não houver investimentos, retorna análise vazia
        if portfolio_summary["total_investido"] == 0:
            return {
                "portfolio_empty": True,
                "message": "Não há investimentos registrados para análise."
            }
        
        # Distribuição ideal
        ideal_distribution = {
            "CRI": 27,
            "Shopping": 17,
            "Logística": 17,
            "Escritório": 16,
            "Renda Urbana": 9,
            "FoF": 14
        }
        
        # Distribuição atual
        current_distribution = portfolio_summary["distribuicao_por_tipo"]
        
        # Comparar distribuições e identificar tipos subrepresentados e superrepresentados
        balance_analysis = {
            "portfolio_empty": False,
            "current_distribution": current_distribution,
            "ideal_distribution": ideal_distribution,
            "deviations": {},
            "unbalanced_types": {"over": [], "under": []}
        }
        
        # Calcular desvios
        for tipo, ideal_percent in ideal_distribution.items():
            current_percent = current_distribution.get(tipo, 0)
            deviation = current_percent - ideal_percent
            balance_analysis["deviations"][tipo] = deviation
            
            # Classificar como sub ou superrepresentado (margem de 5%)
            if deviation < -5:
                balance_analysis["unbalanced_types"]["under"].append({
                    "tipo": tipo,
                    "atual": current_percent,
                    "ideal": ideal_percent,
                    "desvio": deviation
                })
            elif deviation > 5:
                balance_analysis["unbalanced_types"]["over"].append({
                    "tipo": tipo,
                    "atual": current_percent,
                    "ideal": ideal_percent,
                    "desvio": deviation
                })
        
        # Tipos que não estão na carteira
        missing_types = [tipo for tipo in ideal_distribution.keys() 
                        if tipo not in current_distribution]
        
        for tipo in missing_types:
            balance_analysis["unbalanced_types"]["under"].append({
                "tipo": tipo,
                "atual": 0,
                "ideal": ideal_distribution[tipo],
                "desvio": -ideal_distribution[tipo]
            })
        
        # Tipos na carteira que não estão no ideal (ex: "Outros")
        extra_types = [tipo for tipo in current_distribution.keys() 
                      if tipo not in ideal_distribution]
        
        balance_analysis["extra_types"] = extra_types
        
        return balance_analysis
    
    def suggest_rebalancing(self, investment_amount=None):
        """
        Sugere FIIs para investimento com base no rebalanceamento da carteira.
        
        Args:
            investment_amount (float, opcional): Valor disponível para investimento
        
        Returns:
            dict: Sugestões de investimento para rebalancear a carteira
        """
        # Analisar equilíbrio atual
        balance_analysis = self.analyze_portfolio_balance()
        
        if balance_analysis["portfolio_empty"]:
            # Se carteira estiver vazia, retornar sugestão de criar uma nova
            return {
                "message": "Você ainda não possui investimentos. Recomendamos criar uma carteira diversificada.",
                "suggestions_empty": True
            }
        
        # Ordenar tipos subrepresentados pelo desvio (mais negativos primeiro)
        types_to_increase = sorted(
            balance_analysis["unbalanced_types"]["under"],
            key=lambda x: x["desvio"]
        )
        
        # Se não houver valor de investimento, considerar 5% do total da carteira atual
        portfolio_summary = self.investment_agent.get_portfolio_summary()
        total_invested = portfolio_summary["total_investido"]
        
        if not investment_amount:
            investment_amount = total_invested * 0.05
        
        # Calcula quanto investir em cada tipo
        suggestions = {
            "message": "Sugestões para rebalancear sua carteira:",
            "investment_amount": investment_amount,
            "suggestions_empty": len(types_to_increase) == 0,
            "suggestions_by_type": []
        }
        
        # Se não há tipos subrepresentados, sugerir manter a carteira
        if not types_to_increase:
            suggestions["message"] = "Sua carteira está bem balanceada! Não há necessidade de rebalanceamento significativo."
            return suggestions
        
        # Calcular o total de desvio negativo
        total_negative_deviation = sum(abs(tipo["desvio"]) for tipo in types_to_increase)
        
        # Distribuir o valor de investimento proporcionalmente ao desvio
        for tipo_info in types_to_increase:
            tipo = tipo_info["tipo"]
            desvio = abs(tipo_info["desvio"])
            
            # Calcular valor a investir neste tipo
            tipo_allocation = (desvio / total_negative_deviation) * investment_amount
            
            # Buscar melhores FIIs deste tipo
            best_fiis = self.brapi_agent.get_best_fiis(tipo.lower())
            
            type_suggestion = {
                "tipo": tipo,
                "desvio_percentual": tipo_info["desvio"],
                "atual_percentual": tipo_info["atual"],
                "ideal_percentual": tipo_info["ideal"],
                "valor_alocado": tipo_allocation,
                "fiis_recomendados": []
            }
            
            # Selecionar os 3 melhores FIIs
            for fii in best_fiis[:3]:
                # Obter preço atual
                try:
                    preco = self.brapi_agent.get_ticker_price(fii["ticker"])
                    # Calcular quantidade de cotas
                    cotas = max(1, int(tipo_allocation / (3 * preco)))
                    
                    fii_suggestion = {
                        "ticker": fii["ticker"],
                        "preco": preco,
                        "cotas_sugeridas": cotas,
                        "investimento_sugerido": cotas * preco,
                        "dividend_yield": fii.get("dividend_yield", 0)
                    }
                    
                    type_suggestion["fiis_recomendados"].append(fii_suggestion)
                except Exception:
                    # Se não conseguir obter o preço, pular este FII
                    continue
            
            suggestions["suggestions_by_type"].append(type_suggestion)
        
        return suggestions
    
    def get_ai_recommendations(self, investment_amount=None):
        """
        Obtém recomendações de IA para melhorar a carteira do usuário.
        
        Args:
            investment_amount (float, opcional): Valor disponível para investimento
        
        Returns:
            str: Recomendações textuais da IA
        """
        # Obter dados da carteira atual
        portfolio = self.investment_agent.get_current_portfolio()
        portfolio_summary = self.investment_agent.get_portfolio_summary()
        
        # Obter sugestões de rebalanceamento
        rebalancing = self.suggest_rebalancing(investment_amount)
        
        # Preparar contexto para a IA
        if portfolio:
            tickers_atuais = [inv["ticker"] for inv in portfolio]
            tickers_str = ", ".join(tickers_atuais)
            
            distribuicao = portfolio_summary["distribuicao_por_tipo"]
            distribuicao_str = "\n".join([f"- {tipo}: {porcentagem:.1f}%" 
                                         for tipo, porcentagem in distribuicao.items()])
            
            valor_total = format_currency(portfolio_summary["total_investido"])
            
            # Preparar informações de sugestões
            if not rebalancing["suggestions_empty"]:
                sugestoes = []
                for tipo in rebalancing["suggestions_by_type"]:
                    fiis_sugeridos = [f"{fii['ticker']} ({format_currency(fii['preco'])} - {fii['cotas_sugeridas']} cotas)" 
                                     for fii in tipo["fiis_recomendados"]]
                    fiis_str = ", ".join(fiis_sugeridos)
                    sugestoes.append(f"- {tipo['tipo']}: {fiis_str}")
                
                sugestoes_str = "\n".join(sugestoes)
                
                context = f"""
                Analise a carteira atual de FIIs do investidor e forneça recomendações inteligentes.
                
                Carteira atual:
                - Valor total: {valor_total}
                - FIIs na carteira: {tickers_str}
                
                Distribuição atual por tipo:
                {distribuicao_str}
                
                Recomendações de rebalanceamento:
                {sugestoes_str}
                
                Valor disponível para investimento: {format_currency(rebalancing["investment_amount"])}
                
                Como especialista em FIIs, forneça:
                1. Uma análise da carteira atual do investidor
                2. Recomendações para melhorar a diversificação e performance
                3. Justificativa para as recomendações sugeridas
                4. Comentários sobre o mercado atual de FIIs
                
                Seja específico e utilize os dados da carteira atual e as sugestões de rebalanceamento.
                """
            else:
                context = f"""
                Analise a carteira atual de FIIs do investidor e forneça recomendações inteligentes.
                
                Carteira atual:
                - Valor total: {valor_total}
                - FIIs na carteira: {tickers_str}
                
                Distribuição atual por tipo:
                {distribuicao_str}
                
                A carteira está bem balanceada.
                
                Como especialista em FIIs, forneça:
                1. Uma análise da carteira atual do investidor
                2. Recomendações para melhorar a performance mantendo a diversificação
                3. Comentários sobre o mercado atual de FIIs
                
                Seja específico e utilize os dados da carteira atual.
                """
        else:
            # Caso a carteira esteja vazia
            context = """
            O investidor ainda não possui FIIs em sua carteira.
            
            Como especialista em FIIs, forneça:
            1. Recomendações para iniciar uma carteira diversificada de FIIs
            2. Estratégias para um investidor iniciante no mercado de FIIs
            3. Comentários sobre o mercado atual de FIIs
            
            Seja específico e didático, considerando que o investidor está começando.
            """
        
        # Consultar a IA para obter recomendações
        try:
            recommendations = query_groq(context)
            return recommendations
        except Exception as e:
            return f"Não foi possível obter recomendações da IA: {str(e)}"
    
    def get_formatted_suggestions(self, investment_amount=None):
        """
        Formata as sugestões de rebalanceamento para exibição.
        
        Args:
            investment_amount (float, opcional): Valor disponível para investimento
        
        Returns:
            tuple: (pd.DataFrame - sugestões, str - mensagem)
        """
        suggestions = self.suggest_rebalancing(investment_amount)
        
        if suggestions["suggestions_empty"]:
            return pd.DataFrame(), suggestions["message"]
        
        # Preparar dados para o DataFrame
        suggestion_data = []
        
        for tipo in suggestions["suggestions_by_type"]:
            for fii in tipo["fiis_recomendados"]:
                suggestion_data.append({
                    "Tipo": tipo["tipo"],
                    "Ticker": fii["ticker"],
                    "Preço": fii["preco"],
                    "Cotas Sugeridas": fii["cotas_sugeridas"],
                    "Investimento Sugerido": fii["investimento_sugerido"],
                    "Dividend Yield": fii.get("dividend_yield", 0) * 100  # Converter para percentual
                })
        
        if not suggestion_data:
            return pd.DataFrame(), "Não foi possível encontrar FIIs adequados para sugestão."
        
        df = pd.DataFrame(suggestion_data)
        
        # Formatar valores
        df_display = df.copy()
        df_display["Preço"] = df_display["Preço"].apply(format_currency)
        df_display["Investimento Sugerido"] = df_display["Investimento Sugerido"].apply(format_currency)
        df_display["Dividend Yield"] = df_display["Dividend Yield"].apply(lambda x: f"{x:.2f}%")
        
        return df_display, suggestions["message"] 