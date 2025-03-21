import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega a chave da API do arquivo .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lê o conteúdo do arquivo de texto
with open("texto.txt", "r", encoding="utf-8") as file:
    conteudo = file.read()

# Envia o conteúdo para a API da OpenAI com instrução para resumir
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Você é um assistente que resume textos de forma clara e objetiva."},
        {"role": "user", "content": f"Resuma o seguinte texto:\n\n{conteudo}"}
    ],
    temperature=0.5
)

# Exibe o resumo
resumo = response.choices[0].message.content
print("\nResumo gerado:\n")
print(resumo)
