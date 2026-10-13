import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


@pytest.fixture
def admin_client(db, client):
    admin = get_user_model().objects.create_superuser("chefe", "chefe@local.test", "senha-forte-123")
    client.force_login(admin)
    return client


def test_pagina_de_grupo_mostra_permissoes_agrupadas(admin_client):
    response = admin_client.get("/admin/auth/group/add/")

    assert response.status_code == 200
    assert b"grupo-permissoes" in response.content
    assert b"marcar-grupo" not in response.content or b"Marcar todas" in response.content


def test_modulos_tecnicos_do_django_ficam_ocultos(admin_client):
    response = admin_client.get("/admin/auth/group/add/")

    assert "Tipos de Conteúdo".encode() not in response.content
    assert "Sessões".encode() not in response.content
    assert b"Pode adicionar tipo de conte" not in response.content


def test_atalho_gerente_marca_todas_as_permissoes_do_estoque(admin_client):
    from inventory.admin_permissoes import PERFIS

    response = admin_client.get("/admin/auth/group/add/")

    assert response.status_code == 200
    assert "Gerente de estoque".encode() in response.content
    assert len(PERFIS["Gerente de estoque"]) == 16


def test_salvar_grupo_com_permissoes_marcadas(admin_client):
    permissoes = list(Permission.objects.filter(codename__in=["view_product", "add_stockmovement"]))
    ids = [p.pk for p in permissoes]

    response = admin_client.post(
        "/admin/auth/group/add/",
        {"name": "Operadores", "permissions": ids},
    )

    assert response.status_code == 302
    grupo = Group.objects.get(name="Operadores")
    assert set(grupo.permissions.values_list("pk", flat=True)) == set(ids)


def test_editar_grupo_mostra_permissoes_ja_marcadas(admin_client):
    grupo = Group.objects.create(name="Estoquistas")
    permissao = Permission.objects.get(codename="view_product")
    grupo.permissions.add(permissao)

    response = admin_client.get(f"/admin/auth/group/{grupo.pk}/change/")

    assert response.status_code == 200
    assert f'value="{permissao.pk}" checked'.encode() in response.content
