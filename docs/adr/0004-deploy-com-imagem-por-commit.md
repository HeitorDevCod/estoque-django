# 0004. Deploy com imagem Docker identificada pelo commit

## Contexto

Precisamos saber exatamente qual código está rodando em produção e conseguir voltar para uma versão anterior sem improviso.

## Decisão

- O workflow `deploy.yml` roda os testes e, se passarem, gera a imagem Docker e a envia ao GitHub Container Registry (GHCR).
- A imagem recebe como tag o SHA do commit.
- Rollback é feito subindo a imagem de um SHA anterior, com `docker-compose.producao.yml`.
- Segredos ficam em um arquivo `.env` no servidor, fora do repositório.

## Consequências

- Cada versão em produção tem um identificador único.
- O deploy depende de acesso ao servidor. Esta versão deixa o passo de atualização do servidor documentado no README, e não automatizado.
