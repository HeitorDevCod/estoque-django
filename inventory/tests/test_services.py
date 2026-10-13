import pytest

from inventory.models import Product, StockMovement
from inventory.services import (
    InsufficientStockError,
    InvalidQuantityError,
    register_movement,
)


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="Caneca", sku="CAN-001", unit_price="25.00", quantity=10, minimum_stock=3
    )


def test_entrada_aumenta_estoque(product):
    register_movement(product.pk, StockMovement.Kind.IN, 5)

    product.refresh_from_db()
    assert product.quantity == 15


def test_saida_diminui_estoque_e_registra_movimentacao(product):
    movement = register_movement(product.pk, StockMovement.Kind.OUT, 4, note="venda")

    product.refresh_from_db()
    assert product.quantity == 6
    assert movement.kind == StockMovement.Kind.OUT
    assert movement.note == "venda"
    assert product.movements.count() == 1


def test_saida_maior_que_estoque_falha_sem_alterar_nada(product):
    with pytest.raises(InsufficientStockError):
        register_movement(product.pk, StockMovement.Kind.OUT, 11)

    product.refresh_from_db()
    assert product.quantity == 10
    assert product.movements.count() == 0


def test_quantidade_zero_ou_negativa_e_rejeitada(product):
    with pytest.raises(InvalidQuantityError):
        register_movement(product.pk, StockMovement.Kind.IN, 0)


def test_produto_com_estoque_no_minimo_aparece_como_baixo(product):
    product.quantity = 3
    assert product.is_low_stock is True

    product.quantity = 4
    assert product.is_low_stock is False
