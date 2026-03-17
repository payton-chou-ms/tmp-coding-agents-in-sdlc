from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
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
    # Build base query with optional filters for category and publisher
    query = get_games_base_query()

    category_id = request.args.get('category_id', type=int)
    publisher_id = request.args.get('publisher_id', type=int)

    if category_id is not None:
        query = query.filter(Game.category_id == category_id)
    if publisher_id is not None:
        query = query.filter(Game.publisher_id == publisher_id)

    games_list = [game.to_dict() for game in query.all()]
    
    return jsonify(games_list)

@games_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    # Return all categories for use in filter dropdowns
    categories = db.session.query(Category).order_by(Category.name).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@games_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    # Return all publishers for use in filter dropdowns
    publishers = db.session.query(Publisher).order_by(Publisher.name).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in publishers])

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)
