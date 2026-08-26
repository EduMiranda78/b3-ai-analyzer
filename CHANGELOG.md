# Changelog

Todas as mudanças relevantes do projeto são registradas neste arquivo.

## 2026-08-26

### Motor V3.1 em shadow mode

- adicionado Motor V3.1 congelado em observação paralela;
- contexto de mercado baseado em BOVA11;
- estados internos `COMPRA`, `AGUARDAR`, `EVITAR` e `NEUTRO`;
- sinal comprador exige tendência de alta, rompimento de 20 pregões, confirmação de barra, volume, liquidez, volatilidade e limites de extensão;
- tendência de baixa é tratada como `EVITAR`, sem operação vendida automática;
- criadas tabelas `shadow_v31` e `shadow_v31_outcomes`;
- adicionado `scripts/shadow_v31_status.py`;
- falhas do shadow mode são isoladas e não interrompem a análise principal.

### Resiliência de mercado

- SciPy adicionado às dependências;
- detecção preventiva da disponibilidade de SciPy;
- fallback automático para `repair=False` no `yfinance`;
- nova tentativa sem reparo quando a primeira consulta retorna vazia;
- saneamento de colunas, tipos, duplicidades e preços;
- mensagens de erro deixaram de afirmar que um ticker é inválido quando a origem pode ser a fonte de dados.

### Relatório e interface

- relatório reorganizado para leitura direta por usuário não técnico;
- resumo prático priorizado antes dos indicadores detalhados;
- Home e relatório unificados visualmente;
- Histórico e Backtest passaram a ter controles separados;
- Gemini permanece complementar e não pode alterar o sinal local;
- corrigido fallback de `ATR/preço` para payloads legados e testes.

### Metodologia

- força técnica diferenciada de probabilidade de acerto;
- níveis estruturais preservados no plano de risco;
- alvo não é deslocado apenas para forçar 2R;
- alertas de liquidez adicionados sem alteração oportunista dos pesos do motor atual;
- backtest direcional e auditorias ampliadas usados para avaliar candidatos de motor.

### Documentação

- README reorganizado no padrão visual dos demais projetos;
- adicionados badges e diagrama Mermaid;
- documentação separada de arquitetura, produção, metodologia e Motor V3.1;
- adicionado CI com GitHub Actions;
- removidos arquivos temporários e instruções obsoletas da raiz.

## 2026-07-31

### Consolidação da aplicação principal

- versão azul validada tornou-se a aplicação principal;
- motor técnico local integrado;
- indicadores ampliados;
- fallback local para falhas do Gemini;
- histórico persistente;
- healthcheck e testes adicionados;
- documentação técnica inicial consolidada.

## Notas

O projeto está em evolução. Resultados históricos e métricas de backtest não constituem garantia de desempenho futuro nem recomendação de investimento.
