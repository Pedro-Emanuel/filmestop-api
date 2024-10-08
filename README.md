# FilmesTop API

![FilmesTop Logo](logo.png)

## Índice

- [Descrição](#descrição)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso da API](#uso-da-api)
- [Desenvolvimento](#desenvolvimento)
- [Testes](#testes)
- [Migrações de Banco de Dados](#migrações-de-banco-de-dados)

## Descrição

Este repositório contém a implementação de um case de seleção para desenvolvedor backend. Não se trata de um projeto real, mas sim de um exercício prático para avaliar habilidades de programação. Não há intenção de uso em produção.

FilmesTop API é um serviço backend desenvolvido para gerenciar um sistema de aluguel de filmes online. Esta API permite que os usuários explorem um vasto catálogo de filmes, realizem aluguéis, avaliem os títulos assistidos e gerenciem seu histórico de locações.

## Funcionalidades

- 🎬 Listagem de filmes disponíveis por gênero
- 📊 Detalhamento completo de informações sobre filmes específicos
- 🛒 Sistema de aluguel de filmes
- ⭐ Avaliação personalizada de filmes alugados
- 📅 Visualização detalhada do histórico de aluguéis dos usuários

## Tecnologias Utilizadas

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| Python | 3.11 | Linguagem de programação principal |
| Flask | 3.0.3 | Framework web para construção da API |
| SQLAlchemy | 2.0.34 | ORM para interação com o banco de dados |
| PostgreSQL | 13.x | Sistema de gerenciamento de banco de dados |
| Marshmallow | 3.19.0 | Biblioteca para serialização/desserialização |
| Alembic | 1.13.2 | Ferramenta para migrações de banco de dados |

## Instalação e Configuração

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.11
- PostgreSQL 13.x
- pip (gerenciador de pacotes do Python)

### Passos de Instalação

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/Pedro-Emanuel/filmestop-api.git
   cd filmestop-api
   ```

2. **Crie e ative um ambiente virtual:**

   ```bash
   python3.11 -m venv venv_py311
   source venv_py311/bin/activate  # No Windows use: venv_py311\Scripts\activate
   ```

3. **Instale as dependências do projeto:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**

   Crie um arquivo `.env` na raiz do projeto e adicione:

   ```env
   DB_USER=seu_usuario
   DB_PASS=sua_senha
   DB_NAME=filmestop_db
   DB_HOST=localhost # Local
   # DB_HOST=db # Docker
   ```

    **Nota de Segurança:** Este exemplo é fornecido apenas para fins educativos e de demonstração. Mantenha suas credenciais seguras e não as compartilhe publicamente.

5. **Inicialize o postgres:**

   Certifique-se de que o PostgreSQL está instalado e em execução. Se necessário, inicie o serviço:

   ```bash
   # No Linux (systemd):
   sudo systemctl start postgresql

   # No macOS:
   brew services start postgresql

   # No Windows:
   # Inicie o serviço PostgreSQL através do Gerenciador de Serviços
   ```

   Configure o banco de dados e o usuário:

   ```bash
   sudo -u postgres psql

   # Mesmo usuário e senha definidos no .env
   # No prompt do PostgreSQL, execute:
   CREATE DATABASE filmestop_db;
   CREATE USER seu_usuario WITH PASSWORD 'sua_senha';
   GRANT ALL PRIVILEGES ON DATABASE filmestop_db TO seu_usuario;
   \c filmestop_db
   GRANT ALL ON SCHEMA public TO seu_usuario;
   ALTER SCHEMA public OWNER TO seu_usuario;
   \q
   ```

6. **Inicialize o banco de dados:**

   Abra um novo terminal, entre no ambiente virtual e execute as migrações do banco de dados:

   ```bash
   flask db upgrade
   ```

7. **Execute o servidor de desenvolvimento:**

   ```bash
   python run.py
   ```

8. **Popule o banco de dados:**

   Para adicionar dados iniciais ao banco de dados, execute o script `populate_db.sh`:

   ```bash
   chmod +x populate_db.sh
   ./populate_db.sh
   ```

   Este script adicionará alguns filmes e usuários ao banco de dados para testes.

   Experimente olhar as rotas de admin no app/routes.py (apenas para testes).

## Uso da API

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/movies` | Lista todos os filmes |
| GET | `/movies/genre?genre=<genero>` | Lista filmes por gênero |
| GET | `/movies/<id>` | Obtém detalhes de um filme específico |
| POST | `/rent` | Aluga um filme |
| POST | `/rate` | Avalia um filme alugado |
| GET | `/users/<id>/rentals` | Lista aluguéis de um usuário |

### Exemplos de Requisições

#### Listar todos os filmes

```bash
curl -X GET http://localhost:5001/movies
```

#### Listar filmes por gênero

```bash
curl -X GET "http://localhost:5001/movies/genre?genre=com%C3%A9dia"
```

> ⚠️ **Importante:** Ao pesquisar gêneros ou títulos com caracteres especiais (como acentos), use a codificação URL apropriada.

**Exemplos de codificação:**

| Palavra   | Codificação URL    |
|-----------|--------------------|
| comédia   | `com%C3%A9dia`     |
| ficção    | `fic%C3%A7%C3%A3o` |

💡 **Dica:** Você pode usar [ferramentas online de codificação URL](https://www.urlencoder.org/) ou funções específicas em sua linguagem de programação para gerar a string codificada corretamente.

**Parâmetros opcionais:**

- `page`: Número da página (padrão: 1)
- `per_page`: Número de itens por página (padrão: 10)

**Exemplo com paginação:**

```bash
curl -X GET "http://localhost:5001/movies/genre?genre=com%C3%A9dia&page=1&per_page=5"
```

#### Detalhar informações de um filme

```bash
curl -X GET http://localhost:5001/movies/6
```

#### Alugar um filme

```bash
curl -X POST http://localhost:5001/rent \
     -H "Content-Type: application/json" \
     -d '{"user_id": 10, "movie_id": 6}'
```

#### Avaliar um filme alugado

```bash
curl -X POST http://localhost:5001/rate \
     -H "Content-Type: application/json" \
     -d '{"user_id": 10, "movie_id": 6, "rating": 4.5}'
```

#### Listar aluguéis de um usuário

```bash
curl -X GET http://localhost:5001/users/10/rentals
```

## Desenvolvimento

### Estrutura do Projeto

A estrutura do projeto segue o seguinte padrão:

```plaintext
filmestop-api/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── utils.py
│
├── migrations/
│   ├── versions/
│   │   ├── 2ee9952e7b50_init.py
│   │   └── 55fbe96430b8_adding_final_grade_and_total_ratings_to_.py
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── tests/
│   ├── conftest.py
│   ├── __init__.py
│   ├── test_models.py
│   └── test_routes.py
│
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Testes

Para executar os testes unitários:

```bash
python -m pytest tests/
```

Os testes estão organizados nos seguintes arquivos:

- `test_models.py`: Testes para os modelos de dados
- `test_routes.py`: Testes para as rotas da API

## Migrações de Banco de Dados

As migrações do banco de dados são gerenciadas usando Alembic através do Flask-Migrate.

### Criando uma nova migração

Para criar uma nova migração após fazer alterações nos modelos:

```bash
flask db migrate -m "Descrição da migração"
```

### Aplicando migrações

Para aplicar as migrações pendentes ao banco de dados:

```bash
flask db upgrade
```

### Revertendo migrações

Para reverter a última migração aplicada:

```bash
flask db downgrade
```

### Histórico de migrações

As migrações existentes podem ser encontradas no diretório `migrations/versions/`. Atualmente, temos as seguintes migrações:

1. `2ee9952e7b50_init.py`: Migração inicial
2. `55fbe96430b8_adding_final_grade_and_total_ratings_to_.py`: Adição de nota final e total de avaliações à tabela de filmes

Para ver o histórico completo de migrações:

```bash
flask db history
```
