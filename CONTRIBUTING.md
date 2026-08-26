# Como contribuir

Contribuições são bem-vindas quando preservam a separação entre motor quantitativo, camada de IA e interface.

## Antes de abrir uma Issue

1. verifique se o problema já foi relatado;
2. confirme que consegue reproduzi-lo;
3. remova chaves, tokens, senhas e dados pessoais;
4. informe Python, sistema operacional e contexto relevante;
5. descreva resultado esperado e resultado observado.

## Relato de erro

Inclua, quando aplicável:

- ticker utilizado;
- passos para reprodução;
- mensagem de erro completa;
- rota ou componente afetado;
- versão do Python;
- commit ou branch;
- logs sanitizados.

Nunca publique:

- `GOOGLE_API_KEY`;
- `TELEGRAM_BOT_TOKEN`;
- `TELEGRAM_CHAT_ID`;
- conteúdo de `.env`;
- banco SQLite real;
- credenciais de servidor.

## Mudanças no motor de mercado

Alterações em score, filtros, gatilhos ou risco precisam de justificativa metodológica e testes.

Evite ajustar parâmetros apenas para melhorar um backtest já observado. Prefira:

- hipótese explícita;
- teste fora da amostra;
- comparação por regime;
- custos plausíveis;
- amostra prospectiva quando possível.

Consulte [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) e [`docs/MOTOR_V31.md`](docs/MOTOR_V31.md).

## Fluxo recomendado

1. faça fork do repositório;
2. crie uma branch objetiva;
3. faça mudanças pequenas e rastreáveis;
4. atualize testes e documentação;
5. execute as verificações locais;
6. abra Pull Request explicando motivação, impacto e validação.

Exemplos de branches:

```text
feat/grafico-preco
fix/fonte-mercado
docs/arquitetura
research/motor-v32
```

## Validação local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
bash scripts/check.sh
```

## Pull Requests

Um PR deve informar:

- problema resolvido;
- arquivos principais alterados;
- testes executados;
- impacto esperado no motor e na produção;
- necessidade de migração, nova variável de ambiente ou mudança operacional.

Mudanças que alterem o comportamento de investimento devem deixar claro se afetam o motor visível, o shadow mode ou apenas a apresentação.
