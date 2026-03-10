# Use a pipeline as a high-level helper
from transformers import pipeline

analisis_sentimientos = pipeline("text-classification", model="finiteautomata/beto-sentiment-analysis") 


def analisis_sentimientos_nlp(texto: str):
    resultado = analisis_sentimientos(texto)
    return {
        "frase": texto,
        "sentimiento": resultado[0]['label'],
        "confianza": round(resultado[0]['score'], 4)
    }

""" resultado = analisis_sentimientos_nlp(texto)
print("Resultado del análisis de sentimientos:", resultado) 
 """

''' print(resultado)
print(f"frase: {texto}")
print(f"sentimiento:{resultado[0]['label']}")
print(f"confianza:{resultado[0]['score']:.4f}")  '''