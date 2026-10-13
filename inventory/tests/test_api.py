import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from inventory.models import Product


@pytest.fixture
def client(db):
    user = get_user_model().objects.create_user(username="ana", password="senha-forte-123")
    api = APIClient()
    api.force_authenticate(user=user)
    return api


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="Caneca", sku="CAN-001", unit_price="25.00", quantity=2, minimum_stock=3
    )


def test_api_exige_autenticacao():
    response = APIClient().get("/api/products/")
    assert response.status_code in (401, 403)


def test_criar_saida_pela_api_atualiza_estoque(client, product):
    response = client.post(
        "/api/movements/",
        {"product": product.pk, "kind": "OUT", "quantity": 1, "note": "venda"},
        format="json",
    )

    assert response.status_code == 201
    product.refresh_from_db()
    assert product.quantity == 1


def test_saida_sem_estoque_retorna_erro_400(client, product):
    response = client.post(
        "/api/movements/",
        {"product": product.pk, "kind": "OUT", "quantity": 5},
        format="json",
    )

    assert response.status_code == 400
    assert "quantity" in response.json()


def test_quantidade_nao_pode_ser_alterada_direto_no_produto(client, product):
    response = client.patch(
        f"/api/products/{product.pk}/", {"quantity": 999}, format="json"
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.quantity == 2


def test_listagem_de_estoque_baixo(client, product):
    response = client.get("/api/products/low-stock/")

    assert response.status_code == 200
    skus = [item["sku"] for item in response.json()]
    assert "CAN-001" in skus
