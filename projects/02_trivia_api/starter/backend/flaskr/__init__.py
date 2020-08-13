import os
from flask import Flask, request, abort, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
      return response

  @app.route('/')
  def index():
    return app.send_static_file('index.html')
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categories_array = {}
    for category in categories:
        categories_array[category.id] = category.type
    if (len(categories_array) == 0):
        abort(404)
    return jsonify({
        'success': True,
        'categories': categories_array
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
      questions = Question.query.all()
      total_questions = len(questions)
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * 10
      end = start + 10
      questions_paging = [question.format() for question in questions]
      current_questions = questions_paging[start:end]
      categories = Category.query.all()
      categories_array = {}
      for category in categories:
          categories_array[category.id] = category.type
      if (len(current_questions) == 0):
          abort(404)
      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': total_questions,
          'categories': categories_array
        })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['GET','DELETE'])
  def delete_question(id):
      try:
          question = Question.query.filter_by(id=id).one_or_none()
          if question is None:
              abort(404)
          question.delete()
          return jsonify({
              'success': True,
              'deleted': id
          })
      except:
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
  def create_question():
      body = request.get_json()
      if (body.get('searchTerm',None)):
          search_term = body.get('searchTerm',None)
          questions = Question.query.filter(
              Question.question.ilike(f'%{search_term}%')).all()
          if (len(questions) == 0):
              abort(404)
          page = request.args.get('page', 1, type=int)
          start = (page - 1) * 10
          end = start + 10
          questions_paging = [question.format() for question in questions]
          current_questions = questions_paging[start:end]
          return jsonify({
              'success': True,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
          })
      else:
          current_question = body.get('question',None)
          current_answer = body.get('answer',None)
          current_difficulty = body.get('difficulty',None)
          current_category = body.get('category',None)
          if ((current_question is None) or (current_answer is None)
                  or (current_ifficulty is None) or (current_category is None)):
              abort(422)
          try:
              question = Question(question=current_question, answer=current_answer,
                                  difficulty=current_difficulty, category=current_category)
              question.insert()
              questions = Question.query.order_by(Question.id).all()
              page = request.args.get('page', 1, type=int)
              start = (page - 1) * 10
              end = start + 10
              questions_paging = [question.format() for question in questions]
              current_questions = questions_paging[start:end]
              return jsonify({
                  'success': True,
                  'created': question.id,
                  'question_created': question.question,
                  'questions': current_questions,
                  'total_questions': len(Question.query.all())
              })
          except:
              abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
      questions = Question.query.filter(Question.category == category_id).all()
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * 10
      end = start + 10
      questions_paging = [question.format() for question in questions]
      current_questions = questions_paging[start:end]
      if len(current_questions) < 1:
          return abort(404)
      return jsonify({
          "success": True,
          "questions": current_questions,
          "total_questions": len(questions),
          "current_category": category_id
      })

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
  @app.route('/quizzes', methods=['GET','POST'])
  def get_guesses():
    body = request.get_json()
    if not body:
        abort(400)
    if (body.get('previous_questions') is None or body.get('quiz_category') is None):
        abort(400)
    previous_questions = body.get('previous_questions')
    if type(previous_questions) != list:
        abort(400)
    category = body.get('quiz_category')
    category_id = category['id']
    if category_id == 0:
        randomQuestion = Question.query.order_by(func.random())
    else:
        randomQuestion = Question.query.filter(
            Question.category == category_id).order_by(func.random())
    if not randomQuestion.all():
        abort(404)
    else:
        quest = randomQuestion.filter(Question.id.notin_(
            previous_questions)).first()
    if quest is None:
        return jsonify({
            'success': True
        })
    return jsonify({
        'success': True,
        'question': quest.format()
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "sever error"
      }), 500

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  return app

    