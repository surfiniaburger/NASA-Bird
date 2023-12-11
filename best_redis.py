# RedPlanet Explore - send_mars_rover_email.py

# ... (Existing code for sending a random Mars Rover photo)

# Integrate Redis Cloud for caching
import redis

# Connect to Redis Cloud
redis_client = redis.StrictRedis(host='your-redis-host', port=6379, db=0, decode_responses=True)

def get_cached_mars_rover_photo(api_key):
    # Check if photo is in cache
    cached_photo_url = redis_client.get('mars_rover_photo')
    if cached_photo_url:
        return cached_photo_url

    # If not in cache, fetch a new photo
    photo_url = get_random_mars_rover_photo(api_key)

    # Cache the new photo for future use
    redis_client.set('mars_rover_photo', photo_url)

    return photo_url

# Get a random or cached Mars Rover photo URL
photo_url = get_cached_mars_rover_photo(nasa_api_key)

# ... (Rest of the code remains unchanged)

