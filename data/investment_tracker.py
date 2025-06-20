import os
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

class InvestmentTracker:
    """
    Classe para rastrear e analisar os investimentos do usuário em FIIs ao longo do tempo.
    """
    def __init__(self, data_dir="data"):
        """
        Inicializa o rastreador de investimentos.
        
        Args:
            data_dir (str): Diretório onde os dados serão armazenados
        """
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "investment_history.json")
        # Garantir que o diretório de dados exista
        os.makedirs(data_dir, exist_ok=True)
        # Inicializar histórico
        self.load_history()
    
    def load_history(self):
        """Carrega o histórico de investimentos do arquivo JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                # Em caso de arquivo corrompido, inicia um novo histórico
                self.history = {"investments": []}
        else:
            # Se o arquivo não existir, cria um novo histórico
            self.history = {"investments": []}
    
    def save_history(self):
        """Salva o histórico de investimentos no arquivo JSON"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)
    
    def add_investment(self, ticker, tipo, preco, quantidade, data=None):
        """
        Adiciona um novo investimento ao histórico.
        
        Args:
            ticker (str): O código do FII (ex: MXRF11)
            tipo (str): O tipo de FII (ex: "CRI", "Shopping", etc.)
            preco (float): O preço unitário do FII
            quantidade (int): Quantidade de cotas adquiridas
            data (str, opcional): Data da aquisição (formato YYYY-MM-DD)
        """
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")
        
        # Verificar se já existe este ticker na carteira
        existing_investment = None
        for inv in self.history["investments"]:
            if inv["ticker"] == ticker:
                existing_investment = inv
                break
        
        # Se o investimento já existe, atualiza a posição
        if existing_investment:
            # Calcula o preço médio ponderado
            total_anterior = existing_investment["quantidade"] * existing_investment["preco_medio"]
            total_novo = quantidade * preco
            nova_quantidade = existing_investment["quantidade"] + quantidade
            novo_preco_medio = (total_anterior + total_novo) / nova_quantidade
            
            # Atualiza os valores
            existing_investment["quantidade"] = nova_quantidade
            existing_investment["preco_medio"] = novo_preco_medio
            existing_investment["transacoes"].append({
                "data": data,
                "operacao": "compra",
                "quantidade": quantidade,
                "preco": preco
            })
        else:
            # Se é um novo investimento, adiciona ao histórico
            novo_investimento = {
                "ticker": ticker,
                "tipo": tipo,
                "preco_medio": preco,
                "quantidade": quantidade,
                "data_inicial": data,
                "transacoes": [{
                    "data": data,
                    "operacao": "compra",
                    "quantidade": quantidade,
                    "preco": preco
                }]
            }
            self.history["investments"].append(novo_investimento)
        
        # Salva as alterações
        self.save_history()
        
    def remove_investment(self, ticker, quantidade, preco, data=None):
        """
        Registra a venda de um investimento.
        
        Args:
            ticker (str): O código do FII
            quantidade (int): Quantidade de cotas vendidas
            preco (float): Preço unitário da venda
            data (str, opcional): Data da venda (formato YYYY-MM-DD)
        
        Returns:
            bool: True se a venda foi registrada com sucesso, False caso contrário
        """
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")
            
        # Procura o investimento
        for i, inv in enumerate(self.history["investments"]):
            if inv["ticker"] == ticker:
                # Verifica se há quantidade suficiente
                if inv["quantidade"] < quantidade:
                    return False
                
                # Registra a venda
                inv["transacoes"].append({
                    "data": data,
                    "operacao": "venda",
                    "quantidade": quantidade,
                    "preco": preco
                })
                
                # Atualiza a quantidade
                inv["quantidade"] -= quantidade
                
                # Se a quantidade chegou a zero, remove o investimento
                if inv["quantidade"] == 0:
                    self.history["investments"].pop(i)
                
                # Salva as alterações
                self.save_history()
                return True
                
        return False
    
    def get_current_portfolio(self):
        """
        Retorna a carteira atual do usuário.
        
        Returns:
            list: Lista de dicionários com os investimentos atuais
        """
        return self.history["investments"]
    
    def get_portfolio_summary(self):
        """
        Retorna um resumo da carteira atual com valor total investido,
        distribuição por tipo de FII e outras métricas.
        
        Returns:
            dict: Resumo da carteira de investimentos
        """
        if not self.history["investments"]:
            return {
                "total_investido": 0,
                "total_cotas": 0,
                "distribuicao_por_tipo": {},
                "distribuicao_por_ticker": {}
            }
        
        total_investido = 0
        total_cotas = 0
        distribuicao_por_tipo = {}
        distribuicao_por_ticker = {}
        
        for inv in self.history["investments"]:
            valor_investido = inv["quantidade"] * inv["preco_medio"]
            total_investido += valor_investido
            total_cotas += inv["quantidade"]
            
            # Distribuição por tipo
            if inv["tipo"] not in distribuicao_por_tipo:
                distribuicao_por_tipo[inv["tipo"]] = 0
            distribuicao_por_tipo[inv["tipo"]] += valor_investido
            
            # Distribuição por ticker
            distribuicao_por_ticker[inv["ticker"]] = valor_investido
        
        # Normalizar as distribuições para porcentagens
        for tipo in distribuicao_por_tipo:
            distribuicao_por_tipo[tipo] = (distribuicao_por_tipo[tipo] / total_investido) * 100
            
        for ticker in distribuicao_por_ticker:
            distribuicao_por_ticker[ticker] = (distribuicao_por_ticker[ticker] / total_investido) * 100
        
        return {
            "total_investido": total_investido,
            "total_cotas": total_cotas,
            "distribuicao_por_tipo": distribuicao_por_tipo,
            "distribuicao_por_ticker": distribuicao_por_ticker
        }
    
    def generate_portfolio_charts(self):
        """
        Gera gráficos de análise da carteira atual.
        
        Returns:
            matplotlib.figure.Figure: Figura com os gráficos gerados
        """
        summary = self.get_portfolio_summary()
        
        if summary["total_investido"] == 0:
            # Criar uma figura vazia se não houver investimentos
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, "Nenhum investimento registrado", 
                    ha='center', va='center', fontsize=14)
            ax.axis('off')
            return fig
        
        # Criar figura com dois subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Gráfico de distribuição por tipo
        tipos = list(summary["distribuicao_por_tipo"].keys())
        valores_tipo = list(summary["distribuicao_por_tipo"].values())
        
        ax1.pie(valores_tipo, labels=tipos, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Distribuição por Tipo de FII")
        
        # Gráfico de distribuição por ticker (top 10 se houver mais que 10)
        tickers = list(summary["distribuicao_por_ticker"].keys())
        valores_ticker = list(summary["distribuicao_por_ticker"].values())
        
        if len(tickers) > 10:
            # Ordenar e pegar os top 10
            ticker_data = sorted(zip(tickers, valores_ticker), 
                                 key=lambda x: x[1], reverse=True)
            top_tickers = [t[0] for t in ticker_data[:9]]
            top_valores = [t[1] for t in ticker_data[:9]]
            
            # Adicionar "Outros" para o restante
            outros_valor = sum([t[1] for t in ticker_data[9:]])
            if outros_valor > 0:
                top_tickers.append("Outros")
                top_valores.append(outros_valor)
                
            ax2.pie(top_valores, labels=top_tickers, autopct='%1.1f%%', startangle=90)
            ax2.set_title("Top 10 FIIs por Valor Investido")
        else:
            ax2.pie(valores_ticker, labels=tickers, autopct='%1.1f%%', startangle=90)
            ax2.set_title("Distribuição por FII")
        
        plt.tight_layout()
        return fig
    
    def analyze_performance(self, precos_atuais):
        """
        Analisa o desempenho da carteira com base nos preços atuais.
        
        Args:
            precos_atuais (dict): Dicionário com {ticker: preco_atual}
        
        Returns:
            dict: Análise de desempenho da carteira
        """
        if not self.history["investments"]:
            return {
                "valor_atual": 0,
                "valor_investido": 0,
                "lucro_prejuizo": 0,
                "rentabilidade": 0,
                "detalhes_por_fii": []
            }
        
        valor_atual_total = 0
        valor_investido_total = 0
        detalhes = []
        
        for inv in self.history["investments"]:
            ticker = inv["ticker"]
            if ticker in precos_atuais:
                preco_atual = precos_atuais[ticker]
                valor_atual = inv["quantidade"] * preco_atual
                valor_investido = inv["quantidade"] * inv["preco_medio"]
                lucro_prejuizo = valor_atual - valor_investido
                rentabilidade = (lucro_prejuizo / valor_investido) * 100 if valor_investido > 0 else 0
                
                valor_atual_total += valor_atual
                valor_investido_total += valor_investido
                
                detalhes.append({
                    "ticker": ticker,
                    "tipo": inv["tipo"],
                    "quantidade": inv["quantidade"],
                    "preco_medio": inv["preco_medio"],
                    "preco_atual": preco_atual,
                    "valor_investido": valor_investido,
                    "valor_atual": valor_atual,
                    "lucro_prejuizo": lucro_prejuizo,
                    "rentabilidade": rentabilidade
                })
        
        lucro_prejuizo_total = valor_atual_total - valor_investido_total
        rentabilidade_total = (lucro_prejuizo_total / valor_investido_total) * 100 if valor_investido_total > 0 else 0
        
        return {
            "valor_atual": valor_atual_total,
            "valor_investido": valor_investido_total,
            "lucro_prejuizo": lucro_prejuizo_total,
            "rentabilidade": rentabilidade_total,
            "detalhes_por_fii": detalhes
        } 