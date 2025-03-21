from gmail_helper import autenticar_gmail, buscar_emails

service = autenticar_gmail()
emails = buscar_emails(service)

for i, email in enumerate(emails, 1):
    print(f"\nEmail {i}:")
    print("Assunto:", email['assunto'])
    print("Remetente:", email['remetente'])
    print("Resumo do corpo:", email['corpo'][:300], "...")
    print("Link:", email['link'])
