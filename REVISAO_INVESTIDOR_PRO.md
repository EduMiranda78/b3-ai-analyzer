# Revisão técnica e de investimento — versão aperfeiçoada

## Resumo executivo

A base original é boa: separação por serviços, fallback local quando a IA falha, testes automatizados, cache, histórico SQLite e prompt que proíbe a IA de alterar o sinal.

O principal risco do desenho original estava no motor de decisão: a pontuação era apresentada como "confiança" sem calibração estatística e o plano de risco podia projetar artificialmente um alvo de 2R mesmo quando a resistência/suporte estrutural ficava antes desse nível.

Esta revisão preserva a arquitetura e fortalece o projeto em quatro frentes:

1. integridade do sinal;
2. qualidade do plano de risco;
3. validação histórica;
4. consistência operacional/documental.

## Problemas encontrados e correções

### 1. Relação risco-retorno artificial

**Antes:** quando uma resistência/suporte oferecia menos de 2R, o código deslocava o alvo para completar 2R.

**Risco:** o usuário podia interpretar que existia uma oportunidade estrutural de 2R quando, na verdade, o nível técnico relevante estava mais próximo.

**Agora:** o nível estrutural é preservado. A relação real é exibida e o setup é classificado como `APROVADO`, `ATENÇÃO` ou `FRACO`.

### 2. "Confiança" não era probabilidade

**Antes:** `ALTA`, `MÉDIA` e `BAIXA` eram derivadas apenas do valor absoluto da pontuação.

**Risco:** linguagem probabilística sem backtest/calibração.

**Agora:** a interface chama a métrica de **força técnica**. O score também é normalizado pelo máximo de fatores efetivamente disponíveis.

### 3. SMA 200 incompleta

**Antes:** quando não existiam 200 pregões, a SMA 200 virava zero e era simplesmente ignorada.

**Agora:** o indicador expõe `sma200_disponivel` e o motor gera alerta de histórico insuficiente.

### 4. Volume relativo contaminado pela barra atual

**Antes:** o volume atual era dividido por uma média de 20 períodos que já continha o próprio volume atual.

**Agora:** a média é deslocada em um pregão (`shift(1)`), comparando a barra atual somente com os 20 pregões anteriores.

### 5. Price action insuficiente

Foram adicionados:

- Close Location Value (CLV);
- amplitude da barra em ATR;
- rompimento da máxima/mínima dos 20 pregões anteriores;
- confirmação do rompimento apenas quando o fechamento está forte e a barra tem amplitude relevante.

Isso aproxima o motor de uma leitura de price action sem fingir que um conjunto simples de regras reproduz integralmente a metodologia de Al Brooks.

### 6. Backtest inexistente

Foi criado `services/backtest_service.py`, uma CLI e uma tela `/backtest`.

A avaliação:

- calcula cada sinal apenas com informações disponíveis até a data;
- usa a abertura seguinte como referência de entrada;
- mede o retorno direcional após um horizonte definido;
- registra eventos quando o estado do sinal muda;
- calcula taxa de acerto, retorno médio/mediano e profit factor.

O teste não simula custos, impostos, slippage nem execução intraday; por isso é diagnóstico do sinal, não comprovação de rentabilidade.

### 7. Séries não ajustadas

O download de mercado passou a usar OHLC ajustado e a opção de reparo do `yfinance`, reduzindo distorções causadas por eventos corporativos e alguns erros de unidade nas séries históricas.

### 8. Gemini desatualizado

O modelo padrão foi atualizado para `gemini-3.6-flash`. A configuração de raciocínio agora diferencia a série Gemini 3 (`thinking_level`) da série 2.5 (`thinking_budget`), mantendo compatibilidade via `.env`.

### 9. Telegram podia soar como ordem

A mensagem agora usa "viés técnico", informa se o plano 2R foi aprovado e inclui aviso de caráter informativo.

### 10. Documentação e dependências

O README antigo descrevia recursos que não correspondiam ao código e mencionava `pandas-ta`, embora os indicadores já fossem calculados manualmente.

O README foi refeito e `requirements.txt` passou a listar apenas dependências diretas utilizadas pela aplicação.

## O que ainda falta antes de confiar no motor

### Prioridade alta

- backtest em centenas de ativos, incluindo ativos que deixaram de existir para reduzir survivorship bias;
- custos operacionais e slippage;
- walk-forward / out-of-sample;
- avaliação por regimes de mercado;
- benchmark contra regras simples;
- dimensionamento de posição baseado em risco.

### Prioridade média

- filtro de liquidez;
- gráfico de preço com sinais e níveis;
- métricas por ticker e por setor;
- separação entre "viés técnico" e "gatilho de entrada";
- detecção de trading range versus tendência;
- padrões de pullback e second entry inspirados em price action.

### Fundamentalista

A análise fundamentalista deve ser uma camada separada, com dados auditáveis e datas de referência explícitas. Não recomendo misturar múltiplos/fundamentos diretamente na pontuação técnica antes de validar cada componente separadamente.

## Validação realizada nesta revisão

- compilação de sintaxe de `main.py`, serviços, scripts e testes: **OK**;
- 9 testes puros de indicadores, sinal e backtest executados diretamente: **9/9 passaram**;
- busca por marcadores de conflito, `debug=True` e segredos hardcoded: **nenhum encontrado**;
- suíte Flask completa: **não executada neste sandbox**, porque as dependências Flask/Google/yfinance não estão pré-instaladas e o ambiente não permite baixar pacotes da internet.

No ambiente local do projeto, execute:

```bash
pip install -r requirements-dev.txt
python -m pytest
bash scripts/check.sh
```

## Critério de sucesso sugerido

Antes de alterar pesos para "melhorar" a taxa de acerto, defina métricas por amostra fora do treino. Um motor útil não precisa maximizar acerto; precisa demonstrar expectativa positiva robusta após custos e estabilidade em diferentes regimes.

---

Este documento é uma revisão de engenharia e metodologia. Não constitui recomendação de investimento.
