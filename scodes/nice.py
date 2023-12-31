# Flask web application integrating educational AI, space photos, and fun facts with Redis
from flask import Flask, render_template, Response, flash, redirect, url_for, request
from flask import stream_with_context
from flask_redis import FlaskRedis
from dotenv import load_dotenv
from autoscraper import AutoScraper

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
import redis
import random
import requests

app = Flask(__name__)
redis_client = FlaskRedis(app)
load_dotenv()
app.config['SECRET_KEY'] = 'secret_key'

# Initialize Redis connection
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_pubsub = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

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


@app.route('/send-email', methods=['POST'])
def send_email():
    # Fetch the educational AI data, space photo, and fun fact
    ai_data = fetch_educational_ai_data()
    space_photo_url, fun_fact = get_random_space_photo()
    

    # Fetch AutoScraper results
    url = request.form.get('url')
    extracted_info = scrape_url(url) if url else None

    # Set up the SMTP server for Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'jdmasciano2@gmail.com'
    smtp_password = os.environ.get('app_password')  # Use the generated app password here

    # Create a MIMEText object for the email content
    msg = MIMEMultipart()
    msg['From'] = 'jdmasciano2@gmail.com'
    msg['To'] = 'surfiniaburger@gmail.com'  # Update the recipient email address
    msg['Subject'] = 'Educational AI, Mars Rover Photo, and Fun Fact'

    # Construct the HTML email content
    email_content = f'''
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

    msg.attach(MIMEText(email_content, 'html'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail('jdmasciano2@gmail.com', 'surfiniaburger@gmail.com', msg.as_string())

        # Close the connection
        server.quit()

        # Flash a success message
        success_message = 'Email sent successfully!'
        flash(success_message, 'success')

    except Exception as e:
        print(f"Error sending email: {e}")

    return redirect(url_for('landing_page'))



@app.route('/')
def landing_page():
    # Check if educational AI data is in cache
    ai_data = redis_client.get('educational_ai_data')

    if not ai_data:
        # If not in cache, fetch educational AI data
        ai_data = fetch_educational_ai_data()

        # Cache the educational AI data for future use
        redis_client.set('educational_ai_data', ai_data)

    # Fetch a random space-related photo URL
    space_photo_url, fun_fact = get_random_space_photo()

    # Fetch AutoScraper results (if available)
    url = request.args.get('url')
    extracted_info = scrape_url(url) if url else None

    # Render the template with the variables
    return render_template('index.html', ai_data=ai_data, space_photo_url=space_photo_url, fun_fact=fun_fact, extracted_info=extracted_info)



def notify_clients(data):
    redis_pubsub.publish('real-time-updates', data)


def fetch_educational_ai_data():
    topics = [
        "Explore the fascinating journey of the Mars rovers, including Spirit, Opportunity, Curiosity, and Perseverance.",
        "Learn about the unique challenges of landing and operating rovers on the Martian surface.",
        "Discover how Mars rovers analyze soil and rock samples to understand the geology and history of Mars.",
        "Understand the role of Mars rovers in the search for signs of past or present life on the Red Planet.",
        "Explore the advanced scientific instruments onboard Mars rovers, such as spectrometers and cameras.",
        "Learn about the achievements and key discoveries made by Mars rovers, including evidence of past water activity.",
        "Understand the significance of Perseverance's mission in the context of paving the way for future human exploration.",
        "Explore the technological innovations that enable remote operation and communication with Mars rovers.",
        "Discover the collaborative international efforts involved in planning and executing Mars rover missions.",
        "Learn about the daily challenges faced by Mars rovers, from navigating the Martian terrain to enduring harsh conditions.",
    ]

    return random.choice(topics)

api_key=os.environ.get("NASA_API_KEY")

api_dict = {
    "mars-rovers": {
        "url": "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos",
        "params": {"api_key": api_key, "page": 1, "sol": random.randint(1, 3000)}
    },

    # Add more sections as needed
}

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
def real_time_updates():
    pubsub = redis_pubsub.pubsub()
    pubsub.subscribe('real-time-updates')

    def generate():
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield f"data: {message['data']}\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)