# FilmesTop API

![FilmesTop Logo](logo.png) 

## Índice

- [Descrição](#descrição)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso da API](#uso-da-api)
- [Desenvolvimento](#desenvolvimento)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

## Descrição

FilmesTop API é um serviço backend robusto desenvolvido para gerenciar um sistema de aluguel de filmes online. Esta API permite que os usuários explorem um vasto catálogo de filmes, realizem aluguéis, avaliem os títulos assistidos e gerenciem seu histórico de locações.

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
| Flask | 2.0.1 | Framework web para construção da API |
| SQLAlchemy | 1.4.x | ORM para interação com o banco de dados |
| PostgreSQL | 13.x | Sistema de gerenciamento de banco de dados |
| Marshmallow | 3.14.x | Biblioteca para serialização/desserialização |
| Alembic | 1.7.x | Ferramenta para migrações de banco de dados |

## Instalação e Configuração

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.11
- PostgreSQL
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
   DB_HOST=localhost
   ```

5. **Inicialize o banco de dados:**

   ```bash
   flask db upgrade
   ```

6. **Execute o servidor de desenvolvimento:**

   ```bash
   python run.py
   ```

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
curl -X GET http://localhost:5000/movies
```

#### Listar filmes por gênero

```bash
curl -X GET "http://localhost:5000/movies/genre?genre=com%C3%A9dia"
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
curl -X GET "http://localhost:5000/movies/genre?genre=com%C3%A9dia&page=1&per_page=5"
```

#### Detalhar informações de um filme

```bash
curl -X GET http://localhost:5000/movies/6
```

#### Alugar um filme

```bash
curl -X POST http://localhost:5000/rent \
     -H "Content-Type: application/json" \
     -d '{"user_id": 10, "movie_id": 6}'
```

#### Avaliar um filme alugado

```bash
curl -X POST http://localhost:5000/rate \
     -H "Content-Type: application/json" \
     -d '{"user_id": 10, "movie_id": 6, "rating": 4.5}'
```

#### Listar aluguéis de um usuário

```bash
curl -X GET http://localhost:5000/users/10/rentals
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

<!-- ### Executando Testes

Para executar os testes unitários:

```bash
python -m pytest tests/
``` -->

<!-- ### Adicionando Novas Migrações

Para criar e aplicar novas migrações de banco de dados:

```bash
flask db migrate -m "Descrição da migração"
flask db upgrade
``` -->
