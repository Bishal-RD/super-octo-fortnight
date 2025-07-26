"""
Game Model Module

This module defines the Game model for the Tailspin Toys crowdfunding platform.
Games are the core entity of the platform, representing gaming projects that can
be funded by users.
"""

from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Game(BaseModel):
    """
    Game model representing a game project in the crowdfunding platform.
    
    This model stores essential information about games including their title,
    description, rating, and relationships with publishers and categories.
    
    Attributes:
        id (int): Primary key for the game.
        title (str): The game's title, must be at least 2 characters.
        description (str): Detailed description of the game, minimum 10 characters.
        star_rating (float): Optional rating score for the game.
        category_id (int): Foreign key to the game's category.
        publisher_id (int): Foreign key to the game's publisher.
        category (Category): Relationship to the game's category.
        publisher (Publisher): Relationship to the game's publisher.
    """
    
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    star_rating = db.Column(db.Float, nullable=True)
    
    # Foreign keys for one-to-many relationships
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)
    
    # One-to-many relationships (many games belong to one category/publisher)
    category = relationship("Category", back_populates="games")
    publisher = relationship("Publisher", back_populates="games")
    
    @validates('title')
    def validate_name(self, key: str, name: str) -> str:
        """
        Validate the game's title.
        
        Args:
            key (str): The field being validated ('title').
            name (str): The title to validate.
            
        Returns:
            str: The validated title.
            
        Raises:
            ValueError: If the title is less than 2 characters long.
        """
        return self.validate_string_length('Game title', name, min_length=2)
    
    @validates('description')
    def validate_description(self, key: str, description: str) -> str:
        """
        Validate the game's description.
        
        Args:
            key (str): The field being validated ('description').
            description (str): The description to validate.
            
        Returns:
            str: The validated description.
            
        Raises:
            ValueError: If the description is less than 10 characters long.
        """
        if description is not None:
            return self.validate_string_length('Description', description, min_length=10, allow_none=True)
        return description
    
    def __repr__(self) -> str:
        """
        Get string representation of the Game object.
        
        Returns:
            str: String representation including title and ID.
        """
        return f'<Game {self.title}, ID: {self.id}>'

    def to_dict(self) -> dict:
        """
        Convert the Game object to a dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary containing the game's data with nested publisher
                  and category information.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publisher': {'id': self.publisher.id, 'name': self.publisher.name} if self.publisher else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'starRating': self.star_rating  # Changed from star_rating to starRating
        }