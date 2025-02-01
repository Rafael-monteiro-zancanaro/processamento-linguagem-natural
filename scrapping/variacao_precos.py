import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import csv
import re

empresa_para_ticker = {
    "itau-unibanco-itub4": "ITUB4.SA",
    "banco-do-brasil-bbas3": "BBAS3.SA",
    "bradesco-bbdc4": "BBDC4.SA",
    "btgp-banco-bpac11": "BPAC11.SA"
}

def obter_ticker(empresa):
    return empresa_para_ticker.get(empresa, "Ticker não encontrado")

def padronizar_data(data):
    try:
        data_formatada = datetime.strptime(data, "%d/%m/%Y %Hh%M")

        data_saida = data_formatada.strftime("%Y-%m-%d")   

        data = data_saida
    except ValueError as erro1:
        print(f"Erro: {erro1}")
        try:
            data_formatada = datetime.strptime(data, "%d %b %Y %Hh%M")

            data_saida = data_formatada.strftime("%Y-%m-%d")

            data = data_saida
        except ValueError as erro2:
            data_saida = datetime.today().strftime("%Y-%m-%d")

            data = data_saida

    return data_saida

def coleta_historico_acoes(ticker, start_date, end_date):
    try:
        print(start_date, end_date)
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        
        if stock_data.empty:
            print(f"Nenhum dado disponível para o ticker {ticker} no intervalo de {start_date} a {end_date}.")
            return None

        stock_data['Daily Change (%)'] = ((stock_data['High'] - stock_data['Low']) / stock_data['High']) * 100
        stock_data = stock_data[['Open', 'Close', 'Daily Change (%)']]
        print(stock_data)
        return stock_data
    except Exception as e:
        print(f"Erro ao baixar dados para {ticker}: {e}")
        return None

def coleta_analise(news_date, days=2):
    news_date_obj = datetime.strptime(news_date, '%Y-%m-%d')
    start_date = news_date_obj - timedelta(days=days)
    end_date = news_date_obj + timedelta(days=days)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def variacao_por_noticia(df_noticias):
    resultado = []
    df_noticias['TICKER'] = df_noticias['EMPRESA'].apply(obter_ticker)

    with open("dados_historicos.csv", mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["EMPRESA", "DATA", "TICKER", "VARIACAO"])

        for empresa, data, ticker in zip(df_noticias['EMPRESA'], df_noticias['DATA'], df_noticias['TICKER']):
            if data != "Dados não encontrados":
                news_date = str(data)
            else:
                continue 
            
            start_date, end_date = coleta_analise(news_date, days=2)
            stock_data = coleta_historico_acoes(ticker, start_date, end_date)

            if stock_data is not None:
                resultado.append(f"Dados históricos de {ticker} para o intervalo de {start_date} a {end_date}:")
                for index, row in stock_data.iterrows():
                    dailyC = row['Daily Change (%)']
                    match = re.search(r"Ticker\s+([\d.]+)", str(dailyC))
                    if match:
                        variacao = float(match.group(1))
                    else:
                        variacao = 0
                    writer.writerow([empresa, data, ticker, variacao])
            else:
                writer.writerow([empresa, data, ticker, data, '', '', ''])

    print("Dados salvos em 'dados_historicos.txt'.")

arquivo_csv = "noticias_empresas.csv"

df = pd.read_csv(arquivo_csv, delimiter = ';')
df_selecionado = df[['EMPRESA', 'DATA']].copy()

df_selecionado['DATA'] = df_selecionado['DATA'].apply(padronizar_data)

variacao_por_noticia(df_selecionado)