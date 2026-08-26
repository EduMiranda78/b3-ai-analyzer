# B3 AI Analyzer

Aplicação web em Python/Flask para análise técnica de ações e FIIs da B3.

O projeto separa o **motor quantitativo** da camada de IA: o sinal é calculado localmente a partir dos dados de mercado; o Gemini apenas explica os dados e o sinal já definidos. Se a API de IA estiver indisponível, um relatório local é gerado automaticamente.

> Uso educacional e informativo. Não constitui recomendação de investimento.

## O que o projeto faz

- Consulta cotações diárias com `yfinance`.
- Aceita tickers da B3 com ou sem o sufixo `.SA`.
- Mantém cache de mercado por 15 minutos.
- Calcula indicadores e contexto técnico:
  - EMA 9 e EMA 21;
  - SMA 50 e SMA 200;
  - RSI 14;
  - MACD 12/26/9;
  - ATR 14;
  - volatilidade anualizada de 20 pregões;
  - retorno de 20 e 60 pregões;
  - suporte e resistência dos 20 pregões anteriores;
  - volume relativo aos 20 pregões anteriores;
  - Close Location Value (CLV);
  - amplitude da barra em ATR;
  - rompimento de máxima/mínima de 20 pregões.
- Calcula sinal local: `COMPRA`, `VENDA` ou `NEUTRO`.
- Diferencia **força técnica** de probabilidade estatística de acerto.
- Calcula stop, alvo, relação risco-retorno e qualidade do plano.
- Não desloca um alvo estrutural apenas para forçar uma relação 2:1.
- Persiste as análises em SQLite.
- Compara cada análise com a anterior do mesmo ticker.
- Envia sinalização opcional ao Telegram.
- Possui backtest direcional de 5 anos pela interface web e por CLI.
- Usa Gemini para a explicação textual, com fallback local.

## Arquitetura

```text
.
├── main.py
├── wsgi.py
├── prompt_analise.txt
├── services/
│   ├── backtest_service.py
│   ├── cache_service.py
│   ├── gemini_service.py
│   ├── history_service.py
│   ├── indicators_service.py
│   ├── market_service.py
│   ├── report_service.py
│   ├── signal_service.py
│   └── telegram_service.py
├── scripts/
│   ├── backtest.py
│   └── check.sh
├── templates/
│   ├── backtest.html
│   ├── historico.html
│   ├── historico_detalhe.html
│   ├── index.html
│   └── relatorio.html
├── static/
└── tests/
```

## Como o sinal é formado

O motor usa uma pontuação de confluência. Entre os fatores considerados estão:

1. alinhamento do preço com EMA 9 e EMA 21;
2. posição em relação à SMA 50;
3. posição em relação à SMA 200, quando há histórico suficiente;
4. histograma do MACD;
5. faixa do RSI;
6. retorno de 20 pregões;
7. confirmação por volume;
8. rompimento de 20 pregões com fechamento forte e amplitude relevante.

A pontuação absoluta é normalizada pelo máximo disponível. A classificação exibida como `ALTA`, `MÉDIA` ou `BAIXA` significa **força/confluência técnica**, não uma probabilidade de acerto.

### Plano de risco

Quando existe sinal direcional, o sistema calcula um stop técnico com base em ATR e estrutura de preço.

Se houver resistência/suporte válido, esse nível é preservado como alvo. Se o alvo estrutural oferecer menos de 2R, o sistema mostra a relação real e marca o setup como não aprovado. Um alvo de 2R só é projetado quando não há nível estrutural válido na direção do movimento, e isso é sinalizado ao usuário.

## Backtest

A tela `/backtest` baixa 5 anos de dados e avalia o motor sem usar informações futuras na criação do sinal.

Metodologia padrão:

- `warmup`: 220 pregões;
- sinal calculado no fechamento do pregão `t`;
- entrada de referência na abertura de `t+1`;
- saída no fechamento após 10 pregões;
- um novo evento é registrado quando o estado do sinal muda;
- métricas: quantidade de sinais, taxa de acerto, retorno direcional médio/mediano e profit factor.

