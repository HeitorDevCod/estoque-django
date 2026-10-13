from django.db import transaction

from .models import Product, StockMovement


class InsufficientStockError(Exception):
    """Lançada quando uma saída excede a quantidade disponível."""


class InvalidQuantityError(ValueError):
    """Lançada quando a quantidade informada não é positiva."""


def register_movement(product_id, kind, quantity, note=""):
    """Registra uma entrada ou saída de estoque de forma atômica.

    A linha do produto é bloqueada (select_for_update) para que duas saídas
    simultâneas não consigam retirar mais do que o disponível.
    """
    if quantity <= 0:
        raise InvalidQuantityError("A quantidade deve ser maior que zero.")

    with transaction.atomic():
        product = Product.objects.select_for_update().get(pk=product_id)

        if kind == StockMovement.Kind.OUT:
            if quantity > product.quantity:
                raise InsufficientStockError(
                    f"Estoque insuficiente: disponível {product.quantity}, "
                    f"solicitado {quantity}."
                )
            product.quantity -= quantity
        elif kind == StockMovement.Kind.IN:
            product.quantity += quantity
        else:
            raise ValueError(f"Tipo de movimentação inválido: {kind}")

        product.save(update_fields=["quantity"])
        return StockMovement.objects.create(
            product=product, kind=kind, quantity=quantity, note=note
        )
