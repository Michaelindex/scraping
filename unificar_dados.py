import pandas as pd
import numpy as np

def limpar_valor(valor):
    if pd.isna(valor) or valor == '' or valor == 'nan' or valor == 'None':
        return None
    return str(valor).strip()

def preencher_campos_vazios(df_base, df_local, df_base_simple):
    # Criar uma cópia do DataFrame base
    df_resultado = df_base.copy()
    
    # Mapeamento de colunas entre output.csv e outputlocal.csv
    mapeamento_local = {
        'Nome': 'Firstname',
        'Sobrenome': 'LastName',
        'Especialidade Médica': 'Medical specialty',
        'Endereco Completo': 'Endereco Completo A1',
        'Logradouro': 'Address A1',
        'Numero': 'Numero A1',
        'Complemento': 'Complement A1',
        'Bairro': 'Bairro A1',
        'CEP': 'postal code A1',
        'Cidade': 'City A1',
        'Estado': 'State A1',
        'Telefone A1': 'Phone A1',
        'Telefone A2': 'Phone A2',
        'Celular A1': 'Cell phone A1',
        'Celular A2': 'Cell phone A2',
        'E-mail A1': 'E-mail A1',
        'E-mail A2': 'E-mail A2'
    }
    
    # Mapeamento de colunas entre output.csv e outputbase.csv
    mapeamento_base = {
        'Especialidade Médica': 'Especialidade Médica',
        'Telefone A1': 'Telefone A1',
        'E-mail A1': 'E-mail A1'
    }
    
    # Para cada linha no DataFrame base
    for idx, row in df_resultado.iterrows():
        crm = str(row['CRM'])
        
        # Buscar no outputlocal.csv
        if crm in df_local['CRM'].astype(str).values:
            linha_local = df_local[df_local['CRM'].astype(str) == crm].iloc[0]
            
            # Preencher campos vazios com dados do outputlocal.csv
            for col_base, col_local in mapeamento_local.items():
                if pd.isna(row[col_base]) or row[col_base] == '':
                    valor_local = limpar_valor(linha_local[col_local])
                    if valor_local:
                        df_resultado.at[idx, col_base] = valor_local
        
        # Buscar no outputbase.csv
        if crm in df_base_simple['CRM'].astype(str).values:
            linha_base = df_base_simple[df_base_simple['CRM'].astype(str) == crm].iloc[0]
            
            # Preencher campos vazios com dados do outputbase.csv
            for col_base, col_simple in mapeamento_base.items():
                if pd.isna(row[col_base]) or row[col_base] == '':
                    valor_simple = limpar_valor(linha_base[col_simple])
                    if valor_simple:
                        df_resultado.at[idx, col_base] = valor_simple
    
    return df_resultado

def main():
    try:
        # Ler os arquivos CSV
        print("Lendo arquivos CSV...")
        df_output = pd.read_csv('output.csv')
        df_local = pd.read_csv('outputlocal.csv')
        df_base = pd.read_csv('outputbase.csv')
        
        print("Unificando dados...")
        # Unificar os dados
        df_resultado = preencher_campos_vazios(df_output, df_local, df_base)
        
        # Salvar o resultado
        print("Salvando resultado em output_unificado.csv...")
        df_resultado.to_csv('output_unificado.csv', index=False)
        
        print("Processo concluído com sucesso!")
        
        # Mostrar estatísticas
        total_campos = len(df_resultado) * len(df_resultado.columns)
        campos_preenchidos = df_resultado.count().sum()
        print(f"\nEstatísticas:")
        print(f"Total de registros: {len(df_resultado)}")
        print(f"Total de campos: {total_campos}")
        print(f"Campos preenchidos: {campos_preenchidos}")
        print(f"Campos vazios: {total_campos - campos_preenchidos}")
        
    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")

if __name__ == "__main__":
    main() 