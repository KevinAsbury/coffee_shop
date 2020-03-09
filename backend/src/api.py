import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    if len(all_drinks) == 0:
        abort(404)
    drinks = [drink.short() for drink in all_drinks]
    return jsonify({"success": True, "drinks": drinks}), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    all_drinks = Drink.query.all()
    if len(all_drinks) == 0:
        abort(404)
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({"success": True, "drinks": drinks}), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(token):
    if 'post:drinks' not in token.get('permissions'):
        abort(401)
    result = []

    input = request.get_json()
    recipe = input.get('recipe', '')

    if input != None:
        drink = Drink(title=input.get('title', ''), recipe=json.dumps(recipe))
        drink.insert()
        result = [drink.long()]
    else:
        abort(422)

    return jsonify({"success": True, "drinks": result}), 200


@app.route('/drinks/<int:id_num>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id_num):
    drink = Drink.query.get(id_num)

    if drink == None:
        abort(404)
    
    data = request.get_json()

    if data == None:
        abort(422)

    drink.title = data['title']
    drink.recipe = data['recipe']
    drink.update()

    return jsonify({"success": True, "drinks": [drink.long()]}), 200


@app.route('/drinks/<int:id_num>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id_num):
    drink = Drink.query.get(id_num)

    if drink == None:
        abort(404)

    drink.delete()
    return jsonify({"success": True, "delete": id_num}), 200


## Error Handling
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "forbidden"
                    }), 403


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