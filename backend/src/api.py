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
# db_drop_and_create_all()

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
def post_drinks():
    input = request.get_json()
    result = []
    if input != None:
        drink = Drink(title=input['title'], recipe=input['recipe'])
        drink.insert()
        result = [drink.long()]
    else:
        abort(422)

    return jsonify({"success": True, "drinks": result}), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id_num>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink():
    return jsonify({"success": True, "drinks": []}), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id_num>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id_num):
    return jsonify({"success": True, "delete": 0}), 200


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