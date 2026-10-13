# 0003. Trava de linha nas saídas de estoque

## Contexto

Duas saídas simultâneas do mesmo produto podem ler o mesmo saldo e, juntas, retirar mais do que existe. Isso acontece quando a verificação de saldo e a atualização não são atômicas.

## Decisão

`register_movement` roda dentro de `transaction.atomic()` e bloqueia a linha do produto com `select_for_update()` antes de ler o saldo.

## Consequências

- Saídas concorrentes do mesmo produto são executadas uma depois da outra.
- O bloqueio só funciona com um banco que suporte `SELECT ... FOR UPDATE`. O PostgreSQL suporta; o SQLite, usado nos testes locais, ignora a instrução.
- Operações de leitura não são bloqueadas.

Veja também [0002](0002-movimentacoes-imutaveis.md).
