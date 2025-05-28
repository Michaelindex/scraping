import base64
import os
from google import genai
from google.genai import types


def generate():
    # Lê a chave da API do arquivo
    with open("api.key", "r") as f:
        api_key = f.read().strip()

    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""

                Atue como um assistente de extração de dados médicos. Sua tarefa é encontrar informações sobre o médico com o CRM "2875" NOME "CARLOS" e SOBRENOME "EDUARDO RYUJI NISHIO" e retornar estritamente um objeto JSON contendo os seguintes campos: "Especialidade Médica", "Endereco Completo", "Logradouro", "Numero", "Complemento", "Bairro", "CEP", "Cidade", "Estado", "Telefone A1", "Telefone A2", "Celular A1", "Celular A2", "E-mail A1", "E-mail A2".

                **Instruções Cruciais:**

                1.  **Fonte Primária:** Utilize os dados "[CRM_MEDICO=2875]", "[NOME_MEDICO=CARLOS]" e "[SOBRENOME_MEDICO=EDUARDO RYUJI NISHIO]" para realizar a busca no Google.
                2.  **Foco do Endereço:** As informações de "Endereco Completo", "Logradouro", "Numero", "Complemento", "Bairro", "CEP", "Cidade" e "Estado" devem ser do **local de atendimento/trabalho principal** do médico.
                3.  **Foco dos Telefones:**
                    * "Telefone A1" e "Telefone A2": Devem ser, prioritariamente, números de telefone fixo do **local de trabalho** do médico. Se encontrar mais de um, preencha ambos. Se encontrar apenas um, deixe o "Telefone A2" como `null`.
                    * "Celular A1" e "Celular A2": Devem ser, prioritariamente, números de celular **pessoais ou profissionais diretos** do médico. Se encontrar mais de um, preencha ambos. Se encontrar apenas um, deixe o "Celular A2" como `null`.
                4.  **Foco dos E-mails:**
                    * "E-mail A1" e "E-mail A2": Podem ser o e-mail **profissional, pessoal do médico ou do local de trabalho**. Se encontrar mais de um, preencha ambos. Se encontrar apenas um, deixe o "E-mail A2" como `null`.
                5.  **Mínimo Requerido:** É essencial encontrar pelo menos uma informação válida para "Telefone A1" (ou "Telefone A2"), "Celular A1" (ou "Celular A2"), e "E-mail A1" (ou "E-mail A2"). Se alguma dessas categorias não for encontrada, retorne `null` para os respectivos campos.
                6.  **Formato da Resposta:** A resposta DEVE SER APENAS o objeto JSON. Não inclua nenhuma introdução, explicação, observação ou qualquer texto fora do JSON.
                7.  **Campos Não Encontrados:** Se uma informação específica para um campo não for encontrada após a busca, o valor para essa chave no JSON deve ser `null`. Não invente dados.
                8.  **Precisão:** Priorize informações de fontes confiáveis (ex: conselhos de medicina, sites de clínicas, plataformas de agendamento médico).

                **Exemplo de Entrada (Substitua com os dados reais):**

                * CRM_MEDICO: "123456SP"
                * NOME_MEDICO: "João"
                * SOBRENOME_MEDICO: "Silva"

                **Exemplo de Saída Esperada (APENAS O JSON):**

                ```json
                {
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
                }
                Sua Tarefa:
                Para o médico com CRM: [CRM_MEDICO=2875], Nome: [NOME_MEDICO=CARLOS], Sobrenome: [SOBRENOME_MEDICO=EDUARDO RYUJI NISHIO], realize a busca e retorne o JSON conforme especificado.

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

if __name__ == "__main__":
    generate()
