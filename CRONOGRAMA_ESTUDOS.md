# Cronograma de estudos: projeto Estoque

Carga: 5 horas por dia. Duração: cerca de 16 semanas (4 meses).

Como usar: para cada etapa, leia os arquivos indicados, rode o código, quebre algo de propósito e corrija. Depois, feche o arquivo e reescreva a parte principal sem olhar. Só avance quando conseguir explicar o que cada linha faz.

---

## Etapa 1 (semanas 1 a 2): Python e Django básico

**Conceitos:** ambiente virtual, pacotes, projeto vs. app, rotas, MTV (models, views, templates), `manage.py`.

**Estude nestes arquivos:**
- `manage.py`: como o Django recebe comandos
- `config/settings.py`: `INSTALLED_APPS`, `DATABASES`, `REST_FRAMEWORK`
- `config/urls.py`: como as rotas são montadas

**Exercício:** suba o projeto com `python manage.py runserver` e acesse `/admin/` e `/api/`. Mude o `TIME_ZONE` e veja o efeito.

---

## Etapa 2 (semanas 3 a 4): Modelagem de dados

**Conceitos:** `models.Model`, campos, `ForeignKey`, `on_delete`, `Meta`, migrations, `__str__`, `@property`.

**Estude:** `inventory/models.py`

**Perguntas para responder:**
- Por que `on_delete=PROTECT` em `StockMovement.product` e `SET_NULL` em `Product.category`?
- Por que `is_low_stock` é uma property e não um campo?
- O que muda no banco quando você roda `makemigrations`?

**Exercício:** adicione um campo `location` (localização no depósito) ao `Product`, gere a migration e leia o arquivo gerado.

---

## Etapa 3 (semanas 5 a 6): Regra de negócio e transações

**Conceitos:** `transaction.atomic`, `select_for_update`, exceções próprias, separação entre regra de negócio e camada HTTP.

**Estude:** `inventory/services.py`

**Pergunta central:** o que aconteceria se duas saídas chegassem ao mesmo tempo sem o `select_for_update`? Tente simular com dois terminais e veja o resultado.

**Exercício:** escreva um teste que tenta duas saídas de 6 unidades em um produto com 10 e confirme que a segunda falha.

---

## Etapa 4 (semanas 7 a 8): Testes

**Conceitos:** pytest, fixtures, `pytest.raises`, testes de API com `APIClient`, teste de regra vs. teste de endpoint.

**Estude:** `inventory/tests/test_services.py` e `inventory/tests/test_api.py`

**Exercício:** apague uma linha de `services.py` (por exemplo, o `product.save`) e veja qual teste quebra. Depois restaure.

**Meta:** escreva três testes novos sem consultar o projeto: um para `register_movement` com entrada, um para a listagem de estoque baixo, e um para o endpoint de categorias.

---

## Etapa 5 (semanas 9 a 10): API com Django REST Framework

**Conceitos:** serializers, `ModelViewSet`, `@action`, `read_only_fields`, permissões, paginação, status HTTP.

**Estude:** `inventory/serializers.py`, `inventory/views.py`, `inventory/urls.py`

**Perguntas:**
- Por que `quantity` é read-only no `ProductSerializer`?
- Por que `StockMovementViewSet` não tem `update` nem `destroy`?
- O que o `DefaultRouter` gera automaticamente?

**Exercício:** use o navegador em `/api/products/` (a interface do DRF) para criar produtos e movimentações.

---

## Etapa 6 (semanas 11 e 12): Admin, autenticação e segurança

**Conceitos:** `admin.register`, `list_display`, `list_filter`, `search_fields`, autenticação de sessão e Basic, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.

**Estude:** `inventory/admin.py` e as variáveis de ambiente em `config/settings.py`

**Exercício:** crie um usuário no admin, cadastre dados pela interface e compare com o que a API retorna. Depois, tente acessar a API sem login e veja o erro.

---

## Etapa 7 (semana 13): Docker

**Conceitos:** imagem, container, volume, variáveis de ambiente, `depends_on` com healthcheck.

**Estude:** `Dockerfile` e `docker-compose.yml`

**Perguntas:**
- Por que `requirements.txt` é copiado antes do resto do código?
- Por que o banco usa `volumes`?
- O que acontece com os dados se você rodar `docker compose down -v`?

**Exercício:** rode `docker compose up --build`, cadastre dados, pare e suba de novo. Os dados continuam?

---

## Etapa 8 (semana 14): CI com GitHub Actions

**Conceitos:** workflow, jobs, `services` para banco de teste, cache de dependências, `makemigrations --check`.

**Estude:** `.github/workflows/ci.yml`

**Exercício:** crie um repositório no GitHub, envie o projeto e acompanhe a execução na aba Actions. Quebre um teste de propósito, veja o pipeline falhar e corrija.

---

## Etapa 9 (semanas 15 e 16): Reescrita e revisão

**Objetivo:** consolidar tudo.

1. Apague a pasta `inventory/` em uma cópia do projeto e reescreva o app do zero, consultando só a documentação oficial.
2. Compare o seu código com o original e anote as diferenças.
3. Adicione uma funcionalidade nova que você escolher, por exemplo: relatório de movimentações por período, ou um campo de validade para produtos.
4. Escreva um parágrafo explicando, com suas palavras, as três decisões técnicas mais importantes do projeto (por exemplo: por que a quantidade só muda por movimentação, e por que existe `select_for_update`).

---

## Checklist final

- [ ] Consigo explicar cada arquivo do projeto sem consultar
- [ ] Reescrevi `models.py`, `services.py` e pelo menos um endpoint do zero
- [ ] Escrevi testes novos sem olhar o projeto original
- [ ] Rodo o projeto com Docker e o CI passa no GitHub
- [ ] Adicionei uma funcionalidade nova sozinho
