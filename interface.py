import customtkinter as ctk
import webbrowser
import os
from dotenv import load_dotenv
from openai import OpenAI
from gmail_helper import autenticar_gmail, buscar_emails
import threading
import time

# Inicialização visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Carrega chave da OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Variáveis globais
email_data = {}
auto_update_interval = 0
auto_update_flag = True
current_font_size = 14

# Gera o resumo com IA
def resumir_com_ia(texto_original):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que resume e-mails de forma objetiva."},
                {"role": "user", "content": f"Resuma o seguinte e-mail:\n\n{texto_original}"}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Erro ao resumir com IA: {e}]"

def carregar_emails():
    status_label.configure(text="🔄 Carregando e-mails...")
    app.update_idletasks()

    try:
        service = autenticar_gmail()
        emails = buscar_emails(service, quantidade=5)

        lista_emails.configure(values=[f"{e['assunto']} ({e['remetente']})" for e in emails])
        for i, e in enumerate(emails):
            email_data[i] = e

        lista_emails.set("🔽 Clique para selecionar um e-mail")
        status_label.configure(text=f"{len(emails)} e-mails carregados")
    except Exception as e:
        status_label.configure(text=f"Erro: {e}")

def ao_selecionar(event=None):
    valor = lista_emails.get()
    if not valor or "Clique para" in valor:
        return

    index = -1
    for i, email in email_data.items():
        item_str = f"{email['assunto']} ({email['remetente']})"
        if item_str == valor:
            index = i
            break

    if index == -1:
        resumo_textbox.delete("0.0", "end")
        resumo_textbox.insert("0.0", "Erro: e-mail não encontrado.")
        return

    dados = email_data[index]
    resumo_textbox.delete("0.0", "end")
    resumo_textbox.insert("0.0", "Resumindo...")
    app.update_idletasks()

    resumo = resumir_com_ia(dados['corpo'])
    resumo_textbox.delete("0.0", "end")
    resumo_textbox.insert("0.0", resumo)

    abrir_btn.configure(command=lambda: webbrowser.open(dados['link']))

def mudar_fonte(opcao):
    global current_font_size
    tamanho = {"Pequena": 12, "Média": 14, "Grande": 18}
    current_font_size = tamanho.get(opcao, 14)
    resumo_textbox.configure(font=("Arial", current_font_size))

def mudar_intervalo(opcao):
    global auto_update_interval
    minutos = {"Desativado": 0, "5 min": 300, "10 min": 600, "30 min": 1800}
    auto_update_interval = minutos.get(opcao, 0)

def auto_atualizar():
    global auto_update_flag
    while auto_update_flag:
        if auto_update_interval > 0:
            time.sleep(auto_update_interval)
            carregar_emails()
        else:
            time.sleep(5)

def fechar():
    global auto_update_flag
    auto_update_flag = False
    app.destroy()

# Criação da janela principal
app = ctk.CTk()
app.title("📬 Agente Resumidor de E-mails")
app.geometry("820x680+1000+100")
app.resizable(True, True)
app.attributes("-topmost", True)

# ==== Barra superior ====
top_bar = ctk.CTkFrame(app)
top_bar.pack(pady=10, padx=10, fill="x")

# ComboBox de e-mails
lista_emails = ctk.CTkComboBox(top_bar, values=[], width=320, command=ao_selecionar)
lista_emails.set("🔽 Clique para selecionar um e-mail")
lista_emails.grid(row=0, column=0, padx=5)

# Botão atualizar
carregar_btn = ctk.CTkButton(top_bar, text="🔄 Atualizar Agora", command=carregar_emails)
carregar_btn.grid(row=0, column=1, padx=5)

# Fonte
fonte_label = ctk.CTkLabel(top_bar, text="Fonte:")
fonte_label.grid(row=0, column=2, padx=(20, 5))

fonte_combo = ctk.CTkComboBox(top_bar, values=["Pequena", "Média", "Grande"], command=mudar_fonte, width=100)
fonte_combo.set("Média")
fonte_combo.grid(row=0, column=3, padx=5)

# Intervalo de auto-atualização
intervalo_label = ctk.CTkLabel(top_bar, text="Auto:")
intervalo_label.grid(row=0, column=4, padx=(20, 5))

intervalo_combo = ctk.CTkComboBox(top_bar, values=["Desativado", "5 min", "10 min", "30 min"], command=mudar_intervalo, width=100)
intervalo_combo.set("Desativado")
intervalo_combo.grid(row=0, column=5, padx=5)

# Botão de fechar
fechar_btn = ctk.CTkButton(top_bar, text="❌", width=40, command=fechar)
fechar_btn.grid(row=0, column=6, padx=(20, 0))

# ==== Resumo e corpo ====
resumo_textbox = ctk.CTkTextbox(app, width=780, height=420, wrap="word", font=("Arial", current_font_size))
resumo_textbox.pack(padx=10, pady=10)

abrir_btn = ctk.CTkButton(app, text="📨 Abrir no Gmail", command=lambda: None)
abrir_btn.pack(pady=5)

status_label = ctk.CTkLabel(app, text="Clique em 'Atualizar Agora' ou configure auto-atualização")
status_label.pack(pady=5)

# Inicia a thread de autoatualização
thread_auto = threading.Thread(target=auto_atualizar, daemon=True)
thread_auto.start()

# Inicia o app
app.mainloop()
