
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
    query = "select * from ruby.funcionarios;"  # Substitua 'sua_tabela' pelo nome da sua tabela
    df = pd.read_sql(query, engine)
    print(df.columns.tolist())
    print(df)
    df.to_csv("funcionarios.csv", index=False, sep=";")
    return df


def connect_intra_logins():
    """Conecta ao banco de dados PostgreSQL e retorna um DataFrame."""
    # Cria a engine de conexão
    engine = create_engine(DATABASE_URL)
    
    # Exemplo de consulta
    query = "select * from intra.op_logins;"  # Substitua 'sua_tabela' pelo nome da sua tabela
    df = pd.read_sql(query, engine)
    #print(df.columns.tolist())
    return df



def get_telfone(user_name):
    query = f"select telefone from intra.logins where user_name = '{user_name}';"
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(query, engine)
    if df.empty:
        return None 
    return df.telefone.tolist()[0]






if __name__ == "__main__":
    connect_intra_logins()
    print("This is the main module")