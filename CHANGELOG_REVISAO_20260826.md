# Revisão de produção 2026-08-26

## Incidente corrigido

O `yfinance` estava sendo chamado com `repair=True`. Em algumas rotinas esse modo depende de SciPy. Como SciPy não estava instalado, o próprio `yfinance` encerrava o download e retornava um DataFrame vazio. O aplicativo interpretava o vazio como "ticker inválido", escondendo a causa real.

Correções:

- SciPy incluído nas dependências;
- detecção preventiva da disponibilidade de SciPy;
- uso automático de `repair=False` quando SciPy não estiver disponível;
- segunda tentativa sem `repair` quando a primeira consulta retornar vazia;
- validação de colunas, tipos, duplicidades e preços inválidos;
- mensagem ao usuário não afirma mais que o ticker é inválido quando a origem pode ser a fonte de dados.

## Leitura de mercado

O motor de pontuação foi preservado para não alterar sinais sem validação histórica. Foram acrescentados alertas de liquidez financeira sem mudar a pontuação.

A apresentação foi reorganizada para um leitor não técnico:

- resumo direto primeiro;
- significado prático do sinal;
- força do sinal e qualidade do plano;
- suporte e resistência;
- plano de risco quando aplicável;
- indicadores detalhados ficam recolhidos;
- explicação por IA é complementar e não pode mudar o sinal.

## Interface

Home e relatório usam a mesma identidade visual. Os acessos a Histórico e Backtest passam a ser controles separados.

## Segurança metodológica

`COMPRA`, `VENDA` e `NEUTRO` continuam sendo vieses técnicos do motor. A interface evita tratá-los como ordens pessoais de investimento. VENDA é explicitamente descrita como cenário desfavorável/cautela, e não como instrução de venda a descoberto.


## v2 - correção pós-validação na VPS

- Corrigido `relatorio.html` para não falhar quando um payload legado/teste não trouxer `atr_percentual`.
- O template calcula `ATR/preço` a partir de `atr14 / preco` como fallback seguro.
- Atualizado teste de relação risco-retorno para a apresentação atual `1 para X`.
- Mock de rota atualizado para refletir os campos atuais do contrato do motor.
- Adicionado teste de regressão para impedir novo HTTP 500 por ausência de `atr_percentual`.

## Motor V3.1 em observação paralela

- Adicionado Motor V3.1 congelado em shadow mode.
- O V3.1 não altera o sinal visível da aplicação nesta fase.
- Contexto de mercado usa BOVA11.
- Sinal comprador exige tendência de alta, rompimento de 20 pregões, confirmação da barra,
  volume, liquidez, volatilidade e limites de extensão.
- Tendência de baixa é registrada como EVITAR, sem gerar operação vendida.
- Criadas tabelas SQLite separadas para leituras V3.1 e resultados prospectivos futuros.
- Falhas do shadow mode são isoladas e não derrubam a análise principal.
- Incluído script de diagnóstico `scripts/shadow_v31_status.py`.
