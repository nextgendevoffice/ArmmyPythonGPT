import openai

def preprocess(text):
    return text

def generate_image(api_key, text):
    openai.api_key = api_key

    response = openai.Image.create(
        prompt=text,
        n=1,
        size="512x512",
        response_format="url"
    )

    image_url = response['data'][0]['url']
    return image_url
