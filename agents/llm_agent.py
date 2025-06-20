import os
import groq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFaceHub

def query_groq(prompt, model_name="llama3-70b-8192", temperature=0.2, max_tokens=1024):
    """
    Envia um prompt para a API do Groq e retorna a resposta.
    
    Args:
        prompt (str): O texto a ser enviado para o modelo
        model_name (str): Nome do modelo a ser usado
        temperature (float): Controle de aleatoriedade (0 a 1)
        max_tokens (int): Número máximo de tokens na resposta
        
    Returns:
        str: Resposta do modelo
    """
    # Verificar chave de API
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "A chave de API GROQ_API_KEY não foi encontrada. "
            "Por favor, configure essa variável de ambiente."
        )
    
    # Criar cliente Groq
    client = groq.Client(api_key=api_key)
    
    # Enviar a solicitação
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar Groq API: {e}")
        raise e

def create_llm_chain():
    """
    Cria e retorna uma LLMChain que usa um modelo de fallback do Hugging Face 
    para demonstração. Para usar o Groq, o código principal será alterado para 
    chamar diretamente a função query_groq.
    """
    # Usamos HuggingFace como fallback para integração com LangChain
    # Na aplicação principal, vamos chamar diretamente a função query_groq
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-large",
        model_kwargs={"temperature": 0.5, "max_length": 512}
    )
    
    # Template do prompt para o assistente de FIIs
    template = """
    Você é um assistente financeiro especializado em Fundos de Investimento Imobiliário (FIIs).
    Seu objetivo é ajudar o usuário a construir uma carteira diversificada de FIIs com base no patrimônio disponível.
    
    Contexto do usuário: {user_input}
    
    Lembre-se que uma boa carteira de FIIs deve conter diferentes tipos de fundos:
    - Fundos de CRI (27% da carteira)
    - Fundos de Shopping (17% da carteira)
    - Fundos de Logística (17% da carteira)
    - Fundos de Escritório (16% da carteira)
    - Fundos de Renda Urbana (9% da carteira)
    - Fundos de Fundos (FoF) (14% da carteira)
    
    Forneça uma análise inicial sobre como podemos ajudar este investidor.
    """
    
    # Criar o prompt
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=template
    )
    
    # Criar e retornar a chain
    return LLMChain(llm=llm, prompt=prompt) 