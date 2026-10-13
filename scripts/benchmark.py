"""Benchmark da listagem de produtos.

Gera dados de teste com o prefixo PERF- e mede o tempo de resposta da página.
Não rode em um banco de produção.

Uso, dentro do container (o script é lido pela entrada padrão):

    docker compose exec -T -e BENCH=seed web python manage.py shell < scripts/benchmark.py
    docker compose exec -T -e BENCH=measure web python manage.py shell < scripts/benchmark.py
    docker compose exec -T -e BENCH=cleanup web python manage.py shell < scripts/benchmark.py
"""

import os
import random
import statistics
import time

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from inventory.models import Category, Product, StockMovement, Supplier

ACAO = os.environ.get("BENCH", "measure")
PREFIXO = "PERF-"
N_PRODUTOS = 50_000
N_MOVIMENTOS = 500_000
LOTE = 5_000
random.seed(42)


def gerar():
    if Product.objects.filter(sku__startswith=PREFIXO).exists():
        print("Dados de teste já existem. Rode BENCH=cleanup antes de gerar de novo.")
        return

    categorias = [Category.objects.get_or_create(name=f"Categoria perf {i}")[0] for i in range(20)]
    fornecedores = [Supplier.objects.get_or_create(name=f"Fornecedor perf {i}")[0] for i in range(50)]
    cores = ["azul", "verde", "grande", "pequeno", "branco", "preto"]

    produtos = [
        Product(
            name=f"Produto {i:06d} {random.choice(cores)}",
            sku=f"{PREFIXO}{i:06d}",
            category=random.choice(categorias),
            supplier=random.choice(fornecedores),
            unit_price=round(random.uniform(5, 500), 2),
            quantity=random.randint(0, 200),
            minimum_stock=random.randint(0, 30),
        )
        for i in range(N_PRODUTOS)
    ]
    Product.objects.bulk_create(produtos, batch_size=LOTE)
    print(f"{N_PRODUTOS} produtos criados")

    ids = list(Product.objects.filter(sku__startswith=PREFIXO).values_list("id", flat=True))
    lote = []
    for _ in range(N_MOVIMENTOS):
        lote.append(
            StockMovement(
                product_id=random.choice(ids),
                kind=random.choice(["IN", "OUT"]),
                quantity=random.randint(1, 10),
                note="carga de teste",
            )
        )
        if len(lote) == LOTE:
            StockMovement.objects.bulk_create(lote)
            lote = []
    if lote:
        StockMovement.objects.bulk_create(lote)
    print(f"{N_MOVIMENTOS} movimentações criadas")


def medir():
    usuario, _ = get_user_model().objects.get_or_create(username="bench")
    if not usuario.has_usable_password():
        usuario.set_password("bench-123")
        usuario.save()

    cliente = Client(HTTP_HOST="localhost")
    cliente.force_login(usuario)

    cenarios = {
        "lista (primeira página)": "/",
        "busca por SKU exato": f"/?q={PREFIXO}000123",
        "busca por termo comum": "/?q=Produto",
        "filtro estoque baixo": "/?baixo=1",
        "página 1000": "/?page=1000",
    }

    print(f"{'cenário':28} {'mediana (ms)':>13} {'consultas':>10}")
    for nome, url in cenarios.items():
        tempos = []
        consultas = None
        for _ in range(5):
            with CaptureQueriesContext(connection) as contexto:
                inicio = time.perf_counter()
                resposta = cliente.get(url)
                tempos.append((time.perf_counter() - inicio) * 1000)
            assert resposta.status_code == 200, (url, resposta.status_code)
            consultas = len(contexto.captured_queries)
        print(f"{nome:28} {statistics.median(tempos):13.1f} {consultas:10}")


def limpar():
    StockMovement.objects.filter(product__sku__startswith=PREFIXO).delete()
    Product.objects.filter(sku__startswith=PREFIXO).delete()
    Category.objects.filter(name__startswith="Categoria perf").delete()
    Supplier.objects.filter(name__startswith="Fornecedor perf").delete()
    print("Dados de teste removidos")


if ACAO == "seed":
    gerar()
elif ACAO == "measure":
    medir()
elif ACAO == "cleanup":
    limpar()
else:
    print(f"Ação desconhecida: {ACAO}")
