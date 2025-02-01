from transformers import pipeline


def analise_mood(textos: list[str]):
    sentiment_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    resultados_transformers = sentiment_model(textos)
    return resultados_transformers