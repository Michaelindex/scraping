import base64
import os
import time
from google import genai
from google.genai import types

# Variáveis do médico
crm_medico = "2875"
nome_medico = "CARLOS"
sobrenome_medico = "EDUARDO RYUJI NISHIO"
especialidade_medica = "Dermatologia"
endereco_completo = "Av. Bosque da Saúde, 1645, Bosque da Saúde - São Paulo/SP, 04142-092"
logradouro = "Av. Bosque da Saúde"
numero = "1645"
bairro = "Bosque da Saúde"
cep = "04142-092"
cidade = "São Paulo"
estado = "SP"

def generate():
    # Início da contagem de tempo
    tempo_inicio = time.time()
    
    try:
        # Lê a chave da API do arquivo
        with open("api.key", "r") as f:
            api_key = f.read().strip()
            
        if not api_key:
            raise ValueError("O arquivo api.key está vazio. Por favor, adicione sua chave da API do Google Gemini.")

        client = genai.Client(
            api_key=api_key,
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"""
                    DADOS JÁ CONHECIDOS:
                    CRM_MEDICO: {crm_medico}
                    NOME_MEDICO: {nome_medico}
                    SOBRENOME_MEDICO: {sobrenome_medico}
                    ESPECIALIDADE: {especialidade_medica}
                    ENDEREÇO COMPLETO: {endereco_completo}
                    LOGRADOURO: {logradouro}
                    NÚMERO: {numero}
                    BAIRRO: {bairro}
                    CEP: {cep}
                    CIDADE: {cidade}
                    ESTADO: {estado}

                    Atue como um assistente de extração de dados médicos. Sua tarefa é encontrar APENAS as seguintes informações para o médico [CRM_MEDICO={crm_medico}], [NOME_MEDICO={nome_medico}] [SOBRENOME_MEDICO={sobrenome_medico}]:
                    
                    Campos a serem encontrados:
                    1. Complemento (referência do local)
                    2. Telefones do local de trabalho (Telefone A1 e A2)
                    3. Celulares (Celular A1 e A2)
                    4. E-mails (E-mail A1 e A2)

                    **Instruções Cruciais:**

                    1. **Prioridade de Busca:**
                       - Para Celulares: Primeiro tente encontrar o número pessoal do médico, se não encontrar, busque o número profissional direto.
                       - Para E-mails: Primeiro tente encontrar o e-mail pessoal do médico, se não encontrar, busque o e-mail profissional, e por último o e-mail de contato da empresa.

                    2. **Foco dos Telefones:**
                       - "Telefone A1" e "Telefone A2": Devem ser números de telefone fixo COMPLETOS do **local de trabalho** do médico.
                       - "Celular A1" e "Celular A2": Devem ser números de celular COMPLETOS.
                       - Se encontrar apenas um número, preencha apenas o campo correspondente e deixe o outro como null.
                       - Se encontrar números incompletos não salve-os, é preferível que traga null do que número incompleto preste muita atenção nisso para não errar.
                       - Repito se encontrar números incompletos não salve-os, é preferível que traga null do que número incompleto preste muita atenção nisso para não errar.

                    3. **Foco dos E-mails:**
                       - "E-mail A1" e "E-mail A2": Siga a ordem de prioridade: pessoal > profissional > contato da empresa.
                       - Se encontrar apenas um e-mail, preencha apenas o campo correspondente e deixe o outro como null.

                    4. **Complemento:**
                       - Busque informações sobre a referência do local (ex: sala, andar, bloco, etc.)

                    5. **Formato da Resposta:** A resposta DEVE SER APENAS o objeto JSON. Não inclua nenhuma introdução, explicação, observação ou qualquer texto fora do JSON.

                    6. **Campos Não Encontrados:** Se uma informação específica não for encontrada, o valor para essa chave no JSON deve ser `null`. Não invente dados.

                    **Exemplo de Saída Esperada (APENAS O JSON):**

                    {{
                    "Complemento": "Sala 405",
                    "Telefone A1": "(11) 3333-4444",
                    "Telefone A2": "(11) 4444-5555",
                    "Celular A1": "(11) 99999-8888",
                    "Celular A2": "(11) 99999-7777",
                    "E-mail A1": "carlos.nishio@email.com",
                    "E-mail A2": "contato@clinicacarlos.com.br"
                    }}

                    Sua Tarefa:
                    Para o médico com CRM: [CRM_MEDICO={crm_medico}], Nome: [NOME_MEDICO={nome_medico}], Sobrenome: [SOBRENOME_MEDICO={sobrenome_medico}], realize a busca e retorne o JSON apenas com os campos solicitados acima.
                    """)
                ],
            ),
        ]
        tools = [
            types.Tool(google_search=types.GoogleSearch()),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=0,
            tools=tools,
            response_mime_type="text/plain",
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")
            
        # Fim da contagem de tempo
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        print(f"\n\nTempo total de execução: {tempo_total:.2f} segundos")
        
    except Exception as e:
        print(f"Erro ao gerar conteúdo: {e}")
        # Mesmo em caso de erro, mostra o tempo decorrido
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        print(f"\nTempo decorrido até o erro: {tempo_total:.2f} segundos")

if __name__ == "__main__":
    generate()
