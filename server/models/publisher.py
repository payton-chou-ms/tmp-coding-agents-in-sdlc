from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Publisher(BaseModel):
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one publisher has many games
    games = relationship("Game", back_populates="publisher")

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate that the publisher name meets minimum length requirements.

        Args:
            key: The attribute key being validated (provided by SQLAlchemy).
            name: The name value to validate.

        Returns:
            str: The validated name string.
        """
        return self.validate_string_length('Publisher name', name, min_length=2)

    @validates('description')
    def validate_description(self, key: str, description: str) -> str:
        """Validate that the publisher description meets minimum length requirements.

        Args:
            key: The attribute key being validated (provided by SQLAlchemy).
            description: The description value to validate.

        Returns:
            str: The validated description string, or None if None was provided.
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)

    def __repr__(self) -> str:
        """Return a string representation of the Publisher instance."""
        return f'<Publisher {self.name}>'

    def to_dict(self) -> dict:
        """Serialize the Publisher instance to a dictionary.

        Returns:
            dict: A dictionary containing the publisher's id, name, description,
                  and game_count.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }