from flask import Flask, render_template, request
import requests
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from io import BytesIO
from PIL import Image

app = Flask(__name__)

def preprocess_text(text):
    # Tokenize the text into words
    tokens = word_tokenize(text.lower())

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # Reconstruct the processed text
    processed_text = ' '.join(tokens)

    return processed_text

def open_recipe_url(url):
    return f"<a href='{url}' target='_blank'>{url}</a>"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
        processed_input = preprocess_text(query)

        # Spoonacular API endpoint for recipe search
        url = 'https://api.spoonacular.com/recipes/search'

        # Spoonacular API key
        api_key = '8933a981b0764ebc9d0035f747a1226d'

        # Parameters for the API request
        params = {
            'apiKey': api_key,
            'query': processed_input,
            'number': 5  # Number of recipes to retrieve
        }

        # Send a GET request to the Spoonacular API
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the recipe data from the JSON response
            data = response.json()

            # Display the recipe information
            recipes = data['results']
            result_html = ""
            for recipe in recipes:
                result_html += f"<div class='chat-item received'><div class='message'>"
                result_html += f"<p>{recipe['title']}</p>"
                if 'image' in recipe:
                    # Load and display the recipe image
                    image_url = recipe['image']
                    if not image_url.startswith('http'):
                        image_url = 'https:' + image_url
                    try:
                        image_response = requests.get(image_url)
                        image_data = Image.open(BytesIO(image_response.content))
                        image_data = image_data.resize((150, 150), Image.ANTIALIAS)
                        image_data.save(f'static/images/{recipe["id"]}.jpg')
                        result_html += f"<img src='static/images/{recipe['id']}.jpg' alt='Recipe Image'>"
                    except requests.exceptions.RequestException:
                        pass
                result_html += f"<p>{open_recipe_url(recipe['sourceUrl'])}</p>"
                result_html += "</div></div>"

            return result_html

    return render_template('index.html')

if __name__ == '__main__':
    app.run()
