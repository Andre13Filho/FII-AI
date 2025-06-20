import streamlit as st
import os
from dotenv import load_dotenv
from agents.llm_agent import query_groq
from agents.market_agent import BrapiAgent, StatusInvestAgent
from agents.portfolio_agent import PortfolioAgent
from agents.investment_agent import InvestmentAgent
from agents.portfolio_analysis_agent import PortfolioAnalysisAgent
from utils.helpers import format_currency, format_percentage
import pandas as pd
from datetime import datetime

# Carregar variáveis de ambiente (Groq API Key e Brapi API Key)
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="FII AI - Recomendador de Fundos Imobiliários",
    page_icon="🏢",
    layout="wide"
)

# Inicializar agentes
@st.cache_resource
def get_investment_agent():
    return InvestmentAgent()

@st.cache_resource
def get_portfolio_analysis_agent():
    return PortfolioAnalysisAgent()

investment_agent = get_investment_agent()
portfolio_analysis_agent = get_portfolio_analysis_agent()

# Título da aplicação
st.title("FII AI - Recomendador de Fundos Imobiliários")
st.markdown("""
Esta aplicação utiliza inteligência artificial para recomendar uma carteira 
diversificada de Fundos de Investimento Imobiliário (FIIs) com base no seu patrimônio total.
O sistema considera que 25% do seu patrimônio será direcionado para FIIs, seguindo uma 
distribuição balanceada entre diferentes tipos de fundos.
""")

# Tabs para diferentes funcionalidades
tab1, tab2, tab3 = st.tabs(["Recomendação de Carteira", "Meus Investimentos", "Análise de Portfólio"])

