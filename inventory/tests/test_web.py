import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from inventory.models import Product


@pytest.fixture
def logged_client(db):
    user = get_user_model().objects.create_user(username="ana", password="senha-forte-123")
    client = Client()
    client.force_login(user)
    return client


def test_pagina_inicial_exige_login(client):
    response = client.get("/")
    assert response.status_code == 302


def test_pagina_inicial_lista_produtos_e_alerta_estoque_baixo(logged_client):
    Product.objects.create(name="Caneca", sku="CAN-001", unit_price="25.00", quantity=1, minimum_stock=3)

    response = logged_client.get("/")

    assert response.status_code == 200
    assert b"CAN-001" in response.content
    assert "1 produto(s) abaixo do estoque mínimo".encode() in response.content


def test_busca_filtra_por_nome_ou_sku(logged_client):
    Product.objects.create(name="Caneca", sku="CAN-001", unit_price="25.00", quantity=5, minimum_stock=1)
    Product.objects.create(name="Papel A4", sku="PAP-001", unit_price="29.00", quantity=5, minimum_stock=1)

    response = logged_client.get("/", {"q": "papel"})

    assert b"PAP-001" in response.content
    assert b"CAN-001" not in response.content


def test_filtro_estoque_baixo_mostra_apenas_produtos_no_minimo(logged_client):
    Product.objects.create(name="Caneca", sku="CAN-001", unit_price="25.00", quantity=1, minimum_stock=3)
    Product.objects.create(name="Papel A4", sku="PAP-001", unit_price="29.00", quantity=50, minimum_stock=3)

    response = logged_client.get("/", {"baixo": "1"})

    assert b"CAN-001" in response.content
    assert b"PAP-001" not in response.content
