import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    raise Exception("GOOGLE_API_KEY missing in .env")

genai.configure(api_key=api_key)

MODEL_NAME = "models/gemini-flash-latest"  # escolha da lista

model = genai.GenerativeModel(model_name=MODEL_NAME)

def gerar_texto(prompt):
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    texto = "Explique a teoria da relatividade de forma simples."
    resultado = gerar_texto(texto)
    print(resultado)
