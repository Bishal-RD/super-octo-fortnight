"""
Games API Routes Module

This module provides the API routes for game-related operations in the
Tailspin Toys crowdfunding platform. It includes endpoints for retrieving
all games and individual game details, as well as creating, updating and
deleting games.
"""

from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError
from typing import Tuple

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

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    """
    Create a new game endpoint.
    
    Creates a new game in the database with the provided information.
    
    Expected request body:
        - title: The game's title (required)
        - description: The game's description (required)
        - publisher_id: ID of the publisher (required)
        - category_id: ID of the category (required)
        - star_rating: Optional rating score for the game
        
    Returns:
        Response: JSON response containing the created game object if successful,
                 or an error message if validation fails
        int: HTTP status code (201 if created, 400 for invalid data)
    """
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'publisher_id', 'category_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Verify publisher and category exist
        publisher = db.session.get(Publisher, data['publisher_id'])
        category = db.session.get(Category, data['category_id'])
        
        if not publisher or not category:
            return jsonify({"error": "Invalid publisher_id or category_id"}), 400
        
        # Create new game
        new_game = Game(
            title=data['title'],
            description=data['description'],
            publisher_id=data['publisher_id'],
            category_id=data['category_id'],
            star_rating=data.get('star_rating')  # Optional field
        )
        
        db.session.add(new_game)
        db.session.commit()
        
        # Return the created game
        return jsonify(new_game.to_dict()), 201
        
    except ValueError as e:
        # Handle validation errors from the model
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        # Handle database errors
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int]:
    """
    Update a game endpoint.
    
    Updates an existing game in the database with the provided information.
    
    Args:
        id (int): The unique identifier of the game to update.
        
    Expected request body:
        - title: The game's new title (optional)
        - description: The game's new description (optional)
        - publisher_id: New publisher ID (optional)
        - category_id: New category ID (optional)
        - star_rating: New rating score (optional)
        
    Returns:
        Response: JSON response containing the updated game object if successful,
                 or an error message if validation fails or game not found
        int: HTTP status code (200 if updated, 404 if not found, 400 for invalid data)
    """
    try:
        game = db.session.get(Game, id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
            
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            game.title = data['title']
        if 'description' in data:
            game.description = data['description']
        if 'publisher_id' in data:
            if not db.session.get(Publisher, data['publisher_id']):
                return jsonify({"error": "Invalid publisher_id"}), 400
            game.publisher_id = data['publisher_id']
        if 'category_id' in data:
            if not db.session.get(Category, data['category_id']):
                return jsonify({"error": "Invalid category_id"}), 400
            game.category_id = data['category_id']
        if 'star_rating' in data:
            game.star_rating = data['star_rating']
            
        db.session.commit()
        
        return jsonify(game.to_dict())
        
    except ValueError as e:
        # Handle validation errors from the model
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        # Handle database errors
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    """
    Delete a game endpoint.
    
    Removes a game from the database.
    
    Args:
        id (int): The unique identifier of the game to delete.
        
    Returns:
        Response: Empty response if successful, or error message if game not found
        int: HTTP status code (204 if deleted, 404 if not found)
    """
    try:
        game = db.session.get(Game, id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
            
        db.session.delete(game)
        db.session.commit()
        
        return '', 204
        
    except SQLAlchemyError as e:
        # Handle database errors
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
