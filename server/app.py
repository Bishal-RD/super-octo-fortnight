"""
Tailspin Toys Crowdfunding Platform Flask Application

This module serves as the main entry point for the Flask application. It initializes
the Flask app, sets up the database connection, and registers all blueprints for
routing.

The application runs on port 5100 to avoid conflicts with other common development
ports on macOS systems.
"""

import os
from flask import Flask
from models import init_db
from routes.games import games_bp
from utils.database import init_db

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask application
app: Flask = Flask(__name__)

def setup_app() -> Flask:
    """
    Configure and set up the Flask application.
    
    This function initializes the database connection and registers all blueprints
    for the application's routing.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    # Initialize the database with the app
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(games_bp)
    
    return app

# Set up the application
app = setup_app()

if __name__ == '__main__':
    app.run(debug=True, port=5100) # Port 5100 to avoid macOS conflicts