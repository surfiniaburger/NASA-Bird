import pytest
from app import app

@pytest.fixture
def test_app():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_landing_page(test_app):
    response = test_app.get('/')
    assert response.status_code == 200

def test_summarize_content(test_app):
    response = test_app.post('/summarize', data={'content': 'Test content'})
    assert response.status_code == 302  # Assuming you're redirecting after form submission

def test_auto_scraper_result(test_app):
    response = test_app.get('/auto-scraper-result?url=https://fastapi.tiangolo.com/#requirements')
    assert response.status_code == 200

def test_send_email(test_app):
    response = test_app.post('/send-email', data={'url': 'https://example.com'})
    assert response.status_code == 302  # Assuming you're redirecting after sending the email


if __name__ == '__main__':
    pytest.main()
