from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
import sys
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
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
@requires_auth('get:drinks')
def retrieve_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks,

        }
    )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-details')
# @requires_auth('get:drinks-details')
def retrieve_drinks_details():
    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks]
    print(drinks)

    if len(drinks) == 0:
        abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks,

        }
    )


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
# @requires_auth('post:drinks')
def add_drink():
    try:

        body = request.get_json()

        title = body.get("req_title", None)
        recipe = body.get("req_recipe", None)
        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify(
            {
                "success": True,
                "code": 201,

            }
        )

    except:
        print(sys.exc_info())
        abort(422)


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


@app.route('/drinks/<int:id>', methods=['PATCH'])
# @requires_auth('patch:drinks')
def edit_drink(id):
    try:
        body = request.get_json()
        title = body.get("req_title", None)
        recipe = body.get("req_recipe", None)
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.title = title
        drink.recipe = recipe
        drink.update()

        return jsonify(
            {
                "success": True,
                "drink": drink.long(),

            }
        )

    except:
        abort(422)


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

app.route('/drinks/<int:id>', methods=['DELETE'])
# @requires_auth('delete:drinks')


def delete_drink(id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.delete()

        return jsonify(
            {
                "success": True,
                "id": drink.id,

            }
        )

    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False,
                "error": 404,
                 "message": "resource not found"}),
        404,
    )


@app.errorhandler(400)
def bad_request(error):
    return (jsonify({"success": False,
                    "error": 400,
                     "message": "bad request"}),
            400,
            )


@app.errorhandler(405)
def not_allowed(error):
    return (
        jsonify({"success": False,
                 "error": 405,
                 "message": "method not allowed"}),
        405,

    )


@app.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({"success": False,
                 "error": 401,
                 "message": "Unauthorized"}),
        401,

    )


@app.errorhandler(403)
def forbidden(error):
    return (
        jsonify({"success": False,
                 "error": 403,
                 "message": "Forbidden"}),
        403,

    )


@app.errorhandler(500)
def bad_request(error):
    return (jsonify({"success": False,
                    "error": 500,
                     "message": "internal server error"}),
            500,
            )


@app.errorhandler(AuthError)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # replace the body with JSON
    response = jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error['code'],
        "description": e.error['description'],

    })
    return response
