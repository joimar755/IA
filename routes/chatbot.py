from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "joimar19/Convocatorias_Academica_Chatbot"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

device = torch.device("cpu")  # En tu Pentium mejor CPU
model.to(device)

def chat_convocatoria(pregunta, max_tokens=200):
    prompt = f"""
    Eres un asistente experto en Convocatorias académicas y administrativas universitaria.
    Respondes de forma clara, técnica.
    Usuario: {pregunta}
    secretari@:
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    # Move inputs to the same device as the model
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.2,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    texto = tokenizer.decode(output[0], skip_special_tokens=True)
    respuesta = texto.split("secretari@:")[-1].strip()
    return respuesta

