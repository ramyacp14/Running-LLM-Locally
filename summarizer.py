from flask import Flask, render_template, request
import requests
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

OLLAMA_BASE_URL = 'http://localhost:11434'  # We'll use this as a base URL
model = 'llama3.2'  # Define the model to use

# Function to call the generate API similar to the second script
def generate_summary(content, context):
    try:
        prompt = f"Summarize the following webpage content: {content}"  # Create a summarization prompt
        r = requests.post(f'{OLLAMA_BASE_URL}/api/generate',
                          json={
                              'model': model,
                              'prompt': prompt,
                              'context': context,
                          },
                          stream=True)
        r.raise_for_status()

        response_text = ""
        for line in r.iter_lines():
            body = json.loads(line)
            response_part = body.get('response', '')
            response_text += response_part  # Collect the streamed response

            if 'error' in body:
                raise Exception(body['error'])

            if body.get('done', False):
                return response_text, body['context']
    except requests.RequestException as e:
        return f"An error occurred: {str(e)}", context
    except json.JSONDecodeError:
        return "Error: Received an invalid response from the LLM.", context
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}", context


# Function to fetch the content of a webpage using the provided URL
def fetch_webpage_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Use BeautifulSoup to extract text content from the webpage
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        return f"Failed to fetch the webpage: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def index():
    context = []  # Initialize context to store conversation history
    summary_response = ""
    url_input = ""  # Initialize url_input to an empty string

    if request.method == 'POST':
        url_input = request.form['url_input']

        # Fetch the content of the webpage
        webpage_content = fetch_webpage_content(url_input)

        # Generate summary of the webpage content using the LLM
        if "Failed to fetch" not in webpage_content:  # Proceed if webpage was fetched successfully
            summary_response, context = generate_summary(webpage_content, context)
        else:
            summary_response = webpage_content

    return render_template('index1.html', response=summary_response, url_input=url_input)


if __name__ == '__main__':
    app.run(debug=True)
