from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

OLLAMA_BASE_URL = 'http://localhost:11434'  # We'll use this as a base URL
model = 'llama3.2'  # Define the model to use

# Function to call the generate API similar to the second script
def generate(prompt, context):
    try:
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


@app.route('/', methods=['GET', 'POST'])
def index():
    context = []  # Initialize context to store conversation history
    llm_response = ""
    user_input = ""  # Initialize user_input to an empty string

    if request.method == 'POST':
        user_input = request.form['user_input']

        # Generate response using the generate function
        llm_response, context = generate(user_input, context)

    return render_template('index.html', response=llm_response, user_input=user_input)


if __name__ == '__main__':
    app.run(debug=True)
