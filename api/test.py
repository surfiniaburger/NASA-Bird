# Flask web application integrating educational AI, space photos, and fun facts with Redis
from flask import Flask, render_template, Response, flash, redirect, url_for, request, jsonify, make_response
from flask import stream_with_context
from flask_redis import FlaskRedis
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from autoscraper import AutoScraper
from transformers import pipeline
from flask_cors import CORS
from flask import session
import os
import redis
import random
import requests


app = Flask(__name__)
CORS(app)
redis_client = FlaskRedis(app)
load_dotenv()
app.config['SECRET_KEY'] = 'secret_key'


# Initialize Redis connection
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_pubsub = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)



def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    return summary[0]['summary_text']

@app.route('/summarize', methods=['POST', 'GET'])
async def summarize_content():
    if request.method == 'POST':
        content = request.form.get('content')
        summarized_content = summarize_text(content)
        return redirect(url_for('landing_page', summarized_content=summarized_content))

# Add a new route to handle the AutoScraper results
@app.route('/auto-scraper-result', methods=['GET', 'OPTIONS'])
def auto_scraper_result():
    if request.method == 'OPTIONS':
        # Handle preflight request (e.g., provide required headers)
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200

    # Regular GET request logic
    url = request.args.get('url')
    extracted_info = scrape_url(url) if url else None

    # Return the AutoScraper result
    return jsonify({'result': extracted_info})

def notify_clients(data):
    redis_pubsub.publish('real-time-updates', data)

# Add a new route to handle the AutoScraper results
def scrape_url(url):
    # Initialize AutoScraper
    scraper = AutoScraper()
    wanted_list = ["Mars", "NASA"]

    # Build the scraper for the provided URL
    result = scraper.build(url, wanted_list)

    if result:
        # Use the scraper to extract information from the provided URL
        extracted_info = scraper.get_result_similar(url)
        return extracted_info

    return None

@app.route('/')
async def landing_page():
    # Check if educational AI data is in cache
    ai_data = redis_client.get('educational_ai_data')

    if not ai_data:
        # If not in cache, fetch educational AI data
        ai_data = fetch_educational_ai_data()

        # Cache the educational AI data for future use
        redis_client.set('educational_ai_data', ai_data)
    
     # Check if the user has selected a specific educational module
    selected_module = request.args.get('selected_module', None)

    # If a module is selected, fetch content related to that module
    if selected_module:
        ai_data = fetch_educational_ai_data(module=selected_module)

    # Fetch a random space-related photo URL
    space_photo_url, fun_fact = get_random_space_photo()
  
    # Fetch AutoScraper results (if available)
    url = request.args.get('url')
    extracted_info = scrape_url(url) if url else None
    
    # Check if the user has submitted an answer
    user_answer = request.args.get('user_answer', None)

    # If a user answer is provided, perform automated grading
    if user_answer:
        grade, feedback = perform_automated_grading(user_answer)
    else:
        grade, feedback = None, None
    
     # Check if the user has selected the Teacher Training module
    if selected_module == 'teacher_training':
        teacher_training_content = get_teacher_training_content()
    else:
        teacher_training_content = None


    summarized_content = request.args.get('summarized_content', None)
    
    # If summarized content is available, provide personalized feedback
    if summarized_content:
        personalized_feedback = generate_personalized_feedback(summarized_content)
    else:
        personalized_feedback = None
    return render_template('index.html', ai_data=ai_data, space_photo_url=space_photo_url, fun_fact=fun_fact, extracted_info=extracted_info, summarized_content=summarized_content)

# Add a new function to generate personalized feedback
def generate_personalized_feedback(summarized_content):
    # Implement your logic to generate personalized feedback based on the summarized content
    # This could involve analyzing the content and providing specific insights or suggestions
    feedback = "Great job summarizing the content! Consider adding more details about..."
    return feedback

def perform_automated_grading(user_answer):
    # Implement your logic to grade the user's answer
    # This could involve comparing the user's answer with predefined correct answers
    correct_answer = "The correct answer is..."

    if user_answer == correct_answer:
        return "Correct", "Well done! Your answer is correct."
    else:
        return "Incorrect", "Sorry, your answer is incorrect. The correct answer is..."

# Add a new function to fetch teacher training content
def get_teacher_training_content():
    # Implement logic to fetch teacher training content
    training_topics = [
        "Effective Classroom Management Strategies",
        "Utilizing Technology in Teaching",
        "Creating Engaging Lesson Plans",
        "Differentiated Instruction Techniques",
        "Assessment and Feedback Best Practices",
        "Inclusive Education Strategies",
        "Professional Development Opportunities for Teachers",
        "Building a Positive Classroom Culture",
        "Collaborative Learning in the Classroom",
        "Addressing Diverse Learning Needs",
    ]
    return random.choice(training_topics)


@app.route('/send-email', methods=['POST'])

