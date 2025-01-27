from scrapping.scrapping import digest_news
from scrapping.variacao_precos import variacao_por_noticia
from word_processing.word_sanitizer import sanitize_text
from mood_analysis.mood_analyser import analise_mood
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    print("Iniciando pipeline...")
    
    # Coleta e processamento de notícias
    digest_news()

    dadosHistDict = {}

    # Carregar dados históricos
    with open("./dados_historicos.csv", "r", encoding="utf-8") as dadosFile:
        dadosHist = dadosFile.readlines()[1:]  # Ignorar cabeçalho

        for line in dadosHist:
            empresa = line.split(",")[0]
            data = line.split(",")[1]
            variacao = float(line.split(",")[3])  # Converter para float
            
            if empresa not in dadosHistDict:
                dadosHistDict[empresa] = {}

            dadosHistDict[empresa][data] = variacao

    # Dados para gráficos por empresa
    empresas_sentimentos_variacao = {}

    with open("./noticias_empresas.csv", "r", encoding="utf-8") as file:
        print("---------------------------------------------------------------\n")
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            empresa = row['EMPRESA']
            titulo = row['TÍTULO']
            data = row['DATA']
            noticia = row['TEXTO']
        
            texto_sanitizado = " ".join(sanitize_text(noticia))
            sentimentos = analise_mood(texto_sanitizado)
            sentimento_score = sentimentos[0]['score']  # Usar o primeiro sentimento analisado

            dataNoticia = datetime.strptime(data, "%d/%m/%Y %Hh%M")
            dataNoticiaStr = dataNoticia.strftime("%Y-%m-%d")

            # Coletar variações de preço
            variacao_no_dia = dadosHistDict.get(empresa, {}).get(dataNoticiaStr, 0)
            variacao_um_dia_antes = dadosHistDict.get(empresa, {}).get((dataNoticia - timedelta(days=1)).strftime("%Y-%m-%d"), 0)
            variacao_um_dia_depois = dadosHistDict.get(empresa, {}).get((dataNoticia + timedelta(days=1)).strftime("%Y-%m-%d"), 0)
            variacao_dois_dias_antes = dadosHistDict.get(empresa, {}).get((dataNoticia - timedelta(days=2)).strftime("%Y-%m-%d"), 0)
            variacao_dois_dias_depois = dadosHistDict.get(empresa, {}).get((dataNoticia + timedelta(days=2)).strftime("%Y-%m-%d"), 0)

            # Inicializar estrutura para a empresa, se necessário
            if empresa not in empresas_sentimentos_variacao:
                empresas_sentimentos_variacao[empresa] = {
                    "no_dia": [],
                    "um_dia_antes": [],
                    "um_dia_depois": [],
                    "dois_dias_antes_e_depois": []
                }

            # Organizar dados para gráficos por empresa
            empresas_sentimentos_variacao[empresa]["no_dia"].append((sentimento_score, variacao_no_dia))
            empresas_sentimentos_variacao[empresa]["um_dia_antes"].append((sentimento_score, variacao_um_dia_antes))
            empresas_sentimentos_variacao[empresa]["um_dia_depois"].append((sentimento_score, variacao_um_dia_depois))
            empresas_sentimentos_variacao[empresa]["dois_dias_antes_e_depois"].append(
                (sentimento_score, (variacao_dois_dias_antes + variacao_dois_dias_depois) / 2)
            )
            
            print(f'Empresa: {empresa}.\n\t Noticia: {titulo}.\n\t Sentimentos: {sentimentos}.\n\t Variacao: {variacao_no_dia}')
            print("---------------------------------------------------------------\n")

    # Função para gerar e salvar gráficos de barras
    def salvar_grafico_barras(titulo, dados, empresa, tipo):
        sentimentos, variacoes = zip(*dados)
        x_indices = np.arange(len(sentimentos))

        plt.figure(figsize=(12, 6))
        plt.bar(x_indices, variacoes, color='skyblue', alpha=0.8)
        plt.xticks(x_indices, [f"{s:.2f}" for s in sentimentos], rotation=45, fontsize=8)
        plt.title(titulo)
        plt.xlabel("Sentimento (score)")
        plt.ylabel("Variação de Preço")
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Criar pasta para salvar gráficos
        output_dir = "./graficos_empresas"
        os.makedirs(output_dir, exist_ok=True)

        # Salvar gráfico como PNG
        plt.tight_layout()
        plt.savefig(f"{output_dir}/{empresa}_{tipo}.png")
        plt.close()

    # Gerar gráficos para cada empresa
    for empresa, dados in empresas_sentimentos_variacao.items():
        salvar_grafico_barras(f"{empresa} - Sentimento x Variação no Dia", dados["no_dia"], empresa, "no_dia")
        salvar_grafico_barras(f"{empresa} - Sentimento x Variação 1 Dia Antes", dados["um_dia_antes"], empresa, "um_dia_antes")
        salvar_grafico_barras(f"{empresa} - Sentimento x Variação 1 Dia Depois", dados["um_dia_depois"], empresa, "um_dia_depois")
        salvar_grafico_barras(f"{empresa} - Sentimento x Variação 2 Dias Antes e Depois", dados["dois_dias_antes_e_depois"], empresa, "dois_dias_antes_e_depois")

if __name__ == "__main__":
    main()
