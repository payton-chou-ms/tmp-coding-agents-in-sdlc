from flask import jsonify, request, Response, Blueprint
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError

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
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

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

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate required fields
    required_fields = ['title', 'description', 'publisher_id', 'category_id']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Validate publisher and category exist
    publisher = db.session.get(Publisher, data['publisher_id'])
    if not publisher:
        return jsonify({"error": "Publisher not found"}), 404

    category = db.session.get(Category, data['category_id'])
    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        game = Game(
            title=data['title'],
            description=data['description'],
            publisher_id=data['publisher_id'],
            category_id=data['category_id'],
            star_rating=data.get('star_rating')
        )
        db.session.add(game)
        db.session.commit()
        created = get_games_base_query().filter(Game.id == game.id).first()
        if not created:
            return jsonify({"error": "Failed to retrieve created game"}), 500
        return jsonify(created.to_dict()), 201
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int]:
    game = db.session.get(Game, id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate publisher if provided
    if 'publisher_id' in data:
        publisher = db.session.get(Publisher, data['publisher_id'])
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 404

    # Validate category if provided
    if 'category_id' in data:
        category = db.session.get(Category, data['category_id'])
        if not category:
            return jsonify({"error": "Category not found"}), 404

    try:
        for field in ['title', 'description', 'publisher_id', 'category_id', 'star_rating']:
            if field in data:
                setattr(game, field, data[field])
        db.session.commit()
        updated = get_games_base_query().filter(Game.id == game.id).first()
        if not updated:
            return jsonify({"error": "Failed to retrieve updated game"}), 500
        return jsonify(updated.to_dict()), 200
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    game = db.session.get(Game, id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    try:
        db.session.delete(game)
        db.session.commit()
        return jsonify({"message": "Game deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
