import pandas as pd
import matplotlib.pyplot as plt
from utils.constants import FII_TYPE_NAMES

def format_currency(value):
    """
    Formata um valor monetário para o formato brasileiro (R$).
    
    Args:
        value (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado como moeda
    """
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(value):
    """
    Formata um valor decimal como percentual.
    
    Args:
        value (float): Valor a ser formatado (ex: 0.27)
        
    Returns:
        str: Valor formatado como percentual (ex: 27,00%)
    """
    return f"{value * 100:.2f}%".replace(".", ",")

def create_comparison_chart(current_allocation, recommended_allocation):
    """
    Cria um gráfico de barras comparando a alocação atual com a recomendada.
    
    Args:
        current_allocation (dict): Alocação atual por tipo de FII
        recommended_allocation (dict): Alocação recomendada por tipo de FII
        
    Returns:
        matplotlib.figure.Figure: Figura com o gráfico de comparação
    """
    # Preparar dados
    types = list(recommended_allocation.keys())
    current_values = [current_allocation.get(t, 0) * 100 for t in types]
    recommended_values = [recommended_allocation[t] * 100 for t in types]
    
    # Usar nomes amigáveis para os tipos de FII
    labels = [FII_TYPE_NAMES.get(t, t) for t in types]
    
    # Configurar figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Largura das barras
    width = 0.35
    
    # Posição das barras
    x = range(len(types))
    
    # Criar barras
    ax.bar([i - width/2 for i in x], current_values, width, label='Alocação Atual', color='#3498db')
    ax.bar([i + width/2 for i in x], recommended_values, width, label='Alocação Recomendada', color='#2ecc71')
    
    # Adicionar rótulos e título
    ax.set_ylabel('Percentual (%)')
    ax.set_title('Comparação: Alocação Atual vs. Recomendada')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    
    # Ajustar layout
    plt.tight_layout()
    
    return fig

def calculate_expected_dividend(portfolio):
    """
    Calcula o dividend yield esperado para o portfólio.
    
    Args:
        portfolio (list): Lista de FIIs no portfólio com seus dados
        
    Returns:
        float: Dividend yield anual esperado (valor decimal)
    """
    total_investment = sum(fii.get("investment", 0) for fii in portfolio)
    total_dividend = sum(fii.get("investment", 0) * fii.get("dividendYield", 0) for fii in portfolio)
    
    if total_investment > 0:
        return total_dividend / total_investment
    return 0.0 