"""
Games API Routes Module

This module provides the API routes for game-related operations in the
Tailspin Toys crowdfunding platform. It includes endpoints for retrieving
all games and individual game details.
"""

from flask import jsonify, Response, Blueprint
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    """
    Create a base query for retrieving games with joined related data.
    
    This function creates a SQLAlchemy query that joins the Game model with
    its related Publisher and Category models. The joins are left outer joins
    to ensure games are returned even if they don't have associated publishers
    or categories.
    
    Returns:
        Query: A SQLAlchemy query object with joined tables.
    """
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    """
    Get all games endpoint.
    
    Retrieves all games from the database including their associated
    publisher and category information.
    
    Returns:
        Response: JSON response containing an array of game objects.
        Each game object includes:
        - id: The game's unique identifier
        - title: The game's title
        - description: The game's description
        - publisher: Object containing publisher id and name
        - category: Object containing category id and name
        - starRating: The game's star rating (if any)
    """
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    """
    Get a specific game by ID endpoint.
    
    Retrieves a single game from the database by its ID, including its
    associated publisher and category information.
    
    Args:
        id (int): The unique identifier of the game to retrieve.
    
    Returns:
        Response: JSON response containing the game object if found, or
                 an error message if not found.
        int: HTTP status code (404 if game not found).
        
    The game object includes:
        - id: The game's unique identifier
        - title: The game's title
        - description: The game's description
        - publisher: Object containing publisher id and name
        - category: Object containing category id and name
        - starRating: The game's star rating (if any)
    """
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)
