"""Seleção de permissões simplificada, usada nas telas de grupos e usuários.

- Esconde módulos técnicos do Django que a equipe da loja não usa.
- Mostra os nomes em linguagem simples ("Cadastrar produto", "Ver produto").
- Oferece atalhos prontos (Só consulta, Operador, Gerente) para evitar erros.
"""

from django import forms
from django.apps import apps
from django.contrib.auth.models import Permission

# Módulos técnicos que não aparecem para quem cadastra acessos.
MODULOS_OCULTOS = {"admin", "contenttypes", "sessions"}

ACOES = {"add": "Cadastrar", "change": "Alterar", "delete": "Excluir", "view": "Ver"}

MODELOS_ESTOQUE = ["product", "category", "supplier", "stockmovement"]

# Atalhos: nome exibido -> códigos das permissões marcadas ao clicar.
PERFIS = {
    "Só consulta": [f"view_{m}" for m in MODELOS_ESTOQUE],
    "Operador de estoque": [f"view_{m}" for m in MODELOS_ESTOQUE] + ["add_stockmovement"],
    "Gerente de estoque": [f"{a}_{m}" for a in ACOES for m in MODELOS_ESTOQUE],
}


def _nome_amigavel(permissao):
    modelo = permissao.content_type.model_class()
    acao = permissao.codename.split("_", 1)[0]
    if modelo is None or acao not in ACOES:
        return permissao.name
    return f"{ACOES[acao]} {modelo._meta.verbose_name}"


def opcoes_agrupadas():
    """Permissões visíveis, agrupadas por módulo, no formato de choices do Django."""
    grupos = {}
    permissoes = (
        Permission.objects.select_related("content_type")
        .exclude(content_type__app_label__in=MODULOS_OCULTOS)
        .order_by("content_type__app_label", "content_type__model", "codename")
    )
    for permissao in permissoes:
        app = permissao.content_type.app_label
        grupos.setdefault(app, []).append((permissao.pk, _nome_amigavel(permissao)))

    return [
        (apps.get_app_config(app).verbose_name, opcoes)
        for app, opcoes in grupos.items()
    ]


def _perfis_com_ids():
    perfis = []
    for nome, codigos in PERFIS.items():
        ids = Permission.objects.filter(
            content_type__app_label="inventory", codename__in=codigos
        ).values_list("pk", flat=True)
        perfis.append({"nome": nome, "ids": ",".join(str(pk) for pk in ids)})
    return perfis


class PermissoesWidget(forms.CheckboxSelectMultiple):
    template_name = "inventory/widgets/permissoes.html"

    class Media:
        js = ("js/permissoes.js",)

    def get_context(self, name, value, attrs):
        contexto = super().get_context(name, value, attrs)
        contexto["widget"]["perfis"] = _perfis_com_ids()
        return contexto


class PermissoesField(forms.TypedMultipleChoiceField):
    def prepare_value(self, value):
        if value is None:
            return []
        # Recebe objetos Permission ao editar e converte para os ids marcados.
        return [getattr(item, "pk", item) for item in value]


class PermissoesAdminMixin:
    """Troca o campo de permissões padrão pela seleção simplificada."""

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ("permissions", "user_permissions"):
            return PermissoesField(
                choices=opcoes_agrupadas(),
                coerce=int,
                required=False,
                label="Permissões",
                help_text="Use um atalho para começar ou marque item por item. Em cada módulo, 'Marcar todas' libera tudo daquele módulo.",
                widget=PermissoesWidget,
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)
