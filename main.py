from scrapping.scrapping import digest_news
from scrapping.variacao_precos import variacao_por_noticia
from word_processing.word_sanitizer import sanitize_text
from mood_analysis.mood_analyser import analise_mood

def main():
    print("Iniciando pipeline...")
    
    # Coleta e processamento de notícias
    digest_news()
    
    # Análise de variações e sentimentos
    # (Considerando que `noticias.csv` seja gerado pelo `digest_news`)
    with open("./noticias_empresas.csv", "r") as file:
        noticias = file.readlines()[1:]  # Ignorar cabeçalho
        noticias_formatadas = [(line.split(",")[0], line.split(",")[1], line.split(",")[4]) for line in noticias]
        print("---------------------------------------------------------------\n")
        for (empresa, titulo, noticia) in noticias_formatadas:
            texto_sanitizado = " ".join(sanitize_text(noticia))
            sentimentos = analise_mood(texto_sanitizado)
            print(f'Empresa: {empresa}.\n\t Noticia: {titulo}.\n\t Sentimentos: {sentimentos}')
            print("---------------------------------------------------------------\n")

if __name__ == "__main__":
    main()