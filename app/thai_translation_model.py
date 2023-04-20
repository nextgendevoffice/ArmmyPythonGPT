from googletrans import Translator

def preprocess(text):
    return text

def translate(text):
    translator = Translator()
    translated_text = translator.translate(text, src='th', dest='en').text
    return translated_text
