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
        textos = [line.split(",")[4] for line in noticias]  # Supondo texto na 4ª coluna
        textos_sanitizados = [" ".join(sanitize_text(texto)) for texto in textos]
        sentimentos = analise_mood(textos_sanitizados)
    
    print("Resultados dos sentimentos:", sentimentos)

if __name__ == "__main__":
    main()