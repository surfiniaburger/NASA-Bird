# config.py

class Config:
    DEBUG = False
    # Other configuration options...

class TestConfig(Config):
    TESTING = True
    DEBUG = True  # Set DEBUG to True for testing
    # Other testing-specific configuration options...
