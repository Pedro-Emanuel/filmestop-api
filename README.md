# FilmesTop API

## Descrição

FilmesTop API é um serviço backend desenvolvido para gerenciar um sistema de aluguel de filmes online. Esta API permite que os usuários naveguem por um catálogo de filmes, aluguem títulos, avaliem filmes assistidos e gerenciem suas locações.

## Funcionalidades

- Listagem de filmes disponíveis por gênero
- Detalhamento de informações sobre filmes específicos
- Sistema de aluguel de filmes
- Avaliação de filmes alugados
- Visualização do histórico de aluguéis dos usuários

## Tecnologias Utilizadas

- Python 3.11
- Flask (Framework web)
- SQLAlchemy (ORM)
- PostgreSQL (Banco de dados)
- Marshmallow (Serialização/Desserialização)
- Alembic (Migrações de banco de dados)

## Instalação e Configuração

### Pré-requisitos

- Python 3.11
- PostgreSQL
- pip (gerenciador de pacotes do Python)

### Passos de Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/Pedro-Emanuel/filmestop-api.git
    cd filmestop-api
    ```

2. Crie e ative um ambiente virtual:

    ```bash
    python3.11 -m venv venv_py311
    source venv_py311/bin/activate  # No Windows use: venv_py311\Scripts\activate
    ```

3. Instale as dependências do projeto:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure as variáveis de ambiente:

    Crie um arquivo `.env` na raiz do projeto e adicione:

    ```bash
    DB_USER=seu_usuario
    DB_PASS=sua_senha
    DB_NAME=filmestop_db
    DB_HOST=localhost
    ```

5. Inicialize o banco de dados:

    ```bash
    flask db upgrade
    ```

6. Execute o servidor de desenvolvimento:

    ```bash
    python run.py
    ```

## Uso da API

### Endpoints Principais

- `GET /movies`: Lista todos os filmes
- `GET /movies/genre?genre=<genero>`: Lista filmes por gênero
- `GET /movies/<id>`: Obtém detalhes de um filme específico
- `POST /rent`: Aluga um filme
- `POST /rate`: Avalia um filme alugado
- `GET /users/<id>/rentals`: Lista aluguéis de um usuário

### Exemplo de Requisição

Listar todos os filmes:

```bash
@route GET /movies
curl http://localhost:5000/movies
```

Listar filmes por gênero:

```bash
@route GET /movies/genre?genre=<genero>
curl http://localhost:5000/movies/genre?genre=comédia
curl http://localhost:5000/movies/genre?genre=comédia&page=1&per_page=10
```

`
page e per_page são opcionais (default: page=1, per_page=10)
`

Detalhar informações de um filme:

```bash
@route GET /movies/<movie_id>
curl http://localhost:5000/movies/1
```

Alugar um filme:

```bash
@route POST /rent
@body {user_id: int, movie_id: int}
curl -X POST http://localhost:5000/rent \
 -H "Content-Type: application/json" \
 -d '{"user_id": 10, "movie_id": 6}'
```

Avaliar um filme alugado:

```bash
@route POST /rate
@body {user_id: int, movie_id: int, rating: float}
curl -X POST http://localhost:5000/rate \
 -H "Content-Type: application/json" \
 -d '{"user_id": 10, "movie_id": 6, "rating": 4.5}'
```

Listar aluguéis de um usuário:

```bash
@route GET /users/<user_id>/rentals
curl http://localhost:5000/users/10/rentals
```

## Desenvolvimento

### Estrutura do Projeto

A estrutura do projeto segue o seguinte padrão:

``` bash
    filmestop-api/
│
├── app/
│   ├── init.py
│   ├── models.py
│   └── routes.py
│
├── migrations/
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```
