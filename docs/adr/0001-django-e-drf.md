# 0001. Usar Django e Django REST Framework

## Contexto

O sistema precisa de cadastro, regras de negócio, autenticação, painel administrativo e uma API para integrações futuras. Um time pequeno precisa entregar isso com poucas peças móveis.

## Decisão

Usar Django para o núcleo da aplicação e Django REST Framework para a API.

## Consequências

- Admin, autenticação, permissões e migrations vêm prontos, o que reduz código próprio.
- O acoplamento entre Django e o banco é alto, o que é aceitável para um sistema desse porte.
- Quem for mexer no projeto precisa conhecer o ORM e o ciclo de requisição do Django.

## Alternativas consideradas

- **FastAPI:** mais leve para APIs puras, mas exigiria escrever admin, autenticação e telas por conta própria.
