# Motor V3.1

## Status

O Motor V3.1 está em **shadow mode** desde 26/08/2026.

Ele roda em paralelo ao motor visível atual, registra sua própria leitura no SQLite e **não altera o sinal mostrado ao usuário**.

Versão congelada no código:

```text
3.1-shadow-20260826
```

## Objetivo

Separar melhor quatro conceitos que o motor original tendia a misturar:

1. direção do ativo;
2. regime do mercado;
3. qualidade do gatilho;
4. oportunidade acionável.

O V3.1 também evita tratar indicadores altamente correlacionados como várias confirmações independentes.

## Contexto de mercado

O benchmark usado é:

```text
BOVA11.SA
```

O regime pode ser classificado como alta, baixa ou lateral a partir da estrutura do benchmark.

## Estados

O V3.1 trabalha com:

| Estado | Interpretação |
|---|---|
| `COMPRA` | rompimento comprador confirmado e filtros aprovados |
| `AGUARDAR` | contexto favorável, mas sem gatilho suficiente |
| `EVITAR` | contexto técnico desfavorável para compra |
| `NEUTRO` | ausência de direção ou confirmação suficiente |

Nesta fase, o V3.1 não usa `VENDA` como operação a descoberto.

## Hipótese congelada

O sinal comprador exige, entre outros critérios:

- tendência de alta no ativo;
- BOVA11 fora de regime baixista;
- rompimento da resistência dos 20 pregões anteriores;
- fechamento forte na barra;
- amplitude relevante em ATR;
- confirmação mínima de volume;
- liquidez financeira mínima;
- volatilidade abaixo do limite;
- preço não excessivamente esticado em relação à EMA21;
- RSI e retorno de 20 pregões dentro dos limites definidos.

Os parâmetros foram congelados após a auditoria histórica e não devem ser alterados apenas para melhorar resultados retroativamente.

## Auditoria histórica ampliada

A candidata V3.1 foi testada em janela de até 10 anos, universo ampliado de ativos e horizontes de 5, 10 e 20 pregões.

No horizonte de 20 pregões, a auditoria consolidada registrou:

```text
Eventos:                  300
Acerto:                  61,0%
Retorno médio bruto:     +1,92%
Profit factor bruto:      1,77
Retorno após custo:      +1,72%
Profit factor líquido:    1,67
Excesso médio vs BOVA11: +1,18%
```

O custo hipotético usado foi de 0,20% por operação.

A estabilidade anual também foi analisada, mas os resultados históricos não devem ser tratados como garantia de comportamento futuro.

## Por que shadow mode

A regra foi construída depois de analisar resultados históricos. Mesmo com boa robustez retrospectiva, ainda existe risco de overfitting.

O shadow mode permite criar uma amostra prospectiva com a regra congelada:

```text
ticker
data
motor atual
motor V3.1
estado V3.1
regime do mercado
preço
critérios aprovados
critérios pendentes
```

Essa amostra é mais valiosa para decidir uma futura promoção do que continuar ajustando parâmetros sobre o mesmo histórico.

## Persistência

Tabelas específicas:

```text
shadow_v31
shadow_v31_outcomes
```

O utilitário de diagnóstico é:

```bash
.venv/bin/python scripts/shadow_v31_status.py --limit 20
```

## Critério para promoção

O V3.1 não deve substituir o motor atual apenas por apresentar taxa de acerto maior.

A promoção exige, no mínimo:

- amostra prospectiva suficiente;
- profit factor consistente;
- retorno médio positivo após custos plausíveis;
- resultado não concentrado em poucos tickers;
- estabilidade em regimes distintos;
- avaliação conjunta com um motor de risco estrutural;
- nenhuma degradação operacional da aplicação.

## Motor de risco

Mesmo quando o V3.1 encontra uma oportunidade compradora, a entrada pode ser reprovada pelo risco.

A camada futura de risco deve avaliar:

- suporte e invalidação estrutural;
- ATR;
- distância entre preço e stop;
- resistência e alvo plausível;
- relação risco-retorno real.

O stop não deve ser aproximado artificialmente apenas para encaixar uma regra de risco.

## Limitações

- dados dependem do Yahoo Finance;
- universo histórico pode conter viés de sobrevivência;
- execução intraday não é simulada na auditoria direcional;
- custos reais variam;
- resultados históricos não garantem resultados futuros.
