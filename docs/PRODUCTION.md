# Produção

## Topologia atual

A aplicação é executada com Gunicorn sob `systemd`.

```text
systemd
  ↓
b3-ai-analyzer.service
  ↓
Gunicorn gthread
  ↓
Flask / wsgi:app
  ↓
porta 8020
```

O serviço de produção usa o diretório:

```text
/home/eduardo/b3-ai-analyzer
```

O ambiente virtual fica em:

```text
/home/eduardo/b3-ai-analyzer/.venv
```

As variáveis de ambiente de produção são carregadas pelo `EnvironmentFile` do systemd, atualmente `/etc/b3-ai-analyzer.env`. O repositório não depende de um `.env` local para funcionar em produção.

## Gunicorn

Configuração validada na VPS:

```text
workers: 1
worker class: gthread
threads: 4
timeout: 180s
graceful timeout: 30s
keep alive: 5s
bind: 0.0.0.0:8020
```

## Endpoints de validação

Depois de qualquer mudança:

```bash
curl -fsS http://127.0.0.1:8020/
curl -fsS http://127.0.0.1:8020/health
curl -fsS http://127.0.0.1:8020/backtest
```

Todos devem responder sem erro. O endpoint `/health` é a verificação mínima do serviço.

## Banco

Banco padrão:

```text
/home/eduardo/b3-ai-analyzer/instance/analisador.db
```

O banco real nunca deve ser versionado. Antes de alteração de schema ou deploy relevante, faça backup explícito.

## Deploy seguro

Princípios adotados:

1. confirmar que a produção atual está saudável;
2. validar dependências e sintaxe antes de alterar o runtime;
3. executar a suíte de testes;
4. testar fontes de mercado reais;
5. fazer smoke test em porta temporária quando possível;
6. criar backup de código e banco;
7. aplicar código sem substituir `.venv`, `.git` ou banco;
8. reiniciar o serviço;
9. validar Home, Health e Backtest;
10. somente depois atualizar o GitHub.

### Importante sobre o virtualenv

Não mova um ambiente virtual pronto entre diretórios. Scripts dentro de `.venv/bin/` podem conter shebangs absolutos e deixar de funcionar após a mudança de caminho.

A estratégia preferida é manter `.venv` no diretório definitivo e atualizar apenas código e dependências.

## Git

O remote de produção deve usar SSH:

```bash
git remote set-url origin git@github.com:EduMiranda78/b3-ai-analyzer.git
```

Validação:

```bash
git remote -v
ssh -T git@github.com || true
git status -sb
```

Não use autenticação por senha para `git push` no GitHub.

## Motor V3.1 em shadow mode

O Motor V3.1 pode ser desativado sem remoção de código:

```env
SHADOW_V31_ENABLED=0
```

Para consultar os registros:

```bash
.venv/bin/python scripts/shadow_v31_status.py --limit 20
```

Uma falha do shadow mode deve ser isolada e não interromper a análise principal.

## Logs

```bash
sudo journalctl -u b3-ai-analyzer.service -n 100 --no-pager
```

Para acompanhar em tempo real:

```bash
sudo journalctl -u b3-ai-analyzer.service -f
```

Nunca publique logs que contenham tokens, chaves ou informações sensíveis.

## Checklist pós-deploy

- serviço `active (running)`;
- Home HTTP 200;
- Health HTTP 200;
- Backtest HTTP 200;
- consulta real de pelo menos um ticker válido;
- banco preservado;
- nenhuma exceção nova nos logs;
- `git status -sb` coerente;
- `HEAD` e `origin/main` alinhados quando o push fizer parte do deploy.
