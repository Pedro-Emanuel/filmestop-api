# Usar uma imagem base do Python
FROM python:3.11-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos do projeto para o diretório de trabalho
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta em que a aplicação vai rodar
EXPOSE 5001

# Definir o comando para rodar a aplicação
CMD ["python", "run.py"]
