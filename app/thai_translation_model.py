from transformers import MarianMTModel, MarianTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-th-en"

tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
model = MarianMTModel.from_pretrained(MODEL_NAME)

def preprocess(text):
    return text

def translate(text):
    input_ids = tokenizer.encode(text, return_tensors="pt")
    output_ids = model.generate(input_ids)[0]
    english_text = tokenizer.decode(output_ids, skip_special_tokens=True)
    return english_text
