
# db_helper.py

from itertools import count
from sqlalchemy import create_engine, text
import pandas as pd
import os, json
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()
# Carregar variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")  # Certifique-se de que essa variável está definida no seu .env



#['idempresa', 'idfilial', 'tipcol', 'matricula', 'nomefuncionario', 'apelidofuncionario', 'numerocpf', 'dataadmissao', 'tipoadmissao', 'idafastamento', 'descsituacao', 'idcargo', 'descargo', 'idescala', 'hordsr', 'horassemana', 'horasmes', 'idlocal', 'local_trabalho', 'genero', 'estadocivil', 'idgrauinstrucao', 'descgrauinstrucao', 'datanascimento', 'ddd', 'tel1', 'tel2', 'email1', 'email2', 'datadesligamento']

def get_funcionarios_ruby_por_cpf(cpf):
    engine = create_engine(DATABASE_URL)
    query = f"select * from ruby.funcionarios where numerocpf = '{cpf}';"
    df = pd.read_sql(query, engine)
    
    # Converte o DataFrame para JSON e depois para uma lista de dicionários
    df_json = json.loads(df.to_json(orient='records'))
    print(df_json)
    # Campos desejados
    fields_to_extract = [
        "matricula",
        "nomefuncionario",
        "apelidofuncionario",
        "idcargo",
        "descargo",
        "numerocpf",
        "local_trabalho",
        "ddd",
        "tel1",
        "datadesligamento",
    ]
    
    # Extrai apenas os campos necessários
    result = [{field: item[field] for field in fields_to_extract} for item in df_json]
    
    return result




def upsert_funcionario(dados):
    try:
        # Establishing the connection
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # SQL query
        query = sql.SQL("""
            INSERT INTO intra.logins (
                nome, nomecompleto, cpf, id_cargo, matricula, cargo, local, ddd, telefone, email, ativo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (cpf, nome) DO UPDATE SET
                nomecompleto = EXCLUDED.nomecompleto,
                id_cargo = EXCLUDED.id_cargo,
                matricula = EXCLUDED.matricula,
                cargo = EXCLUDED.cargo,
                local = EXCLUDED.local,
                ddd = EXCLUDED.ddd,
                telefone = EXCLUDED.telefone,
                email = EXCLUDED.email,
                ativo = EXCLUDED.ativo
        """)

        # Extracting values from the dados dictionary
        values = (
            dados['nome'],      
            dados['nomecompleto'], 
            dados['cpf'],
            dados['id_cargo'],        
            dados['matricula'],     
            dados['cargo'],
            dados['local'],
            dados['ddd'],
            dados['telefone'],
            dados['email'],
            dados['ativo']
        )

        # Executing the query with the extracted values
        cursor.execute(query, values)
        connection.commit()  # Commit the transaction
        print("Funcionário inserido ou atualizado com sucesso!")

    except Exception as e:
        print(f"Erro ao inserir ou atualizar funcionário: {e}")
    finally:
        # Closing the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()



# ['id', 'nome', 'sobrenome', 'cpf', 'id_cargo', 'password', 'cargo', 'local', 'telefone', 'email', 'ativo']
def connect_intra_logins():
    engine = create_engine(DATABASE_URL)
    query = "select * from intra.logins" 
    df = pd.read_sql(query, engine)
    print(df)
    return df

#intra.logins CRUD OP.

def get_usuario_by_id(nome):
    query = f"SELECT *  from intra.logins WHERE nome = '{nome}';"
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(query, engine)
    df_json = json.loads(df.to_json(orient='records'))
    return df_json




def get_telfone(user_name):
    query = f"select telefone from intra.logins where user_name = '{user_name}';"
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(query, engine)
    if df.empty:
        return None 
    return df.telefone.tolist()[0]



def insert_funcionario(cpf):
    try:
        rb =get_funcionarios_ruby_por_cpf(cpf)[0]

        telefone = str(rb.get('ddd')) + str(rb.get('tel1'))
        email = user_name +'@grupotapajos.com.br'
        ativo = True if rb.get('datadesligamento') is None else False
        dados_funcionario = {
        "nome": user_name,
        "nomecompleto": rb.get('nomefuncionario'),
        "cpf": str(rb.get('numerocpf')),
        "id_cargo": int(rb.get('idcargo')),
        "matricula": str(rb.get('matricula')),
        "cargo": rb.get('descargo'),
        "local": str(rb.get('local_trabalho')),
        "ddd": str(rb.get('ddd')),
        "telefone": telefone,
        "email": email,
        "ativo": ativo
        }
        upsert_funcionario(dados_funcionario)
        return dados_funcionario
    except Exception as e:
        return None
    




if __name__ == "__main__":

    connect_intra_logins()

    nome = 'william.monteiro'
    #nome = 'admin'
    funcionario = get_usuario_by_id(nome)
    if not funcionario:
        cpf = None
    else:
        cpf = funcionario[0].get('cpf', None)

    print(cpf)

    cpf = '74339524204'
    rb =get_funcionarios_ruby_por_cpf(cpf)[0]

    print(rb)

    telefone = str(rb.get('ddd')) + str(rb.get('tel1'))
    email = nome +'@grupotapajos.com.br'
    ativo = True if rb.get('datadesligamento') is None else False
    dados_funcionario = {
    "nome": nome,
    "nomecompleto": rb.get('nomefuncionario'),
    "cpf": str(rb.get('numerocpf')),
    "id_cargo": int(rb.get('idcargo')),
    "matricula": str(rb.get('matricula')),
    "cargo": rb.get('descargo'),
    "local": str(rb.get('local_trabalho')),
    "ddd": str(rb.get('ddd')),
    "telefone": telefone,
    "email": email,
    "ativo": ativo
    }

    print(dados_funcionario)
    upsert_funcionario(dados_funcionario)