from transformers import pipeline


def analise_mood(textos: list[str]):
    # Se tudo der errado, pode ser usado o pysentimiento (colocar no requirements se for usar)
    sentiment_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    resultados_transformers = sentiment_model(textos)
    return resultados_transformers
