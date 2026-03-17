from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Category(BaseModel):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one category has many games
    games = relationship("Game", back_populates="category")
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate that the category name meets minimum length requirements.

        Args:
            key: The attribute key being validated (provided by SQLAlchemy).
            name: The name value to validate.

        Returns:
            str: The validated name string.
        """
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key: str, description: str) -> str:
        """Validate that the category description meets minimum length requirements.

        Args:
            key: The attribute key being validated (provided by SQLAlchemy).
            description: The description value to validate.

        Returns:
            str: The validated description string, or None if None was provided.
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self) -> str:
        """Return a string representation of the Category instance."""
        return f'<Category {self.name}>'
        
    def to_dict(self) -> dict:
        """Serialize the Category instance to a dictionary.

        Returns:
            dict: A dictionary containing the category's id, name, description,
                  and game_count.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }