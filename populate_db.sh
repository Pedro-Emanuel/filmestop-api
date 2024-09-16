#!/bin/bash

# Verifica se o jq está instalado
if ! command -v jq &> /dev/null
then
    echo "jq não está instalado. Por favor, instale-o primeiro."
    echo "No Ubuntu/Debian: sudo apt-get install jq"
    echo "No macOS com Homebrew: brew install jq"
    exit 1
fi

# URL base da API
API_URL="http://127.0.0.1:5001"

# Cria um administrador e guarda o admin_token retornado
echo "Criando administrador..."
curl -s -X POST "${API_URL}/create_admin" \
     -H "Content-Type: application/json" \
     -d '{"name": "Admin", "email": "admin@mail.com"}' > admin_token.json

# Verifica se a criação do admin foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "Erro ao criar administrador. Verifique se a API está rodando."
    exit 1
fi

# Extrai o admin_token do arquivo JSON
admin_token=$(jq -r '.admin_token' admin_token.json)

if [ -z "$admin_token" ]; then
    echo "Erro: admin_token não encontrado na resposta."
    exit 1
fi

echo "Admin criado com sucesso. Token: $admin_token"

# Popula o banco de dados com os dados de exemplo
echo "Populando o banco de dados..."
populate_response=$(curl -s -X POST "${API_URL}/populate_database" \
     -H "Authorization: $admin_token")

# Verifica se a população do banco de dados foi bem-sucedida
if echo "$populate_response" | jq -e '.message' &> /dev/null; then
    echo "Banco de dados populado com sucesso."
else
    echo "Erro ao popular o banco de dados. Resposta:"
    echo "$populate_response"
    exit 1
fi

# Remove o arquivo temporário
rm admin_token.json

echo "Processo concluído."