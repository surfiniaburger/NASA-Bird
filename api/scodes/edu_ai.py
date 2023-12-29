# EduAI Explorer - send_mars_rover_email.py

# ... (Existing code for sending a random Mars Rover photo)

# Integrate AI for categorizing Mars Rover photos
from ai_module import ai_categorize_photo  # Assuming an AI module for photo categorization

def get_categorized_mars_rover_photo(api_key):
    # Fetch a random Mars Rover photo
    photo_url = get_random_mars_rover_photo(api_key)

    # Use AI to categorize the photo
    tags = ai_categorize_photo(photo_url)

    # Modify email content to include AI-generated tags
    message.html_content = f'<strong>AI-Categorized Mars Rover Photo</strong><br>' \
                          f'<img src="{photo_url}" alt="Mars Rover Photo"><br>' \
                          f'Tags: {", ".join(tags)}'

    return photo_url

# Get a random or AI-categorized Mars Rover photo URL
photo_url = get_categorized_mars_rover_photo(nasa_api_key)

# ... (Rest of the code remains unchanged)

