# 0002. Movimentações de estoque são imutáveis

## Contexto

A quantidade de um produto pode ser alterada de várias formas. Se ela puder ser editada diretamente, o histórico deixa de bater com o saldo atual, e não há como auditar o que aconteceu.

## Decisão

- A quantidade do produto é somente leitura na API.
- Toda alteração acontece por meio de uma `StockMovement` (entrada ou saída), criada pelo serviço `register_movement`.
- Movimentações não podem ser editadas nem apagadas pela API.

## Consequências

- O saldo sempre é a soma do histórico, e isso pode ser verificado.
- Correções precisam ser feitas com uma nova movimentação, não com edição do registro antigo.
- Quem precisa de ajuste de inventário terá que criar uma entrada ou saída com observação explicando o motivo.

Veja também [0003](0003-trava-no-banco-nas-saidas.md).
