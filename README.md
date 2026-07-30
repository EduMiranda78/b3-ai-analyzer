# Analisador de Ativos com IA

Aplicação web em Python e Flask para gerar relatórios de análise de ativos negociados na B3.

O sistema consulta dados de mercado pelo Yahoo Finance, calcula indicadores técnicos com `pandas-ta` e envia os dados consolidados ao Google Gemini para produzir um relatório em português. O resultado pode incluir uma sinalização resumida enviada ao Telegram.

> Projeto em desenvolvimento. Os relatórios são informativos e não constituem recomendação de investimento.

## Funcionalidades

- Consulta de ações e fundos imobiliários da B3 por ticker.
- Inclusão automática do sufixo `.SA` quando ele não for informado.
- Histórico de preços dos últimos três meses.
- Cache local dos dados por 15 minutos.
- Cálculo de indicadores técnicos:
  - SMA 9 e SMA 21
  - EMA 9 e EMA 21
  - MACD 12, 26 e 9
  - RSI 14
  - volatilidade anualizada de 20 períodos
- Coleta de informações da empresa, preço atual, preço-alvo, recomendações e notícias disponíveis.
- Geração de relatório com Google Gemini.
- Interface web responsiva para envio do ticker.
- Envio opcional da sinalização final para um chat do Telegram.
- Execução local com Flask ou em produção com Gunicorn e WSGI.

## Tecnologias

- Python 3
- Flask
- Gunicorn
- Google Gemini API
- yfinance
- pandas
- pandas-ta
- markdown2
- python-dotenv
- HTML, CSS e JavaScript

## Estrutura principal

```text
Analisador/
├── main.py
├── wsgi.py
├── gemini_analyzer.py
├── verify_models.py
├── prompt_analise.txt
├── prompt_analise_original.txt
├── requirements.txt
├── .env.example
├── .gitignore
└── templates/
    ├── index.html
    └── relatorio.html
```

## Requisitos

- Python 3.10 ou superior
- Conta e chave de API do Google Gemini
- Acesso à internet para consultar o Yahoo Finance e o Gemini
- Bot e chat do Telegram, somente para quem quiser receber notificações

## Instalação

Clone o repositório:

```bash
git clone https://github.com/EduMiranda78/Analisador.git
cd Analisador
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuração

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Preencha as variáveis:

```env
GOOGLE_API_KEY=sua_chave_da_api_google
TELEGRAM_BOT_TOKEN=token_do_bot_opcional
TELEGRAM_CHAT_ID=id_do_chat_opcional
```

A variável `GOOGLE_API_KEY` é obrigatória. As variáveis do Telegram são opcionais.

Nunca publique o arquivo `.env` nem chaves de API no GitHub.

## Execução local

```bash
python main.py
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:5000
```

## Execução com Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

Para uso público, execute atrás de um proxy reverso, como Nginx, com HTTPS e sem o modo de depuração do Flask.

## Como usar

1. Abra a página inicial no navegador.
2. Digite um ticker da B3, como `PETR4`, `VALE3` ou `MXRF11`.
3. Clique em **Analisar**.
4. Aguarde a consulta dos dados e a geração do relatório.
5. Revise o relatório considerando a data, a fonte dos dados e as limitações descritas abaixo.

## Verificação dos modelos Gemini

O arquivo `verify_models.py` pode ser usado para listar os modelos disponíveis que suportam geração de conteúdo:

```bash
python verify_models.py
```

## Fontes e limitações

- As cotações e informações são obtidas por meio da biblioteca `yfinance`.
- A disponibilidade, atualização e precisão dos dados dependem das fontes consultadas pelo Yahoo Finance.
- Notícias, recomendações e dados fundamentalistas podem não estar disponíveis para todos os ativos.
- O conteúdo produzido pelo Gemini pode conter erros ou interpretações incompletas.
- Nenhuma saída deve ser usada isoladamente para decidir uma compra ou venda.

## Segurança

- Não envie `.env`, tokens ou chaves de API para o repositório.
- Use variáveis de ambiente no servidor.
- Desative o modo debug em produção.
- Restrinja o acesso à aplicação quando ela estiver exposta na internet.
- Atualize as dependências e revise vulnerabilidades periodicamente.

## Melhorias previstas

- Testes automatizados das funções de cálculo e formatação.
- Tratamento de erros mais específico.
- Configuração separada para desenvolvimento e produção.
- Validação mais rigorosa dos tickers recebidos.
- Histórico persistente das análises.
- Gráficos de preço e indicadores.
- Containerização com Docker.
- Pipeline de integração contínua.

## Autor

Desenvolvido por [Eduardo Miranda](https://github.com/EduMiranda78).

## Licença

Este repositório ainda não possui uma licença definida. Até que uma licença seja adicionada, o código permanece protegido pelos direitos autorais do autor.
