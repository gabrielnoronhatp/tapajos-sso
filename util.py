import random
import json
import requests
import tempfile
import time
import os
import dotenv
dotenv.load_dotenv()




def gerar_token():
    numero_aleatorio = f"{random.randint(0, 999999):06d}"
    token = f"{numero_aleatorio[:3]}-{numero_aleatorio[3:]}"
    return token

def enviar_mensagem(telefone, token):
    jay_parsed_ary = {
        "from": "559292242323",
        "to": telefone,
        "contents": [
            {
                "type": "template",
                "templateId": "e75df7ee-6429-4d41-a249-1648afd73333",
                "fields": {
                    "token": token
                }
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-TOKEN": os.getenv("WHATSAPP_TOKEN")
    }
    
    url = 'https://api.zenvia.com/v2/channels/whatsapp/messages'
    
    response = requests.post(url, headers=headers, data=json.dumps(jay_parsed_ary))
    
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")






def gerenciar_token(nome_usuario, token):
    # Criar um arquivo temporário com o nome do usuário
    temp_file_path = tempfile.gettempdir() + f'/{nome_usuario}_token.txt'
    
    # Verificar se o arquivo já existe
    if os.path.exists(temp_file_path):
        # Obter o timestamp da criação do arquivo
        token_gerado_time = os.path.getctime(temp_file_path)
        
        # Verificar se o token tem menos de 6 minutos
        tempo_expiracao = 5 * 60  # 6 minutos em segundos
        if time.time() - token_gerado_time > tempo_expiracao:
            # Gerar um novo token
            token = gerar_token()
            # Atualizar o arquivo com o novo token
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write(token)
    else:
        # Se o arquivo não existir, criar e escrever o token
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(token)

    # Ler o token do arquivo e retorná-lo
    with open(temp_file_path, 'r') as temp_file:
        return temp_file.read().strip()



if __name__ == "__main__":
    # Exemplos de uso
    token = gerar_token()
#    enviar_mensagem("5592985021028", token)
    tokens = gerenciar_token('william.monteiro', token)
    enviar_mensagem("5592985021028", tokens)
    
    
    #enviar_mensagem("5592991805721", token)
