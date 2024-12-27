from flask import Flask, redirect, url_for, session, request, jsonify
import msal
import requests
from flask_cors import CORS


# Configurações do Azure AD
# ADICIONE CLIENT SC  E CLIENT ID DPS
TENANT_ID = "1d390b0e-fddf-40eb-9c71-9aaab4f5c8d1"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read", "GroupMember.Read.All"]  # Permissões necessárias
REDIRECT_URI = "https://sso.grupotapajos.com.br/callback"

# Inicializa o aplicativo Flask
app = Flask(__name__)
app.secret_key = "93f7fea8e407169184cf8cdc6e7f01e"  # Substitua por uma chave secreta segura
CORS(app)  # Isso vai permitir requisições de qualquer domínio

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

# Rota de callback para processar a resposta de autenticação
@app.route('/')
def callback():
    msal_app = get_msal_app()
    code = request.args.get('code')
    
    # Solicita um token usando o código de autorização
    result = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)

    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('profile'))
    else:
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
