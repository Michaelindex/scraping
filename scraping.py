import base64
import os
import time
import pandas as pd
import json
import csv
from google import genai
from google.genai import types

def limpar_resposta_json(resposta):
    # Remove a marcação ```json do início e fim
    resposta = resposta.replace('```json', '').replace('```', '')
    # Remove espaços em branco no início e fim
    resposta = resposta.strip()
    return resposta

def generate(medico_data):
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
                    CRM_MEDICO: {medico_data['CRM']}
                    NOME_MEDICO: {medico_data['Nome']}
                    SOBRENOME_MEDICO: {medico_data['Sobrenome']}

                    Atue como um assistente de extração de dados médicos. Sua tarefa é encontrar informações sobre o médico com [CRM_MEDICO={medico_data['CRM']}], [NOME_MEDICO={medico_data['Nome']}] [SOBRENOME_MEDICO={medico_data['Sobrenome']}] e retornar estritamente um objeto JSON contendo os seguintes campos: "Especialidade Médica", "Endereco Completo", "Logradouro", "Numero", "Complemento", "Bairro", "CEP", "Cidade", "Estado", "Telefone A1", "Telefone A2", "Celular A1", "Celular A2", "E-mail A1", "E-mail A2".

                    **Instruções Cruciais:**

                    1.  **Fonte Primária:** Utilize os dados "[CRM_MEDICO={medico_data['CRM']}]", "[NOME_MEDICO={medico_data['Nome']}]" e "[SOBRENOME_MEDICO={medico_data['Sobrenome']}]" para realizar a busca no Google.
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
                    Para o médico com CRM: [CRM_MEDICO={medico_data['CRM']}], Nome: [NOME_MEDICO={medico_data['Nome']}], Sobrenome: [SOBRENOME_MEDICO={medico_data['Sobrenome']}], realize a busca e retorne o JSON conforme especificado.
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

        response_text = ""
        print("\nAguardando resposta da IA...")
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
            print(chunk.text, end="")
            
        # Fim da contagem de tempo
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        print(f"\nTempo total de execução: {tempo_total:.2f} segundos")
        
        # Tenta converter a resposta em JSON
        try:
            print("\nTentando converter resposta em JSON...")
            # Limpa a resposta antes de converter para JSON
            response_text = limpar_resposta_json(response_text)
            print("Resposta limpa:", response_text)
            response_json = json.loads(response_text)
            print("JSON convertido com sucesso!")
            return response_json
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            print("Resposta recebida:", response_text)
            return None
        
    except Exception as e:
        print(f"Erro ao gerar conteúdo: {e}")
        # Mesmo em caso de erro, mostra o tempo decorrido
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        print(f"\nTempo decorrido até o erro: {tempo_total:.2f} segundos")
        return None

def main():
    # Lê o arquivo CSV de entrada
    try:
        print("Lendo arquivo input.csv...")
        df_input = pd.read_csv('input.csv')
        print(f"Arquivo lido com sucesso! {len(df_input)} registros encontrados.")
    except Exception as e:
        print(f"Erro ao ler o arquivo input.csv: {e}")
        return

    # Lista para armazenar os resultados
    resultados = []

    # Processa cada linha do CSV
    for index, row in df_input.iterrows():
        print(f"\n{'='*50}")
        print(f"Processando médico {index + 1} de {len(df_input)}")
        print(f"CRM: {row['CRM']}, Nome: {row['Nome']} {row['Sobrenome']}")
        print(f"{'='*50}")
        
        # Cria um dicionário com os dados do médico
        medico_data = {
            'CRM': row['CRM'],
            'Nome': row['Nome'],
            'Sobrenome': row['Sobrenome']
        }
        
        # Gera os dados usando a IA
        resultado = generate(medico_data)
        
        if resultado:
            print("\nDados encontrados pela IA:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            
            # Combina os dados originais com os novos dados
            dados_combinados = row.to_dict()
            dados_combinados.update(resultado)
            
            print("\nDados combinados:")
            print(json.dumps(dados_combinados, indent=2, ensure_ascii=False))
            
            resultados.append(dados_combinados)
        else:
            print("\nNenhum dado encontrado pela IA. Mantendo dados originais.")
            resultados.append(row.to_dict())

    # Cria o DataFrame de saída
    df_output = pd.DataFrame(resultados)
    
    # Mostra o DataFrame antes de salvar
    print("\nDataFrame final antes de salvar:")
    print(df_output)
    
    # Salva o resultado em um novo CSV
    try:
        print("\nSalvando resultados em output.csv...")
        df_output.to_csv('output.csv', index=False, quoting=csv.QUOTE_ALL)
        print("Arquivo output.csv gerado com sucesso!")
        
        # Verifica se o arquivo foi criado e lê seu conteúdo
        if os.path.exists('output.csv'):
            print("\nVerificando conteúdo do arquivo output.csv:")
            df_verificacao = pd.read_csv('output.csv')
            print(df_verificacao)
        else:
            print("ERRO: Arquivo output.csv não foi criado!")
            
    except Exception as e:
        print(f"Erro ao salvar o arquivo output.csv: {e}")

if __name__ == "__main__":
    main()