# Tab 1: Recomendação de Carteira
with tab1:
    # Sidebar para entrada de dados
    with st.sidebar:
        st.header("Informações do Investidor")
        patrimonio = st.number_input(
            "Qual é o seu patrimônio total disponível?",
            min_value=1000.0,
            step=1000.0,
            format="%.2f"
        )
        
        # Mostrar valor a ser investido em FIIs (25% do patrimônio)
        if patrimonio > 0:
            valor_fii = patrimonio * 0.25
            st.info(f"Valor a ser investido em FIIs (25%): {format_currency(valor_fii)}")
        
        if st.button("Analisar e Recomendar"):
            if patrimonio > 0:
                with st.spinner("Analisando os melhores fundos imobiliários para você..."):
                    try:
                        # Obter contexto inicial da LLM usando Groq diretamente
                        prompt = f"""
                        Você é um assistente financeiro especializado em Fundos de Investimento Imobiliário (FIIs).
                        Seu objetivo é ajudar o usuário a construir uma carteira diversificada de FIIs.
                        
                        Contexto do usuário: O usuário tem um patrimônio total de R$ {patrimonio:.2f}, 
                        do qual 25% (R$ {patrimonio * 0.25:.2f}) será alocado em fundos imobiliários.
                        
                        Lembre-se que uma boa carteira de FIIs deve conter diferentes tipos de fundos:
                        - Fundos de CRI (27% da carteira de FIIs)
                        - Fundos de Shopping (17% da carteira de FIIs)
                        - Fundos de Logística (17% da carteira de FIIs)
                        - Fundos de Escritório (16% da carteira de FIIs)
                        - Fundos de Renda Urbana (9% da carteira de FIIs)
                        - Fundos de Fundos (FoF) (14% da carteira de FIIs)
                        
                        Forneça uma análise inicial sobre como podemos ajudar este investidor a alocar os 
                        R$ {patrimonio * 0.25:.2f} disponíveis para investimento em FIIs.
                        """
                        
                        user_context = query_groq(prompt)
                        st.session_state['llm_analysis'] = user_context
                        
                        # Criar e executar agentes de mercado
                        brapi_agent = BrapiAgent()
                        status_invest_agent = StatusInvestAgent()
                        
                        # Obter recomendações de fundos
                        st.session_state['fiis_cri'] = brapi_agent.get_best_fiis("cri")
                        st.session_state['fiis_shopping'] = brapi_agent.get_best_fiis("shopping")
                        st.session_state['fiis_logistica'] = brapi_agent.get_best_fiis("logistica")
                        st.session_state['fiis_escritorio'] = brapi_agent.get_best_fiis("escritorio")
                        st.session_state['fiis_renda_urbana'] = status_invest_agent.get_best_fiis("renda_urbana")
                        st.session_state['fiis_fof'] = status_invest_agent.get_best_fiis("fof")
                        
                        # Calcular alocação de portfólio
                        portfolio_agent = PortfolioAgent(patrimonio)
                        st.session_state['portfolio'] = portfolio_agent.calculate_portfolio(
                            fiis_cri=st.session_state['fiis_cri'],
                            fiis_shopping=st.session_state['fiis_shopping'],
                            fiis_logistica=st.session_state['fiis_logistica'],
                            fiis_escritorio=st.session_state['fiis_escritorio'],
                            fiis_renda_urbana=st.session_state['fiis_renda_urbana'],
                            fiis_fof=st.session_state['fiis_fof']
                        )
                        
                        st.success("Análise concluída!")
                    except Exception as e:
                        st.error(f"Ocorreu um erro durante a análise: {str(e)}")
            else:
                st.error("Por favor, informe um valor válido para o patrimônio.")

    # Corpo principal - exibir resultados
    if 'portfolio' in st.session_state:
        # Exibir análise da IA
        if 'llm_analysis' in st.session_state:
            st.header("Análise do Assistente IA")
            st.write(st.session_state['llm_analysis'])
            st.markdown("---")
        
        st.header("Sua carteira recomendada de FIIs")
        
        # Mostrar quanto está sendo investido
        portfolio = st.session_state['portfolio']
        st.info(f"""
        **Patrimônio total:** {format_currency(st.session_state['portfolio']['patrimonio_total'])}
        **Valor investido em FIIs (25%):** {format_currency(portfolio['total_investment'])}
        """)
        
        # Exibir resumo de rendimentos
        dividend_info = portfolio['portfolio_dividend_yield']
        
        st.success(f"""
        **Rendimento mensal estimado: {format_currency(dividend_info['monthly_income'])}** 
        ({dividend_info['formatted_monthly_yield']} ao mês)
        
        **Rendimento anual estimado: {format_currency(dividend_info['annual_income'])}** 
        ({dividend_info['formatted_annual_yield']} ao ano)
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Alocação por tipo de FII")
            
            # Exibir a distribuição da carteira em tabela
            st.dataframe(portfolio['allocation_summary'])
            
            # Exibir detalhes de cada FII recomendado
            st.subheader("Detalhes dos FIIs recomendados")
            
            # Preparar DataFrame para exibição detalhada dos FIIs
            detailed_portfolio = portfolio['detailed_portfolio']
            for fii in detailed_portfolio:
                # Formatar valores para exibição
                fii['formatted_price'] = format_currency(fii['price'])
                fii['formatted_investment'] = format_currency(fii['investment'])
                fii['formatted_dividend_yield'] = format_percentage(fii['dividend_yield'])
                fii['formatted_monthly_income'] = format_currency(fii['monthly_income'])
                fii['formatted_annual_income'] = format_currency(fii['annual_income'])
                
            # Criar DataFrame com colunas selecionadas e renomeadas
            df_display = pd.DataFrame(detailed_portfolio)
            
            # Verificar se DataFrame não está vazio
            if not df_display.empty:
                columns_to_display = {
                    'ticker': 'Ticker',
                    'type': 'Tipo', 
                    'formatted_price': 'Preço',
                    'shares': 'Qtd. Cotas',
                    'formatted_investment': 'Investimento',
                    'formatted_dividend_yield': 'Dividend Yield',
                    'formatted_monthly_income': 'Renda Mensal',
                    'formatted_annual_income': 'Renda Anual'
                }
                
                # Selecionar e renomear colunas
                df_display = df_display[[col for col in columns_to_display.keys() if col in df_display.columns]]
                df_display = df_display.rename(columns=columns_to_display)
                
                # Exibir DataFrame
                st.dataframe(df_display)
                
                # Exibir detalhes expandíveis para cada FII
                st.subheader("Análise detalhada dos FIIs recomendados")
                st.write("Expanda para ver detalhes sobre cada FII e por que você deve investir:")
                
                for fii in detailed_portfolio:
                    with st.expander(f"**{fii['ticker']}** - {fii['type'].capitalize()} ({fii['formatted_price']})"):
                        st.write(f"**Preço Atual:** {fii['formatted_price']}")
                        st.write(f"**Dividend Yield:** {fii['formatted_dividend_yield']}")
                        st.write(f"**Qtd. Cotas Recomendadas:** {fii['shares']}")
                        st.write(f"**Investimento Total:** {fii['formatted_investment']}")
                        st.write(f"**Rendimento Mensal Esperado:** {fii['formatted_monthly_income']}")
                        st.write(f"**Rendimento Anual Esperado:** {fii['formatted_annual_income']}")
                        
                        # Exibir explicação sobre por que investir neste FII
                        if "investment_explanation" in fii and fii["investment_explanation"]:
                            st.markdown("### Por que investir neste fundo?")
                            st.write(fii["investment_explanation"])
                
                # Adicionar botão para adicionar à carteira
                st.subheader("Adicionar à sua carteira")
                st.write("Selecione os FIIs recomendados que você deseja adicionar à sua carteira de investimentos:")
                
                for fii in detailed_portfolio:
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{fii['ticker']}**")
                    with col2:
                        st.write(f"Tipo: {fii['type']}")
                    with col3:
                        st.write(f"Preço: {fii['formatted_price']}")
                    with col4:
                        if st.button(f"Adicionar {fii['ticker']}", key=f"add_{fii['ticker']}"):
                            # Adicionar à carteira
                            success = investment_agent.register_investment(
                                ticker=fii['ticker'],
                                tipo=fii['type'],
                                preco=fii['price'],
                                quantidade=fii['shares']
                            )
                            if success:
                                st.success(f"{fii['ticker']} adicionado à sua carteira!")
                            else:
                                st.error(f"Erro ao adicionar {fii['ticker']} à sua carteira.")
            else:
                st.warning("Não há FIIs para exibir no momento.")
        
        with col2:
            st.subheader("Distribuição da Carteira")
            st.pyplot(portfolio['allocation_chart'])
            
            # Informações adicionais
            st.info(f"""
            **Alocação dentro dos 25% investidos em FIIs:**
            - 27% em Fundos CRI
            - 17% em Fundos de Shopping
            - 17% em Fundos de Logística
            - 16% em Fundos de Escritório
            - 9% em Renda Urbana
            - 14% em FoF
            """)
            
            # Adicionar informação sobre dividend yield
            st.info(f"""
            **Rendimento médio mensal:** {dividend_info['formatted_monthly_yield']}
            **Rendimento médio anual:** {dividend_info['formatted_annual_yield']}
            """)
    elif patrimonio > 0:
        st.info("Clique em 'Analisar e Recomendar' para obter sua carteira personalizada de FIIs.")
    else:
        st.info("Informe seu patrimônio total disponível na barra lateral para começar.")

# Tab 2: Meus Investimentos
with tab2:
    st.header("Minha Carteira de Investimentos")
    
    # Subtabs para diferentes visualizações
    subtab1, subtab2, subtab3, subtab4 = st.tabs(["Visão Geral", "Análise de Desempenho", "Registrar Operação", "Histórico de Operações"])
    
    # Subtab 1: Visão Geral
    with subtab1:
        # Resumo da carteira
        portfolio_summary = investment_agent.get_portfolio_summary()
        
        if portfolio_summary["total_investido"] > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Resumo da Carteira")
                st.info(f"""
                **Valor total investido:** {format_currency(portfolio_summary['total_investido'])}
                **Total de cotas:** {portfolio_summary['total_cotas']}
                """)
                
                # Exibir carteira atual
                st.subheader("Investimentos Atuais")
                df_portfolio = investment_agent.get_formatted_portfolio()
                st.dataframe(df_portfolio)
            
            with col2:
                st.subheader("Distribuição da Carteira")
                fig = investment_agent.get_portfolio_charts()
                st.pyplot(fig)
        else:
            st.info("Você ainda não possui investimentos registrados. Utilize a aba 'Registrar Operação' para adicionar seus investimentos.")
    
    # Subtab 2: Análise de Desempenho
    with subtab2:
        if st.button("Analisar Desempenho da Carteira"):
            with st.spinner("Analisando desempenho da carteira..."):
                try:
                    performance, df_performance, fig_performance = investment_agent.analyze_portfolio_performance()
                    
                    if performance and performance["valor_investido"] > 0:
                        # Exibir resumo do desempenho
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Resumo do Desempenho")
                            st.info(f"""
                            **Valor investido:** {format_currency(performance['valor_investido'])}
                            **Valor atual:** {format_currency(performance['valor_atual'])}
                            """)
                            
                            # Formatar lucro/prejuízo com cor
                            lucro = performance['lucro_prejuizo']
                            if lucro >= 0:
                                st.success(f"**Lucro: {format_currency(lucro)} ({format_percentage(performance['rentabilidade'])})**")
                            else:
                                st.error(f"**Prejuízo: {format_currency(lucro)} ({format_percentage(performance['rentabilidade'])})**")
                        
                        with col2:
                            st.subheader("Rentabilidade por FII")
                            if fig_performance:
                                st.pyplot(fig_performance)
                        
                        # Exibir detalhes por FII
                        st.subheader("Detalhes do Desempenho")
                        st.dataframe(df_performance)
                    else:
                        st.warning("Você não possui investimentos para analisar.")
                except Exception as e:
                    st.error(f"Erro ao analisar desempenho: {str(e)}")
    
    # Subtab 3: Registrar Operação
    with subtab3:
        st.subheader("Registrar Nova Operação")
        
        # Opções de operação
        operacao = st.radio("Tipo de Operação", ["Compra", "Venda"])
        
        # Formulário para registrar operação
        with st.form("form_operacao"):
            col1, col2 = st.columns(2)
            
            with col1:
                ticker = st.text_input("Ticker do FII (ex: HGLG11)").upper()
                
                if operacao == "Compra":
                    tipos_fii = ["CRI", "Shopping", "Logística", "Escritório", "Renda Urbana", "FoF", "Outros"]
                    tipo_fii = st.selectbox("Tipo de FII", tipos_fii)
                
                quantidade = st.number_input("Quantidade de Cotas", min_value=1, step=1)
                
            with col2:
                preco = st.number_input("Preço Unitário (R$)", min_value=0.01, step=0.01, format="%.2f")
                
                data_atual = datetime.now().strftime("%Y-%m-%d")
                data = st.date_input("Data da Operação", 
                                    value=datetime.strptime(data_atual, "%Y-%m-%d"))
                data_str = data.strftime("%Y-%m-%d")
                
                valor_total = quantidade * preco
                st.info(f"Valor Total: {format_currency(valor_total)}")
            
            submitted = st.form_submit_button("Registrar Operação")
            
            if submitted:
                if not ticker:
                    st.error("Por favor, informe o ticker do FII.")
                elif operacao == "Compra" and not tipo_fii:
                    st.error("Por favor, selecione o tipo de FII.")
                elif quantidade <= 0:
                    st.error("A quantidade de cotas deve ser maior que zero.")
                elif preco <= 0:
                    st.error("O preço unitário deve ser maior que zero.")
                else:
                    try:
                        if operacao == "Compra":
                            success = investment_agent.register_investment(
                                ticker=ticker,
                                tipo=tipo_fii,
                                preco=preco,
                                quantidade=quantidade,
                                data=data_str
                            )
                            if success:
                                st.success(f"Compra de {quantidade} cotas de {ticker} registrada com sucesso!")
                            else:
                                st.error("Erro ao registrar a compra.")
                        else:  # Venda
                            success = investment_agent.register_sale(
                                ticker=ticker,
                                quantidade=quantidade,
                                preco=preco,
                                data=data_str
                            )
                            if success:
                                st.success(f"Venda de {quantidade} cotas de {ticker} registrada com sucesso!")
                            else:
                                st.error("Erro ao registrar a venda. Verifique se você possui cotas suficientes.")
                    except Exception as e:
                        st.error(f"Erro ao registrar operação: {str(e)}")
    
    # Subtab 4: Histórico de Operações
    with subtab4:
        st.subheader("Histórico de Operações")
        
        # Filtro por ticker
        tickers = [inv["ticker"] for inv in investment_agent.get_current_portfolio()]
        ticker_filter = st.selectbox("Filtrar por FII (opcional)", ["Todos"] + tickers, index=0)
        
        filter_ticker = None if ticker_filter == "Todos" else ticker_filter
        
        # Obter histórico
        df_history = investment_agent.get_investment_history(ticker=filter_ticker)
        
        if not df_history.empty:
            st.dataframe(df_history)
        else:
            st.info("Nenhuma operação encontrada com os filtros selecionados.")

# Tab 3: Análise de Portfólio
with tab3:
    st.header("Análise Inteligente de Portfólio")
    
    portfolio_summary = investment_agent.get_portfolio_summary()
    if portfolio_summary["total_investido"] > 0:
        # Mostrar resumo básico da carteira
        st.info(f"""
        **Valor total investido em FIIs:** {format_currency(portfolio_summary['total_investido'])}
        **Total de FIIs na carteira:** {len(investment_agent.get_current_portfolio())}
        """)
        
        # Formulário para solicitar análise
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Obter Recomendações para sua Carteira")
            
            with st.form("form_analise"):
                # Opção para informar valor de investimento
                option = st.radio(
                    "Valor para novos investimentos:",
                    ["Usar 5% do valor atual da carteira", "Informar valor específico"]
                )
                
                investment_amount = None
                if option == "Informar valor específico":
                    investment_amount = st.number_input(
                        "Valor disponível para investimento (R$)",
                        min_value=100.0,
                        step=100.0,
                        format="%.2f"
                    )
                
                submitted = st.form_submit_button("Analisar minha Carteira")
                
                if submitted:
                    with st.spinner("Analisando sua carteira e obtendo recomendações..."):
                        # Obter sugestões formatadas
                        df_suggestions, message = portfolio_analysis_agent.get_formatted_suggestions(investment_amount)
                        
                        # Obter recomendações da IA
                        ai_recommendations = portfolio_analysis_agent.get_ai_recommendations(investment_amount)
                        
                        # Guardar resultados na sessão
                        st.session_state['df_suggestions'] = df_suggestions
                        st.session_state['suggestion_message'] = message
                        st.session_state['ai_recommendations'] = ai_recommendations
        
        with col2:
            st.subheader("Distribuição Atual")
            fig = investment_agent.get_portfolio_charts()
            st.pyplot(fig)
        
        # Exibir resultados da análise, se disponíveis
        if 'df_suggestions' in st.session_state:
            st.markdown("---")
            st.subheader("Resultados da Análise")
            
            st.write(st.session_state['suggestion_message'])
            
            if not st.session_state['df_suggestions'].empty:
                st.subheader("Sugestões de Rebalanceamento")
                st.dataframe(st.session_state['df_suggestions'])
                
                # Adicionar botões para adicionar sugestões
                st.subheader("Adicionar Sugestões à Carteira")
                
                for idx, row in st.session_state['df_suggestions'].iterrows():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.write(f"**{row['Ticker']}**")
                    with col2:
                        st.write(f"Tipo: {row['Tipo']} | {row['Cotas Sugeridas']} cotas a {row['Preço']}")
                    with col3:
                        if st.button(f"Adicionar {row['Ticker']}", key=f"add_suggest_{idx}"):
                            # Extrair preço numérico do formato R$ X.XXX,XX
                            preco_str = row['Preço'].replace('R$', '').replace('.', '').replace(',', '.').strip()
                            preco = float(preco_str)
                            
                            success = investment_agent.register_investment(
                                ticker=row['Ticker'],
                                tipo=row['Tipo'],
                                preco=preco,
                                quantidade=row['Cotas Sugeridas']
                            )
                            if success:
                                st.success(f"{row['Ticker']} adicionado à sua carteira!")
                            else:
                                st.error(f"Erro ao adicionar {row['Ticker']} à sua carteira.")
            
            if 'ai_recommendations' in st.session_state:
                st.subheader("Análise do Assistente IA")
                st.write(st.session_state['ai_recommendations'])
    else:
        st.warning("Você ainda não possui investimentos registrados. Utilize a aba 'Meus Investimentos' para adicionar seus FIIs antes de solicitar uma análise.")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido com ❤️ usando Streamlit e modelo LLaMA 3 da Groq")