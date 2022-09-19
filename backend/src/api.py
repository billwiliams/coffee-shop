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


@app.route('/drinks')
def retrieve_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    return jsonify(
        {
            "success": True,
            "drinks": drinks

        }
    ), 200


# Get dring details

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    drinks = Drink.query.all()

    drinks = [drink.long() for drink in drinks]

    return jsonify(
        {
            "success": True,
            "drinks": drinks

        }
    ), 200


# Create a drink

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:

        body = request.get_json()

        title = body.get("title", None)
        recipe = body.get("recipe", None)

        drink = Drink(title=title,
                      recipe=json.dumps(recipe))
        drink.insert()

        return jsonify(
            {
                "success": True,
                "code": 201,

            }
        )

    except:

        abort(422)

# Update a Drink


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify(
            {
                "success": True,
                "drink": [drink.long()],

            }
        )

    except:
        abort(422)

# Delete a drink


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
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

# Return Json format for Auth Errors


@app.errorhandler(AuthError)
def handle_exception(error):
    """Return JSON instead of HTML for HTTP errors."""
    # replace the body with JSON
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']

    }), error.status_code
