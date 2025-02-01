from scrapping.scrapping import digest_news
from word_processing.word_sanitizer import sanitize_text
from mood_analysis.mood_analyser import analise_mood
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
from pathlib import Path
import unicodedata
import re


def main():
    print("Iniciando pipeline...")

    def sanitizar_nome(nome, limite=50):
        """
        Sanitiza o nome removendo acentos, espaços e caracteres especiais.
        Limita o tamanho do nome para evitar problemas de caminho longo.
        """
        nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('ascii')
        nome = re.sub(r'\s+', '_', nome)
        nome = re.sub(r'[^\w\-]', '', nome)
        nome = nome.lower()
        return nome[:limite]

    digest_news()

    dadosHistDict = {}

    with open("./dados_historicos.csv", "r", encoding="utf-8") as dadosFile:
        dadosHist = dadosFile.readlines()[1:]
        for line in dadosHist:
            empresa = line.split(",")[0]
            data = line.split(",")[1]
            variacao = float(line.split(",")[3])
            
            if empresa not in dadosHistDict:
                dadosHistDict[empresa] = {}
            dadosHistDict[empresa][data] = variacao

    with open("./noticias_empresas.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            empresa = row['EMPRESA']
            titulo = row['TÍTULO']
            data = row['DATA']
            noticia = row['TEXTO']

            texto_sanitizado = " ".join(sanitize_text(noticia))
            sentimentos = analise_mood(texto_sanitizado)
            sentimento_label = sentimentos[0]['label']

            sentimento_map_numerico = {
                "1 star": 1,
                "2 stars": 2,
                "3 stars": 3,
                "4 stars": 4,
                "5 stars": 5
            }
            sentimento_numerico = sentimento_map_numerico.get(sentimento_label, 3)

            dataNoticia = datetime.strptime(data, "%d/%m/%Y %Hh%M")
            dataNoticiaStr = dataNoticia.strftime("%Y-%m-%d")

            variacao_no_dia = dadosHistDict.get(empresa, {}).get(dataNoticiaStr, 0)
            variacao_um_dia_antes = dadosHistDict.get(empresa, {}).get(
                (dataNoticia - timedelta(days=1)).strftime("%Y-%m-%d"), 0)
            variacao_um_dia_depois = dadosHistDict.get(empresa, {}).get(
                (dataNoticia + timedelta(days=1)).strftime("%Y-%m-%d"), 0)
            variacao_dois_dias_antes = dadosHistDict.get(empresa, {}).get(
                (dataNoticia - timedelta(days=2)).strftime("%Y-%m-%d"), 0)
            variacao_dois_dias_depois = dadosHistDict.get(empresa, {}).get(
                (dataNoticia + timedelta(days=2)).strftime("%Y-%m-%d"), 0)

            empresa_sanitizada = sanitizar_nome(empresa)
            titulo_sanitizado = sanitizar_nome(titulo)

            output_dir = Path("./graficos_empresas") / empresa_sanitizada / titulo_sanitizado
            output_dir.mkdir(parents=True, exist_ok=True)

            def salvar_grafico_consolidado(titulo_grafico, sentimento, variacoes):
                """
                Gera e salva um único gráfico consolidado para cada notícia.
                """
                dias = ["2 Dias Antes", "1 Dia Antes", "No Dia", "1 Dia Depois", "2 Dias Depois"]
                plt.figure(figsize=(12, 6))
                plt.plot(dias, variacoes, marker='o', color='skyblue', alpha=0.8)

                plt.ylim(-10, 10)

                plt.title(f"{titulo_grafico} (Sentimento: {sentimento})")
                plt.xlabel("Período Relativo à Notícia")
                plt.ylabel("Variação de Preço (%)")
                plt.grid(True, linestyle='--', alpha=0.7)

                grafico_path = output_dir / "grafico_consolidado.png"
                plt.tight_layout()
                plt.savefig(grafico_path)
                plt.close()
                print(f"Gráfico salvo em: {grafico_path}")

            salvar_grafico_consolidado(
                titulo,
                sentimento_label,
                [variacao_dois_dias_antes, variacao_um_dia_antes, variacao_no_dia,
                 variacao_um_dia_depois, variacao_dois_dias_depois]
            )

if __name__ == "__main__":
    main()