import unittest
import json
from typing import Dict, List, Any, Optional
from flask import Flask, Response
from models import Game, Publisher, Category, db, init_db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'
    CATEGORIES_API_PATH: str = '/api/categories'
    PUBLISHERS_API_PATH: str = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        init_db(self.app, testing=True)
        
        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))
            
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        # Verify all games using loop instead of manual testing
        for i, game_data in enumerate(data):
            test_game = self.TEST_DATA["games"][i]
            test_publisher = self.TEST_DATA["publishers"][test_game["publisher_index"]]
            test_category = self.TEST_DATA["categories"][test_game["category_index"]]
            
            self.assertEqual(game_data['title'], test_game["title"])
            self.assertEqual(game_data['publisher']['name'], test_publisher["name"])
            self.assertEqual(game_data['category']['name'], test_category["name"])
            self.assertEqual(game_data['starRating'], test_game["star_rating"])

    def test_get_games_structure(self) -> None:
        """Test the response structure for games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        # Get the first game's ID from the list endpoint
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        first_game = self.TEST_DATA["games"][0]
        first_publisher = self.TEST_DATA["publishers"][first_game["publisher_index"]]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], first_game["title"])
        self.assertEqual(data['publisher']['name'], first_publisher["name"])
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_filter_games_by_category(self) -> None:
        """Test filtering games by category_id returns only matching games"""
        # Get all categories to find the Strategy category id
        response = self.client.get(self.CATEGORIES_API_PATH)
        categories = self._get_response_data(response)
        strategy_category = next(c for c in categories if c['name'] == 'Strategy')

        # Act: filter by Strategy category
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={strategy_category["id"]}')
        data = self._get_response_data(response)

        # Assert: only games with Strategy category are returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')
        self.assertEqual(data[0]['category']['name'], 'Strategy')

    def test_filter_games_by_category_no_results(self) -> None:
        """Test filtering by a category_id that has no games returns empty list"""
        # Use a category_id that does not exist
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id=9999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_filter_games_by_publisher(self) -> None:
        """Test filtering games by publisher_id returns only matching games"""
        # Get all publishers to find the Scrum Masters publisher id
        response = self.client.get(self.PUBLISHERS_API_PATH)
        publishers = self._get_response_data(response)
        scrum_publisher = next(p for p in publishers if p['name'] == 'Scrum Masters')

        # Act: filter by Scrum Masters publisher
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id={scrum_publisher["id"]}')
        data = self._get_response_data(response)

        # Assert: only games from Scrum Masters are returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Agile Adventures')
        self.assertEqual(data[0]['publisher']['name'], 'Scrum Masters')

    def test_filter_games_by_publisher_no_results(self) -> None:
        """Test filtering by a publisher_id that has no games returns empty list"""
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id=9999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_filter_games_by_category_and_publisher(self) -> None:
        """Test filtering games by both category_id and publisher_id returns matching games"""
        # Get IDs for category=Strategy, publisher=DevGames Inc
        categories_response = self._get_response_data(self.client.get(self.CATEGORIES_API_PATH))
        publishers_response = self._get_response_data(self.client.get(self.PUBLISHERS_API_PATH))

        strategy_id = next(c['id'] for c in categories_response if c['name'] == 'Strategy')
        devgames_id = next(p['id'] for p in publishers_response if p['name'] == 'DevGames Inc')

        # Act: filter by both category and publisher
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={strategy_id}&publisher_id={devgames_id}')
        data = self._get_response_data(response)

        # Assert: Pipeline Panic matches both filters
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')

    def test_filter_games_combined_no_results(self) -> None:
        """Test filtering by mismatched category and publisher returns empty list"""
        # Strategy category but Scrum Masters publisher — no game matches both
        categories_response = self._get_response_data(self.client.get(self.CATEGORIES_API_PATH))
        publishers_response = self._get_response_data(self.client.get(self.PUBLISHERS_API_PATH))

        strategy_id = next(c['id'] for c in categories_response if c['name'] == 'Strategy')
        scrum_id = next(p['id'] for p in publishers_response if p['name'] == 'Scrum Masters')

        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={strategy_id}&publisher_id={scrum_id}')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_get_categories_success(self) -> None:
        """Test that the categories endpoint returns all categories"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["categories"]))
        category_names = [c['name'] for c in data]
        for cat in self.TEST_DATA["categories"]:
            self.assertIn(cat['name'], category_names)

    def test_get_publishers_success(self) -> None:
        """Test that the publishers endpoint returns all publishers"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["publishers"]))
        publisher_names = [p['name'] for p in data]
        for pub in self.TEST_DATA["publishers"]:
            self.assertIn(pub['name'], publisher_names)

if __name__ == '__main__':
    unittest.main()
