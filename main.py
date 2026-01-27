import os
import requests
import google.generativeai as genai
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask, render_template, request
from flask import jsonify
from datetime import datetime, timedelta
import markdown2
import re
import threading
from dotenv import load_dotenv, find_dotenv
import logging
#from telegram import Bot
#from telegram.error import TelegramError
load_dotenv(find_dotenv())

# Configuração Telegram (já usa dotenv)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
#bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# Inicializa o bot globalmente

app = Flask(__name__)

app.debug = True

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Erro ao configurar a API do Gemini: {e}")

cache = {}
CACHE_DURATION = timedelta(minutes=15)
cache_lock = threading.Lock()

def is_cache_valid(ticker):
    with cache_lock:
        if ticker not in cache:
            return False
        if datetime.now() - cache[ticker]['timestamp'] > CACHE_DURATION:
            return False
        return True

def buscar_dados_ativo(ticker):
    if is_cache_valid(ticker):
        return cache[ticker]['data'], None
    try:
        ativo = yf.Ticker(ticker)
        hist = ativo.history(period="3mo")
        if hist.empty:
            return None, "Ticker inválido ou sem dados"
        info = ativo.info
        recomendacoes = getattr(ativo, 'recommendations', pd.DataFrame())
        noticias = getattr(ativo, 'news', [])[:3]

        dados = {
            "historico": hist,
            "info": info,
            "recomendacoes": recomendacoes,
            "noticias": noticias
        }

        with cache_lock:
            cache[ticker] = {
                'data': dados,
                'timestamp': datetime.now()
            }
        return dados, None
    except Exception as e:
        return None, f"Erro na API Yahoo Finance: {e}"

def calcular_indicadores(df_historico):
    try:
        df = df_historico.copy()
        df.ta.sma(length=9, append=True)
        df.ta.sma(length=21, append=True)
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=21, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.rsi(length=14, append=True)
        df['returns'] = df['Close'].pct_change()
        df['volatilidade_20d'] = df['returns'].rolling(window=20).std() * (252**0.5)
        return df.iloc[-1]
    except:
        return pd.Series({'Close': 0})

def enviar_para_telegram(ticker, sinalizacao_final):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    
    if not token or not chat_id:
        print("❌ .env sem TELEGRAM vars")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    mensagem = f"📈 *Nova Análise*\n\n`Ticker`: {ticker}\n`Sinalização Final`: {sinalizacao_final}"
    
    try:
        response = requests.post(url, data={
            'chat_id': chat_id,
            'text': mensagem,
            'parse_mode': 'Markdown'
        }, timeout=10)
        
        print(f"✅ Telegram HTTP: {ticker} - {sinalizacao_final} (status: {response.status_code})")
        print(f"📱 RESP: {response.json().get('ok', False)}")
        
    except Exception as e:
        print(f"❌ Telegram erro: {e}")

def formatar_dados_para_ia(ticker, dados_ativo, indicadores):
    info = dados_ativo.get("info", {})
    recom = dados_ativo.get("recomendacoes")
    noticias = dados_ativo.get("noticias", [])

    nome_empresa = info.get('longName', 'N/A')
    preco_atual = info.get('currentPrice', indicadores.get('Close', 0))
    variacao_dia = ((preco_atual / info.get('previousClose', 1)) - 1) if info.get('previousClose') else 0

    recomendacao_geral = info.get('recommendationKey', 'N/A')
    preco_alvo_medio = info.get('targetMeanPrice', 'N/A')

    consenso = "N/A"
    if recom is not None and not recom.empty and 'To Grade' in recom.columns:
        consenso_df = recom['To Grade'].value_counts().reset_index()
        consenso_df.columns = ['Recomendacao', 'Contagem']
        consenso = ", ".join([f"{int(row['Contagem'])} {row['Recomendacao']}" for _, row in consenso_df.iterrows()])

    titulos_noticias = "\n".join([f"- {item.get('title', 'N/A')}" for item in noticias[:3]])
    if not titulos_noticias.strip():
        titulos_noticias = "- Sem notícias recentes"

    # CORREÇÃO: preço-alvo formatado corretamente
    if isinstance(preco_alvo_medio, (int, float)):
        preco_str = f"{preco_alvo_medio:.2f}"
    else:
        preco_str = 'N/A'

    return f"""Ticker: {ticker}
Empresa: {nome_empresa}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Preço Atual: R$ {preco_atual:.2f}
Variação Dia: {variacao_dia:+.2%}
SMA9: {indicadores.get('SMA_9', 0):.2f} | SMA21: {indicadores.get('SMA_21', 0):.2f}
RSI14: {indicadores.get('RSI_14', 0):.1f} | MACD: {indicadores.get('MACD_12_26_9', 0):.4f}
Recomendação: {recomendacao_geral.upper()}
Preço-Alvo Médio: R$ {preco_str}
Consenso: {consenso}
Volatilidade 20d: {indicadores.get('volatilidade_20d', 0):.1%}
Notícias: {titulos_noticias}"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    ticker = request.form['ticker'].strip().upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'

    dados_ativo, erro = buscar_dados_ativo(ticker)
    if erro:
        return render_template('relatorio.html', error=f"Erro: {erro}")

    indicadores = calcular_indicadores(dados_ativo["historico"])
    dados_formatados = formatar_dados_para_ia(ticker, dados_ativo, indicadores)

    try:
        with open('prompt_analise.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        prompt_final = prompt_template.format(dados_do_ativo=dados_formatados)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt_final)

        report_text = response.text
        report_text = re.sub(r'^(\d+\)\s+.*?$)', r'<h2>\1</h2>', report_text, flags=re.MULTILINE)
        report_text = report_text.replace('---------------------------------', '<hr>')
        relatorio_html = markdown2.markdown(report_text)

        # 🔥 EXTRAI E ENVIA PARA TELEGRAM 
        sinal_final_match = re.search(r'8\)\s*SINALIZAÇÃO\s*FINAL.*?([A-ZÇÂÕÚ]+)\.', report_text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        sinalizacao_final = sinal_final_match.group(1).upper() if sinal_final_match else "SEM SINAL"
        print(f"🔍 SINAL DETECTADO: '{sinalizacao_final}'")
        
        enviar_para_telegram(ticker, sinalizacao_final)  # ← ESTA LINHA FALTAVA!!!

        return render_template('relatorio.html', relatorio=relatorio_html)


    except FileNotFoundError:
        return render_template('relatorio.html', error="Arquivo 'prompt_analise.txt' não encontrado.")
    except Exception as e:
        return render_template('relatorio.html', error=f"Erro ao se comunicar com a API do Gemini: {e}")


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=True)
