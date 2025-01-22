from flask import Flask, redirect, url_for, session, request, jsonify
import msal
import requests
import jwt
from db_helper import get_usuario_by_id, get_telfone

# Configurações do Azure AD
CLIENT_ID = "4ca15e42-c2a0-41df-81cd-58f485551533"
CLIENT_SECRET = "e5a8Q~aSOX6woFojIuDCFR6ukR3aSvS6Iah31dfo"
TENANT_ID = "1d390b0e-fddf-40eb-9c71-9aaab4f5c8d1"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read", "Group.Read.All", "User.ReadBasic.All", "User.Read.All"]
REDIRECT_URI = "https://sso.grupotapajos.com.br/callback"



# Inicializa o aplicativo Flask
app = Flask(__name__)
app.secret_key = "#@sua_chave_secreta###"  # Substitua por uma chave secreta segura

# Função para criar uma instância do cliente MSAL
def get_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

# Rota inicial para iniciar o processo de login
@app.route('/')
def home():
    return '<a href="/login">Login com Microsoft</a>'

# Rota para iniciar o login
@app.route('/login')
def login():
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return redirect(auth_url)




def get_payload_jwt(access_token):

    #try:
    
        headers = {"Authorization": f"Bearer {access_token}"}
        # Obtém informações do usuário
        user_info_response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        user_info = user_info_response.json()

        # Obtém grupos do usuário
        groups_response = requests.get("https://graph.microsoft.com/v1.0/me/memberOf", headers=headers)
        groups_info = groups_response.json()

        # Obtém a URL da foto de perfil do usuário
        photo_response = requests.get("https://graph.microsoft.com/v1.0/me/photo/$value", headers=headers)
        if photo_response.status_code == 200:
            # A URL da foto de perfil (sendo mais realista para um sistema local/real seria salvar a foto e gerar um link)
            photo_url = f"https://graph.microsoft.com/v1.0/me/photo/$value"
        else:
            photo_url = "Sem foto de perfil disponível"

        # Simplificando o JSON para retornar apenas as informações necessárias
        
        print(user_info)
        email = user_info.get('userPrincipalName')
        username, domain = email.split('@')
        
        funcionario = get_usuario_by_id(username)
        
        if not funcionario:
            cpf = None
        else:
            cpf = funcionario[0].get('cpf', None)
            
        profile_info = {
            "nome": user_info.get('displayName'),
            "email": email,
            "username": username,
            "cpf": cpf,
            "grupos": [group["displayName"] for group in groups_info.get("value", [])],
            "foto_perfil_url": photo_url,
            "ad_token": access_token
        }
        
        token = jwt.encode(profile_info, app.secret_key, algorithm="HS256")
        return token
    #except:
    #    return None
    




# Rota de callback para processar a resposta de autenticação
@app.route('/callback')
def callback():
    msal_app = get_msal_app()
    code = request.args.get('code')
    
    # Solicita um token usando o código de autorização
    result = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)

    if "access_token" in result:
        token = get_payload_jwt(result['access_token'])
        external_url = f"http://10.2.10.17:2002/{token}"
        return redirect(external_url)
    else:
        return jsonify(result), 400


def valid_token(token):

    try:
        decoded = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
        


@app.route('/cadastrar_cpf', methods=['POST'])
def protected():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token ausente ou inválido"}), 401
    
    data = request.get_json()
    cpf = data.get('cpf')
    
    try:
        decoded = valid_token(auth_header.split(" ")[1])
        user_dados = insert_funcionario(cpf)
        if not user_dados:
            return jsonify({"error": "Erro ao cadastrar o CPF."}), 401
        return jsonify(user_dados), 200
        
    except:
        return jsonify({"error": "Token ausente ou inválido"}), 401


@app.route('/gerar_assinatura', methods=['POST'])
def assinatura():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token ausente ou inválido"}), 401
    
    try:
        decoded = valid_token(auth_header.split(" ")[1])
        user_name = decoded.get('username')
        telefone = get_telfone(user_name)
        tokens = gerenciar_token(user_name, token)
        enviar_mensagem(telefone, tokens)
        
        return jsonify({"token": tokens}), 200
        
    except:
        return jsonify({"error": "Token ausente ou inválido"}), 401




@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    headers = {"Authorization": f"Bearer {access_token}"}

    # Obtém informações do usuário
    user_info_response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    user_info = user_info_response.json()

    # Obtém grupos do usuário
    groups_response = requests.get("https://graph.microsoft.com/v1.0/me/memberOf", headers=headers)
    groups_info = groups_response.json()

    # Obtém a URL da foto de perfil do usuário
    photo_response = requests.get("https://graph.microsoft.com/v1.0/me/photo/$value", headers=headers)
    if photo_response.status_code == 200:
        # A URL da foto de perfil (sendo mais realista para um sistema local/real seria salvar a foto e gerar um link)
        photo_url = f"https://graph.microsoft.com/v1.0/me/photo/$value"
    else:
        photo_url = "Sem foto de perfil disponível"

    # Simplificando o JSON para retornar apenas as informações necessárias
    email = user_info.get('userPrincipalName')
    username, domain = email.split('@')
    profile_info = {
        "nome": user_info.get('displayName'),
        "email": email,
        "username": username,
        "grupos": [group["displayName"] for group in groups_info.get("value", [])],
        "foto_perfil_url": photo_url
    }

    return jsonify(profile_info)

# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
# Rodando o aplicativo



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