O teste mede **capacidade direcional**. Ele não inclui custos, impostos, slippage, liquidez nem a execução intraday do stop/alvo. Portanto, não deve ser interpretado como rentabilidade líquida de uma estratégia.

Também é possível executar:

```bash
python scripts/backtest.py PETR4
python scripts/backtest.py VALE3 --period 10y --horizon 20
python scripts/backtest.py ITUB4 --json
```

## Instalação

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Para desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

## Configuração

Copie o exemplo:

```bash
cp .env.example .env
```

Variáveis principais:

```env
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-3.6-flash

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

A chave do Gemini é opcional para o funcionamento do motor técnico. Sem ela, a aplicação usa o relatório local.

## Execução

Desenvolvimento local:

```bash
python main.py
```

Produção com Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

A aplicação fica disponível, por padrão, em:

```text
http://127.0.0.1:5000
```

## Testes

```bash
python -m pytest
```

Ou:

```bash
bash scripts/check.sh
```

## Limitações importantes

- `yfinance` é uma camada de acesso a dados do Yahoo Finance; disponibilidade e qualidade podem variar.
- O sistema trabalha principalmente com dados diários e não modela microestrutura ou execução intraday.
- O score técnico ainda precisa ser calibrado em uma amostra ampla de ativos e regimes.
- Backtest histórico pode sofrer seleção de universo, mudanças de composição e outros vieses se for usado de forma ingênua.
- A relação risco-retorno não substitui dimensionamento de posição.
- O relatório da IA não altera o sinal calculado localmente.
- Resultados passados não garantem resultados futuros.

## Próximas evoluções recomendadas

1. backtest em universo amplo da B3, com custos e slippage;
2. walk-forward / out-of-sample para calibrar pesos e limiares;
3. controle de liquidez e tamanho de posição;
4. benchmark contra buy-and-hold e contra regras simples;
5. testes de robustez por regime (alta, baixa e lateral);
6. autenticação/rate limiting antes de exposição pública;
7. gráficos de preço, níveis e sinais;
8. camada fundamentalista separada da análise técnica.

## Licença

Consulte o arquivo `LICENSE`.

## Produção e resiliência da fonte de mercado

A coleta usa `yfinance` com dados ajustados. O modo de reparo é ativado quando SciPy está disponível. Se a dependência não estiver presente ou se a primeira consulta com reparo retornar vazia, o serviço tenta novamente sem reparo em vez de rotular automaticamente o ticker como inválido.

Em produção, as variáveis são normalmente carregadas pelo `EnvironmentFile` do systemd. O serviço não depende da presença de um `.env` dentro do repositório.

## Princípio do relatório

O sinal é calculado pelo motor local. A IA só explica o resultado e não pode alterar `COMPRA`, `VENDA` ou `NEUTRO`. A interface prioriza um resumo em linguagem simples e deixa indicadores detalhados em uma seção secundária.

## Motor V3.1 em shadow mode

A partir de 26/08/2026, o projeto inclui o Motor V3.1 em observação paralela.
Ele não substitui o sinal visível atual nesta fase.

A versão V3.1 foi congelada após uma auditoria histórica ampliada. No universo testado,
o gatilho comprador de rompimento confirmado apresentou 300 eventos. No horizonte de
20 pregões, a auditoria registrou 61,0% de acerto, profit factor bruto de 1,77 e profit
factor de 1,67 após um custo hipotético total de 0,20% por operação. Esses números são
históricos e não garantem comportamento futuro.

O shadow mode grava, sem interferir na resposta principal:

- sinal do motor atual;
- sinal V3.1;
- estado V3.1: COMPRA, AGUARDAR, EVITAR ou NEUTRO;
- regime do BOVA11;
- preço e data de mercado;
- critérios aprovados e pendentes.

A consulta principal continua funcionando mesmo que a avaliação V3.1 falhe ou o benchmark
BOVA11 esteja temporariamente indisponível.

Para ver os registros coletados:

```bash
python3 scripts/shadow_v31_status.py --limit 20
```

Em produção, use o Python do ambiente virtual:

```bash
.venv/bin/python scripts/shadow_v31_status.py --limit 20
```

Para desativar a observação paralela sem remover código:

```text
SHADOW_V31_ENABLED=0
```
