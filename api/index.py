from app import app  # assuming 'app' is your Flask app instance

def handler(environ, start_response):
    return app.wsgi_app(environ, start_response)
