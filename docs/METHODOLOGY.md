# Metodologia e risco

## Princípios

O B3 AI Analyzer trata análise técnica como um sistema de evidências, não como previsão certa.

Os principais princípios são:

- força técnica não é probabilidade calibrada;
- mais indicadores concordando não significa automaticamente melhor entrada;
- indicadores correlacionados não devem ser interpretados como confirmações independentes;
- direção do ativo e qualidade do ponto de entrada são conceitos diferentes;
- risco estrutural não deve ser manipulado para fazer um setup parecer melhor;
- qualquer alteração relevante no motor deve ser testada fora da amostra usada para concebê-la.

## Motor atual

O motor visível usa fatores como:

- EMA 9 e EMA 21;
- SMA 50 e SMA 200;
- MACD;
- RSI;
- retorno de 20 pregões;
- volume relativo;
- rompimento com confirmação por fechamento e amplitude.

A classificação de força representa confluência técnica. Não é uma chance percentual de acerto.

## Suporte, resistência e lookahead

Suporte, resistência e médias de volume são calculados a partir de pregões anteriores, evitando contaminar a leitura com a própria barra usada para gerar o sinal.

Esse cuidado também se aplica ao backtest: o sinal de um pregão deve utilizar somente dados disponíveis até aquele momento.

## Plano de risco

Quando existe sinal direcional, o sistema calcula referência, stop e alvo.

A regra metodológica central é:

> um nível estrutural real não deve ser deslocado apenas para fabricar uma relação risco-retorno desejada.

Se uma resistência válida oferece menos de 2R para uma compra, a relação real deve ser exibida e o setup pode ser reprovado. Um alvo projetado só faz sentido quando não existe nível estrutural apropriado e deve ser explicitamente identificado como projeção.

Da mesma forma, um stop estrutural distante não deve ser artificialmente aproximado. Se o risco necessário para respeitar a estrutura for excessivo, a entrada deve ser reprovada.

## Backtest

A avaliação histórica padrão segue esta sequência:

1. utiliza uma janela de aquecimento;
2. calcula o sinal no fechamento do pregão `t`;
3. usa a abertura de `t+1` como referência de entrada;
4. mede o retorno após horizonte definido;
5. registra um novo evento quando o estado do sinal muda.

Métricas principais:

- número de eventos;
- taxa de acerto;
- retorno médio e mediano;
- profit factor;
- comparação por direção e horizonte.

## O que o backtest não prova

A avaliação direcional não simula integralmente:

- slippage;
- impostos;
- custos específicos de execução;
- preenchimento intraday de stop e alvo;
- restrições de liquidez por tamanho de posição;
- aluguel para venda a descoberto;
- alterações históricas de composição do universo.

Por isso, um backtest positivo é evidência para continuar investigando, não prova automática de rentabilidade futura.

## Viés de sobrevivência

Testar apenas empresas atualmente negociadas pode favorecer artificialmente resultados históricos. Uma validação mais forte deve incluir, quando possível, ativos que deixaram de existir, mudaram de ticker ou saíram do universo analisado.

## Regimes de mercado

Um motor robusto deve ser avaliado separadamente em:

- tendência de alta;
- tendência de baixa;
- mercado lateral;
- volatilidade elevada;
- volatilidade comprimida.

O Motor V3.1 começou a incorporar esse princípio usando BOVA11 como contexto de mercado.

## Força relativa

Comparar o ativo com um benchmark ajuda a diferenciar alta absoluta de desempenho realmente superior ao mercado.

Exemplo conceitual: uma ação que sobe 4% enquanto o mercado sobe 8% está em situação diferente de uma ação que sobe 4% enquanto o mercado cai 2%.

## Fundamentalista

Dados fundamentalistas devem permanecer em camada separada da pontuação técnica até que exista fonte auditável, data de referência clara e validação independente de cada fator.

Misturar múltiplos, notícias ou fundamentos diretamente no score técnico sem rastreabilidade dificulta saber de onde vem a vantagem do sistema.

## Critério de evolução

Antes de promover uma nova versão do motor, avaliar:

- desempenho bruto e após custos;
- treino, validação e teste;
- estabilidade anual;
- resultado por ticker e setor;
- concentração de ganhos;
- comportamento por regime;
- amostra prospectiva;
- simplicidade da regra.

A preferência é por um motor explicável e robusto, não por um motor com maior quantidade de indicadores.

---

Este documento descreve princípios de engenharia e validação quantitativa. Não constitui recomendação de investimento.
