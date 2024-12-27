# Use a imagem base do Python
FROM python:3.9

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos necessários para o diretório de trabalho
COPY . .

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Expõe a porta que a aplicação Flask irá usar
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["flask", "run", "--host=0.0.0.0"]