def send_email():
    # Fetch the educational AI data, space photo, and fun fact
    ai_data = fetch_educational_ai_data()
    space_photo_url, fun_fact = get_random_space_photo()

     # Fetch AutoScraper results
    url = request.form.get('url')
    extracted_info = scrape_url(url) if url else None

     


    # Send email with educational AI data, the space-related photo, and the fun fact
    message = Mail(
        from_email='jdmasciano2@gmail.com',
        to_emails='surfiniaburger@gmail.com',
        subject='Educational AI, Mars Rover Photo, and Fun Fact',
         html_content=f'''
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .fun-fact {{
                        font-style: italic;
                        color: #007BFF;
                    }}
                    .feedback-link {{
                        display: block;
                        margin-top: 20px;
                        text-decoration: none;
                        color: #28A745;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <strong>{ai_data}</strong><br>
                    <img src="{space_photo_url}" alt="Space Photo"><br>
                    <em class="fun-fact">Fun Fact:</em> {fun_fact}<br>
                    <a href="https://your-feedback-form-link" class="feedback-link">Provide Feedback</a>
                </div>
            </body>
        </html>
    '''
)

    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)

    # Flash a success message
    if response.status_code == 202:
        success_message = 'Email sent successfully!'
        flash(success_message, 'success')

    return redirect(url_for('landing_page'))

def notify_clients(data):
    redis_pubsub.publish('real-time-updates', data)


def fetch_educational_ai_data(module=None):
    topics = {
        "topic1":"Explore the fascinating journey of the Mars rovers, including Spirit, Opportunity, Curiosity, & Perseverance.",
        "topic2":"Learn about the unique challenges of landing &, operating rovers on the Martian surface.",
        "topic3":"Discover how Mars rovers analyze soil and rock samples to understand the geology and history of Mars.",
        "topic4":"Understand the role of Mars rovers in the search for signs of past or present life on the Red Planet.",
        "topic5":"Explore the advanced scientific instruments onboard Mars rovers, such as spectrometers and cameras.",
        "topic6":"Learn about the achievements and key discoveries made by Mars rovers, including evidence of past water activity.",
        "topic7":"Understand the significance of Perseverance's mission in the context of paving the way for future human exploration.",
        "topic8":"Explore the technological innovations that enable remote operation and communication with Mars rovers.",
        "topic9":"Discover the collaborative international efforts involved in planning and executing Mars rover missions.",
        "topic10":"Learn about the daily challenges faced by Mars rovers, from navigating the Martian terrain to enduring harsh conditions.",
    }
    # If a specific module is provided, fetch content related to that module
    if module:
        return topics.get(module, random.choice(list(topics.values())))
    else:
        return random.choice(list(topics.values()))


api_key=os.environ.get("NASA_API_KEY")

api_dict = {
    "mars-rovers": {
        "url": "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos",
        "params": {"api_key": api_key, "page": 1, "sol": random.randint(1, 3000)}
    },

    # Add more sections as needed
}

@app.route('/mars-rover-photos')
def get_random_space_photo():
    selected_section = random.choice(list(api_dict.keys()))
    selected_api = api_dict[selected_section]
    base_url = selected_api["url"]
    params = selected_api["params"]
    response = requests.get(base_url, params=params)
    
    # Generate a unique cache key based on the selected API and parameters
    cache_key = f"{selected_section}:{params['sol']}"

    # Check if the data is in the cache
    cached_data = redis_client.get(cache_key)

    if cached_data:
        # If cached data exists, return it
        cached_data = cached_data.decode('utf-8').split(',')
        return cached_data[0], cached_data[1]
    
    # If not in the cache, make a new API request
    response = requests.get(base_url, params=params)

    try:
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        if "photos" in data and data["photos"]:
            photo = random.choice(data["photos"])
            return photo["img_src"], get_fun_fact(selected_section)
        else:
            return None, None
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        return None, None
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
        return None, None
    except requests.exceptions.JSONDecodeError as err_json:
        print(f"JSON Decode Error: {err_json}")
        return None, None


def get_fun_fact(selected_section):
    # Add fun facts for each section
    fun_facts =  {
        "mars-rovers": [
            "Did you know that Curiosity, the Mars Science Laboratory rover, landed on Mars on August 5, 2012?",
            "The Opportunity rover operated on Mars for over 14 years, from 2004 to 2019.",
            "Spirit, NASA's first Mars rover, was active on the red planet from 2004 to 2010.",
            "Perseverance, the latest Mars rover, landed on Mars on February 18, 2021.",
            "Mars rovers are designed to study the geology and climate of Mars.",
            "Curiosity is equipped with a laser that can vaporize rocks for analysis.",
            "Opportunity set a record for the longest distance traveled on Mars, covering over 28 miles.",
            "Mars rovers have discovered evidence of past water activity on the Martian surface.",
            "Perseverance carries the first helicopter, Ingenuity, flown on another planet.",
            "Mars rovers are crucial for paving the way for future human exploration of Mars.",
            "Image data gathered by NASA's Curiosity, Opportunity, and Spirit rovers on Mars"
        ],
        # Add more sections as needed
    }

    return random.choice(fun_facts.get(selected_section, []))

@app.route('/real-time-updates')
#@cache.cached(timeout=0, key_prefix='real_time_updates')
def get_real_time_updates():
    pubsub = redis_pubsub.pubsub()
    pubsub.subscribe('real-time-updates')

    def generate():
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield f"data: {message['data']}\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)