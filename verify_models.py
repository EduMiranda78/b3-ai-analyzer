# verify_models.py
# Objetivo: listar modelos disponíveis na API do Google que suportam generateContent

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
print("Carregando chave de API...")
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

# Verifica se a chave existe
if not api_key:
    print("ERRO: GOOGLE_API_KEY não encontrada no arquivo .env")
    print("Verifique se você criou o arquivo .env e adicionou a linha:")
    print("GOOGLE_API_KEY=suachaveaqui")
    exit()

try:
    # Inicializa a configuração da API
    genai.configure(api_key=api_key)
    print("\nConexão estabelecida com a API do Google.\n")

    print("Modelos disponíveis que suportam generateContent:\n")

    modelos_compativeis = []

    # Percorre todos os modelos fornecidos pela biblioteca
    for modelo in genai.list_models():
        # Alguns modelos não possuem todas as chaves, então tratamos com segurança
        generation_methods = getattr(modelo, "supported_generation_methods", [])

        # Filtra apenas modelos que suportam generateContent
        if "generateContent" in generation_methods:
            modelos_compativeis.append(modelo.name)

    # Exibe resultados
    if not modelos_compativeis:
        print("Nenhum modelo compatível encontrado.")
        print("Pode ser limitação da chave de API ou região configurada.")
    else:
        for nome in sorted(modelos_compativeis):
            print(nome)

    print("\n--- Fim da Lista ---\n")
    print(
        "Copie um dos nomes acima e utilize no seu arquivo 'ia/gemini_analyzer.py'."
    )

except Exception as erro:
    print("\nErro ao conectar com a API do Google:")
    print(erro)
