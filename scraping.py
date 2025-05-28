import base64
import os
import time
from google import genai
from google.genai import types

# Variáveis do médico
crm_medico = "2875"
nome_medico = "CARLOS"
sobrenome_medico = "EDUARDO RYUJI NISHIO"

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
                    CRM_MEDICO: {crm_medico}
                    NOME_MEDICO: {nome_medico}
                    SOBRENOME_MEDICO: {sobrenome_medico}

                    Atue como um assistente de extração de dados médicos. Sua tarefa é encontrar informações sobre o médico com [CRM_MEDICO={crm_medico}], [NOME_MEDICO={nome_medico}] [SOBRENOME_MEDICO={sobrenome_medico}] e retornar estritamente um objeto JSON contendo os seguintes campos: "Especialidade Médica", "Endereco Completo", "Logradouro", "Numero", "Complemento", "Bairro", "CEP", "Cidade", "Estado", "Telefone A1", "Telefone A2", "Celular A1", "Celular A2", "E-mail A1", "E-mail A2".

                    **Instruções Cruciais:**

                    1.  **Fonte Primária:** Utilize os dados "[CRM_MEDICO={crm_medico}]", "[NOME_MEDICO={nome_medico}]" e "[SOBRENOME_MEDICO={sobrenome_medico}]" para realizar a busca no Google.
                    2.  **Foco do Endereço:** 
                        - As informações de "Endereco Completo", "Logradouro", "Numero", "Complemento", "Bairro", "CEP", "Cidade" e "Estado" devem ser do **local de atendimento/trabalho principal** do médico.
                        - O CEP DEVE ser extraído do endereço completo. Se o endereço completo estiver disponível, o CEP NÃO pode ser null.
                        - Use o endereço completo para inferir o CEP correto do local.
                    3.  **Foco dos Telefones:**
                        - "Telefone A1" e "Telefone A2": Devem ser números de telefone fixo COMPLETOS do **local de trabalho** do médico. NÃO aceite números truncados ou parciais.
                        - "Celular A1" e "Celular A2": Devem ser números de celular COMPLETOS **pessoais ou profissionais diretos** do médico. NÃO aceite números truncados ou parciais.
                        - Se encontrar apenas um número, preencha apenas o campo correspondente e deixe o outro como null.
                        - Se encontrar números imcompletos não salve-os, é preferível que traga null do que número incompleto.
                    4.  **Foco dos E-mails:**
                        - "E-mail A1" e "E-mail A2": Podem ser o e-mail **profissional, pessoal do médico ou do local de trabalho**.
                        - Se encontrar apenas um e-mail, preencha apenas o campo correspondente e deixe o outro como null.
                    5.  **Mínimo Requerido:** É essencial encontrar pelo menos uma informação válida para "Telefone A1" (ou "Telefone A2"), "Celular A1" (ou "Celular A2"), e "E-mail A1" (ou "E-mail A2"). Se alguma dessas categorias não for encontrada, retorne `null` para os respectivos campos.
                    6.  **Formato da Resposta:** A resposta DEVE SER APENAS o objeto JSON. Não inclua nenhuma introdução, explicação, observação ou qualquer texto fora do JSON.
                    7.  **Campos Não Encontrados:** Se uma informação específica para um campo não for encontrada após a busca, o valor para essa chave no JSON deve ser `null`. Não invente dados.
                    8.  **Precisão:** 
                        - Priorize informações de fontes confiáveis (ex: conselhos de medicina, sites de clínicas, plataformas de agendamento médico).
                        - NUNCA retorne números de telefone truncados ou parciais.
                        - SEMPRE extraia o CEP do endereço completo quando disponível.

                    **Exemplo de Saída Esperada (APENAS O JSON):**

                    {{
                    "Especialidade Médica": "Cardiologia",
                    "Endereco Completo": "Rua das Palmeiras, 123, Sala 405, Centro, São Paulo, SP, 01000-000",
                    "Logradouro": "Rua das Palmeiras",
                    "Numero": "123",
                    "Complemento": "Sala 405",
                    "Bairro": "Centro",
                    "CEP": "01000-000",
                    "Cidade": "São Paulo",
                    "Estado": "SP",
                    "Telefone A1": "(11) 3333-4444",
                    "Telefone A2": null,
                    "Celular A1": "(11) 99999-8888",
                    "Celular A2": null,
                    "E-mail A1": "joao.silva.cardiologia@email.com",
                    "E-mail A2": "contato@clinicajoaosilva.com.br"
                    }}

                    Sua Tarefa:
                    Para o médico com CRM: [CRM_MEDICO={crm_medico}], Nome: [NOME_MEDICO={nome_medico}], Sobrenome: [SOBRENOME_MEDICO={sobrenome_medico}], realize a busca e retorne o JSON conforme especificado.
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
