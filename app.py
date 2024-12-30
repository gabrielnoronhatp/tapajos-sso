import os
import base64
import hashlib
import msal
import requests
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Azure AD
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = os.getenv("AUTHORITY")
SCOPE = ["User.Read", "GroupMember.Read.All"]  # Permissões necessárias
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Inicializa o aplicativo Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Usando a variável de ambiente
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)


# Função para criar uma instância do cliente MSAL
def get_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

# Função para gerar um code_verifier e code_challenge
def generate_code_challenge():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip("=")
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').rstrip("=")
    return code_verifier, code_challenge

# Rota inicial para iniciar o processo de login
@app.route('/')
def home():
    return '<a href="/login">Login com Microsoft</a>'

# Rota para iniciar o login
@app.route('/login')
def login():
    msal_app = get_msal_app()
    
    # Gerar o code_verifier e code_challenge
    code_verifier, code_challenge = generate_code_challenge()
    session['code_verifier'] = code_verifier  # Armazene o code_verifier na sessão
    
    # Obter o URL de autorização com o PKCE
    auth_url = msal_app.get_authorization_request_url(
        SCOPE, 
        redirect_uri=REDIRECT_URI,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )
    return redirect(auth_url)

# Rota de callback para processar a resposta de autenticação
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Código de autorização não encontrado.", 400
    
    code_verifier = session.pop('code_verifier', None)  # Recupere o code_verifier da sessão
    if not code_verifier:
        return "Code verifier not found.", 400
    
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code, 
        scopes=SCOPE, 
        redirect_uri=REDIRECT_URI,
        code_verifier=code_verifier
    )

    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('profile'))
    else:
        print("Erro ao obter token:", result)
        return jsonify(result), 400

# Rota para obter informações do usuário
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

    return jsonify({
        "user_info": user_info,
        "groups": groups_info.get("value", [])
    })

# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Rodando o aplicativo
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
