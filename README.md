# Estoque

Sistema de gestão de estoque para pequenos negócios, feito com Django e Django REST Framework. Cadastro de produtos, categorias e fornecedores, com movimentações de entrada e saída que nunca são editadas diretamente, para que o histórico sempre bata com o saldo atual.

## Funcionalidades

- Cadastro de produtos (com SKU único), categorias e fornecedores
- Entradas e saídas de estoque, registradas como movimentações
- Bloqueio de saída quando não há saldo suficiente, com trava no banco para evitar saídas concorrentes
- Alerta de estoque baixo quando a quantidade fica igual ou abaixo do mínimo
- API REST com autenticação
- Painel administrativo do Django e tela de listagem de produtos

## Decisões de arquitetura

As decisões estão registradas em `docs/adr/`:

- [0001 - Django e DRF](docs/adr/0001-django-e-drf.md)
- [0002 - Movimentações imutáveis](docs/adr/0002-movimentacoes-imutaveis.md)
- [0003 - Trava no banco nas saídas](docs/adr/0003-trava-no-banco-nas-saidas.md)
- [0004 - Deploy com imagem por commit](docs/adr/0004-deploy-com-imagem-por-commit.md)

## Stack

- Python 3.12
- Django 5 e Django REST Framework
- PostgreSQL 16 (SQLite no desenvolvimento local, sem Docker)
- Docker e Docker Compose
- pytest e pytest-django
- GitHub Actions: testes em cada push e pull request, e publicação da imagem no GHCR

## Como rodar com Docker

```bash
docker compose up --build
```

Depois de subir os containers, crie um usuário administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

A aplicação fica em `http://localhost:8000`.

> O `docker-compose.yml` usa credenciais de exemplo do PostgreSQL (`estoque`/`estoque`) e `DJANGO_DEBUG=1`. Isso serve só para desenvolvimento local. Não use esse arquivo em produção.

## Como rodar localmente (sem Docker)

Sem `POSTGRES_HOST` definido, o projeto usa SQLite.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Variáveis de ambiente

| Variável | Padrão | Função |
|---|---|---|
| `DJANGO_SECRET_KEY` | `dev-only-insecure-key` | Chave secreta do Django. Defina sempre em produção. |
| `DJANGO_DEBUG` | `1` | `1` liga o modo debug. Use `0` em produção. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts aceitos, separados por vírgula. |
| `POSTGRES_HOST` | (vazio) | Se definido, o projeto usa PostgreSQL. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` | `estoque`, `estoque`, `estoque`, `5432` | Conexão com o banco. |

Em produção, copie `.env.example` para `.env`, preencha os valores e nunca versione o `.env`. O arquivo `docker-compose.producao.yml` lê as variáveis desse `.env`.

## Testes

```bash
pytest
```

## Benchmark

O script `scripts/benchmark.py` gera 50 mil produtos e 500 mil movimentações, mede a página de produtos e depois remove os dados de teste. **Não rode em banco de produção.**

```bash
docker compose exec -T -e BENCH=seed web python manage.py shell < scripts/benchmark.py
docker compose exec -T -e BENCH=measure web python manage.py shell < scripts/benchmark.py
docker compose exec -T -e BENCH=cleanup web python manage.py shell < scripts/benchmark.py
```

## Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/products/` | Listar e cadastrar produtos |
| GET | `/api/products/low-stock/` | Produtos com estoque baixo |
| GET/POST | `/api/movements/` | Listar e registrar movimentações |
| GET/POST | `/api/categories/` | Categorias |
| GET/POST | `/api/suppliers/` | Fornecedores |

A quantidade de um produto só muda por meio de movimentações.

## Estrutura

```
config/                 configurações do projeto (settings, urls, wsgi)
docs/adr/               decisões de arquitetura
inventory/
  models.py             Product, Category, Supplier, StockMovement
  services.py           regra de negócio das movimentações
  serializers.py
  views.py
  urls.py
  admin.py
  web.py                tela de listagem de produtos
  tests/                testes de serviço, API, web e permissões
scripts/benchmark.py    carga de teste para medir desempenho
```
