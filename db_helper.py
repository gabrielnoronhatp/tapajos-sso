
# db_helper.py

from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
# Carregar variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")  # Certifique-se de que essa variável está definida no seu .env

def connect_to_db():
    """Conecta ao banco de dados PostgreSQL e retorna um DataFrame."""
    # Cria a engine de conexão
    engine = create_engine(DATABASE_URL)
    
    # Exemplo de consulta
    query = "SELECT * FROM sua_tabela;"  # Substitua 'sua_tabela' pelo nome da sua tabela
    df = pd.read_sql(query, engine)
    
    return df













if __name__ == "__main__":
    print("This is the main module")