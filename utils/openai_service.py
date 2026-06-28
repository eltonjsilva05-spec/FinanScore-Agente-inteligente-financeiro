import os
import requests

def perguntar_openai(pergunta: str, contexto: str) -> str:
    """
    Envia uma pergunta ao motor do Gemini utilizando requisição HTTP direta.
    Abordagem imune a conflitos de bibliotecas/SDKs desatualizados locais.
    """
    try:
        # 1. Recupera a chave de API salva no ambiente ou no secrets.toml do Streamlit
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return (
                "🚨 Erro de Configuração: A variável 'GEMINI_API_KEY' não foi encontrada. "
                "Certifique-se de que ela está configurada no seu arquivo .streamlit/secrets.toml "
                "ou nas variáveis de ambiente do seu sistema."
            )

        # 2. Rota de produção estável (v1) utilizando o modelo estável atualizado
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # 3. Estruturação do Prompt de Engenharia de Contexto para a IA Financeira
        prompt_completo = f"""
        Você é o consultor financeiro oficial integrado ao ecossistema FinanScore.
        Sua missão é responder às dúvidas do usuário com tom profissional, encorajador, didático e analítico.
        Baseie-se estritamente nos dados fornecidos no contexto abaixo para formular suas dicas e análises.
        
        CONTEXTO DO USUÁRIO OPERANTE:
        {contexto}
        
        PERGUNTA DO USUÁRIO:
        {pergunta}
        """
        
        # 4. Montagem dos Headers e Payload no padrão exigido pela API do Google
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_completo}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3  # Mantido baixo para priorizar precisão matemática e evitar alucinações
            }
        }
        
        # 5. Dispara a requisição para os servidores do Google
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        # 6. Tratamento do retorno e extração do texto da resposta
        if response.status_code == 200:
            try:
                texto_resposta = response_data['candidates'][0]['content']['parts'][0]['text']
                return str(texto_resposta)
            except (KeyError, IndexError):
                return "Desculpe, a API do Google respondeu com um formato inesperado de dados."
        else:
            # Captura a mensagem detalhada enviada pelo servidor do Google em caso de erro
            erro_msg = response_data.get('error', {}).get('message', 'Erro desconhecido')
            return f"Erro na API do Google (Código {response.status_code}): {erro_msg}"

    except Exception as e:
        return f"Desculpe, falha crítica na conexão com o motor do Gemini: {str(e)}"