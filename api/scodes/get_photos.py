import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

# Function to get a random Mars Rover photo URL
def get_random_mars_rover_photo(api_key):
    base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    params = {
        "api_key": api_key,
        "page": 1,
        "sol": random.randint(1, 3000),  # Choose a random Martian day (sol)
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Extracting a random photo URL
    if "photos" in data and data["photos"]:
        photo = random.choice(data["photos"])
        return photo["img_src"]
    else:
        return None

# Get a random Mars Rover photo URL
nasa_api_key = "Fcu3mnOKVdo4KE0HdX2CHMjhqPlVMjgMHqJjhLX8"
photo_url = get_random_mars_rover_photo(nasa_api_key)

# If a photo URL is available, create and send the email
if photo_url:
    message = Mail(
        from_email='jdmasciano2@gmail.com',
        to_emails='surfiniaburger@gmail.com',
        subject='Random Mars Rover Photo',
        html_content=f'<strong>Here is a random Mars Rover photo:</strong><br><img src="{photo_url}" alt="Mars Rover Photo">')

    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code, response.body, response.headers)
else:
    print("Failed to retrieve a Mars Rover photo.")
