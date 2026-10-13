from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inventory.models import Category, Product, StockMovement, Supplier
from inventory.services import register_movement

SUPPLIERS = [
    {"name": "Distribuidora Central", "email": "contato@central.example", "phone": "(11) 3000-0001"},
    {"name": "Atacado Bom Preço", "email": "vendas@bompreco.example", "phone": "(11) 3000-0002"},
]

CATEGORIES = ["Bebidas", "Mercearia", "Limpeza"]

# sku, nome, categoria, fornecedor, preço, estoque inicial, estoque mínimo, saída de demonstração
PRODUCTS = [
    ("BEB-001", "Água mineral 500 ml", "Bebidas", "Distribuidora Central", "2.50", 120, 30, 0),
    ("BEB-002", "Refrigerante lata 350 ml", "Bebidas", "Distribuidora Central", "5.90", 80, 24, 0),
    ("MER-001", "Arroz tipo 1 5 kg", "Mercearia", "Atacado Bom Preço", "27.90", 40, 10, 0),
    # Saída de 25 unidades: sobram 15, abaixo do mínimo de 20, então aparece como estoque baixo.
    ("MER-002", "Feijão carioca 1 kg", "Mercearia", "Atacado Bom Preço", "8.49", 40, 20, 25),
    ("LIM-001", "Detergente neutro 500 ml", "Limpeza", "Atacado Bom Preço", "2.19", 60, 15, 0),
]


class Command(BaseCommand):
    help = "Carrega fornecedores, categorias e produtos de exemplo. Só roda com DJANGO_DEBUG=1."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo só roda com DJANGO_DEBUG=1. Não use em produção."
            )

        with transaction.atomic():
            suppliers = {}
            for data in SUPPLIERS:
                supplier, _ = Supplier.objects.get_or_create(
                    name=data["name"],
                    defaults={"email": data["email"], "phone": data["phone"]},
                )
                suppliers[data["name"]] = supplier

            categories = {
                name: Category.objects.get_or_create(name=name)[0] for name in CATEGORIES
            }

            created = 0
            for sku, name, category, supplier, price, initial, minimum, out in PRODUCTS:
                if Product.objects.filter(sku=sku).exists():
                    continue

                product = Product.objects.create(
                    sku=sku,
                    name=name,
                    category=categories[category],
                    supplier=suppliers[supplier],
                    unit_price=Decimal(price),
                    quantity=0,
                    minimum_stock=minimum,
                )
                # Toda quantidade passa por movimentação, como nas regras do sistema.
                register_movement(
                    product.id, StockMovement.Kind.IN, initial, note="Estoque inicial (demo)"
                )
                if out:
                    register_movement(
                        product.id, StockMovement.Kind.OUT, out, note="Venda de demonstração"
                    )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} produto(s) de exemplo criado(s)."))
