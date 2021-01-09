import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
# paginate questions helper function


def paginate(request, list):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in list]
    display_questions = questions[start:end]
    return display_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        thecategories = Category.query.all()
        categoryTypes = {
            category.id: category.type for category in thecategories}
        return jsonify({
            'success': True,
            'categories': categoryTypes
        })

    @app.route('/questions')
    def get_questions():
        question_list = Question.query.all()
        category_list = Category.query.all()
        formatted_questions = [question.format() for question in question_list]
        formatted_categories = {
            category.id: category.type for category in category_list}
        questions_paginated = paginate(request, question_list)
        if not len(questions_paginated):
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions_paginated,
            'total_questions': len(formatted_questions),
            'categories': formatted_categories
        })

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            deleted = Question.query.get(question_id)
            if not deleted:
                abort(404)
            deleted.delete()
            return jsonify({
                'success': True
            })
        except BaseException:
            import traceback
            traceback.print_exc()
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            new_question = Question(
                question=request.json.get('question', ''),
                answer=request.json.get('answer', ''),
                category=request.json.get('category', ''),
                difficulty=request.json.get('difficulty', '')
            )
            new_question.insert()
            return jsonify({
                "success": True
            })
        except BaseException:
            abort(405)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        try:
            search_term = request.json.get('searchTerm')
            question_search_list = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            if not question_search_list:
                abort(404)
            formatted_search = [question.format()
                                for question in question_search_list]
            questions_paginated = paginate(request, question_search_list)
            category_list = Category.query.all()
            category_types = {
                category.id: category.type for category in category_list}
            return jsonify({
                'success': True,
                'questions': questions_paginated,
                'total_questions': len(formatted_search),
                'categories': category_types
            })
        except BaseException:
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
        try:
            question_search_list = Question.query.filter(
                Question.category == category_id).all()
            if not question_search_list:
                abort(404)
            formatted_search = [question.format()
                                for question in question_search_list]
            category_list = Category.query.all()
            category_types = {
                category.id: category.type for category in category_list}
            questions_paginated = paginate(request, question_search_list)
            return jsonify({
                'success': True,
                'questions': questions_paginated,
                'total_questions': len(formatted_search),
                'categories': category_types,
                "current_category": category_id
            })
        except BaseException:
            abort(500)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            previous_questions = request.json.get('previous_questions')
            quiz_category = request.json.get('quiz_category')
            if quiz_category['type'] == 'click':
                questions = Question.query.all()
                formatted_search = [question.format()
                                    for question in questions]
            else:
                questions = Question.query.filter(
                    Question.category == quiz_category['id']).filter(
                    Question.id.notin_(previous_questions)).all()
                formatted_search = [question.format()
                                    for question in questions]
                if questions:
                    random_question = random.choice(formatted_search)
                else:
                    abort(422)
            return jsonify({
                'success': True,
                'question': random_question
            })
        except BaseException:
            abort(422)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "error": 500,
            "message": "There's a problem with the server."
        }), 500

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "The resource you requested was not found."
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "The request you made was not processable."
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": 400,
            "message": "You made a bad request."
        }), 400

    @app.errorhandler(405)
    def method_not_request(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "This method is not allowed, sorry."
        }), 405

    return app
