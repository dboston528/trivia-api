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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  cors = CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    thecategories = Category.query.all()
    categoryTypes = {category.id: category.type for category in thecategories}
    return jsonify({
      'success': True,
      'categories': categoryTypes
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    question_list = Question.query.all()
    category_list = Category.query.all()
    formatted_questions = [question.format() for question in question_list]
    formatted_categories = {category.id: category.type for category in category_list}
    questions_paginated = paginate(request, question_list)
    if not len(questions_paginated):
     abort(404) 

    return jsonify({
      'success': True,
      'questions': questions_paginated,
      'total_questions': len(formatted_questions),
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      deleted = Question.query.get(question_id)
      if not deleted:
        abort(404)
      deleted.delete()
      return jsonify({
        'success':True
      })
    except:
      import traceback
      traceback.print_exc()
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      new_question = Question(
        question = request.json.get('question', ''),
        answer = request.json.get('answer', ''),
        category = request.json.get('category', ''),
        difficulty =  request.json.get('difficulty','')
      )
      new_question.insert()
      return jsonify({
        'success': True
      })
    except:
      abort(405)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    try:
      search_term = request.json.get('searchTerm')
      question_search_list = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if not question_search_list:
        abort(404)
      formatted_search = [question.format() for question in question_search_list]
      questions_paginated = paginate(request, question_search_list)
      category_list = Category.query.all()
      category_types = [category.type for category in category_list]
      return jsonify({
        'success':True,
        'questions': questions_paginated,
        'total_questions': len(formatted_search),
        'categories': category_types
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    try:
      question_search_list = Question.query.filter(Question.category == category_id).all()
      formatted_search = [question.format() for question in question_search_list]
      category_list = Category.query.all()
      category_types = [category.type for category in category_list]
      questions_paginated = paginate(request, question_search_list)
      return jsonify({
        'success':True,
        'questions': questions_paginated,
        'total_questions': len(formatted_search),
        'categories': category_types
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      previous_questions = request.json.get('previous_questions')
      quiz_category = request.json.get('quiz_category')
      if quiz_category['type'] == 'click':
        questions = Question.query.all()
        formatted_search = [question.format() for question in questions]
      else:
        questions = Question.query.filter(Question.category == quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()
        formatted_search = [question.format() for question in questions]
      random_question = random.choice(formatted_search) if questions else None
      return jsonify({
        'success': True,
        'question': random_question
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "error": 500,
      "message": "There's a problem with the server."
    }, 500)
  
  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({
      "error": 404,
      "message": "The resource you requested was not found."
    }, 404)
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "error": 422,
      "message": "The request you made was not processable."
    }, 422)
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "error": 400,
      "message": "You made a bad request."
    }, 400)
  
  
  
  return app

    