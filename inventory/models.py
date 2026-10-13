from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("nome", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField("nome", max_length=150)
    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=30, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "fornecedor"
        verbose_name_plural = "fornecedores"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("nome", max_length=150)
    sku = models.CharField("código (SKU)", max_length=50, unique=True)
    category = models.ForeignKey(
        Category,
        verbose_name="categoria",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="fornecedor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    unit_price = models.DecimalField(
        "preço unitário",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.PositiveIntegerField("quantidade em estoque", default=0)
    minimum_stock = models.PositiveIntegerField(
        "estoque mínimo",
        default=0,
        help_text="Abaixo deste valor o produto aparece como estoque baixo.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        indexes = [
            models.Index(fields=["name"], name="produto_nome_idx"),
            models.Index(fields=["quantity", "minimum_stock"], name="produto_estoque_idx"),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock

    @property
    def fill_percent(self):
        """Percentual do mínimo coberto pelo estoque atual, limitado a 100."""
        if not self.minimum_stock:
            return 100
        return min(100, round(self.quantity * 100 / self.minimum_stock))


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        IN = "IN", "Entrada"
        OUT = "OUT", "Saída"

    product = models.ForeignKey(
        Product,
        verbose_name="produto",
        on_delete=models.PROTECT,
        related_name="movements",
    )
    kind = models.CharField("tipo", max_length=3, choices=Kind.choices)
    quantity = models.PositiveIntegerField(
        "quantidade", validators=[MinValueValidator(1)]
    )
    note = models.CharField("observação", max_length=255, blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "movimentação"
        verbose_name_plural = "movimentações"
        indexes = [
            models.Index(fields=["product", "-created_at"], name="movimento_produto_data_idx"),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} de {self.quantity} x {self.product.sku}"
