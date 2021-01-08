import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            "question": "Is this is another questions?",
            "answer": "Yes",
            "category": "Science",
            "difficulty": 2,
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test for getting all categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_getcategories_404(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'The resource you requested was not found.')

    # Test for paginated questions
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
    
    # Test beyond paginated list of questions
    def test_get_paginated_questions_404(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['success'], 'The resource you requested was not found.')

    # Test delete questions
    def test_delete_question(self):
        res = self.client().delete("/questions/6")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 6).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)
    
    def test_delete_question_422(self):
        res = self.client().delete("/questions/200")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "The request you made was not processable.")
    # Test post new question
    def test_post_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])

        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_post_new_question_405(self):
        res = self.client().post("/questions/100", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "This method is not allowed, sorry.")
    
    # test search question
    def test_search_questions(self):
        res = self.client().post("/questions/search", json={"search": "title"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_questions_404(self):
        res = self.client().post("/questions/search", json={"search": "1"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "The resource you requested was not found.")
    
    # test Get questions by category
    def test_questions_with_category_id(self):
        res = self.client().get("/categories/<int:category_id>/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["current_category"], 2)

    def test_questions_with_category_id_not_found(self):
        res = self.client().get("/questions/100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "The resource you requested was not found.")
    
    # Test Quiz Play
    def test_play_quiz(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": ["1"],
                "quiz_category": {"type": "History", "id": 1},
            },
        )
        data = json.loads(res.data)

        quiz = Question.query.filter_by(category="1").all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

        self.assertTrue(data["question"])

    def test_play_quiz_if_not_quiz(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": ["100"],
                "quiz_category": {"type": "History", "id": 100},
            },
        )

        quiz = Question.query.filter_by(category="100").all()

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "The request you made was not processable.")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()