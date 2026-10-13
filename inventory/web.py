from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.shortcuts import render
from django.utils.http import urlencode

from .models import Product

ITENS_POR_PAGINA = 25


@login_required
def product_list(request):
    query = request.GET.get("q", "").strip()
    only_low = request.GET.get("baixo") == "1"

    produtos = Product.objects.select_related("category", "supplier").order_by("name")
    if query:
        produtos = produtos.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if only_low:
        produtos = produtos.filter(quantity__lte=F("minimum_stock"))

    pagina = Paginator(produtos, ITENS_POR_PAGINA).get_page(request.GET.get("page"))

    # Totais calculados pelo banco, sem carregar os produtos na memória.
    filtrado = produtos.aggregate(total=Count("id"), unidades=Sum("quantity"))
    geral = Product.objects.aggregate(total=Count("id"), unidades=Sum("quantity"))
    para_repor = Product.objects.filter(quantity__lte=F("minimum_stock")).select_related("supplier")

    parametros_filtro = urlencode(
        {k: v for k, v in {"q": query, "baixo": "1" if only_low else ""}.items() if v}
    )

    return render(
        request,
        "inventory/product_list.html",
        {
            "pagina": pagina,
            "products": pagina.object_list,
            "total_filtrado": filtrado["total"],
            "unidades_filtrado": filtrado["unidades"] or 0,
            "total_geral": geral["total"],
            "unidades_geral": geral["unidades"] or 0,
            "low_stock_count": para_repor.count(),
            "low_stock": para_repor.order_by("name")[:5],
            "query": query,
            "only_low": only_low,
            "parametros_filtro": parametros_filtro,
        },
    )
