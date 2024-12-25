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

# Uncomment the following line to initialize the database (drops all records and starts fresh)
db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    Public endpoint to get all drinks with short() representation.
    """
    try:
        drinks = Drink.query.all()
        drinks_short = [drink.short() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": drinks_short
        }), 200
    except Exception as e:
        abort(500)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    Requires 'get:drinks-detail' permission.
    Returns all drinks with long() representation.
    """
    try:
        drinks = Drink.query.all()
        drinks_long = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": drinks_long
        }), 200
    except Exception as e:
        abort(500)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    Requires 'post:drinks' permission.
    Creates a new drink in the database.
    """
    body = request.get_json()

    if not body:
        abort(400, description="Request does not contain a valid JSON body.")

    title = body.get('title')
    recipe = body.get('recipe')

    if not title or not recipe:
        abort(400, description="Title and recipe are required.")

    try:
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)  # Ensure recipe is stored as JSON
        )
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except exc.IntegrityError:
        abort(400, description="Drink with this title already exists.")
    except Exception as e:
        abort(500)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    """
    Requires 'patch:drinks' permission.
    Updates an existing drink in the database.
    """
    body = request.get_json()

    if not body:
        abort(400, description="Request does not contain a valid JSON body.")

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404, description=f"Drink with ID {id} not found.")

    title = body.get('title')
    recipe = body.get('recipe')

    try:
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception as e:
        abort(500)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    """
    Requires 'delete:drinks' permission.
    Deletes an existing drink from the database.
    """
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404, description=f"Drink with ID {id} not found.")

    try:
        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except Exception as e:
        abort(500)


# Error Handling

@app.errorhandler(404)
def not_found(error):
    """
    Error handler for 404 - Resource Not Found.
    """
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    """
    Error handler for 400 - Bad Request.
    """
    return jsonify({
        "success": False,
        "error": 400,
        "message": str(error.description if hasattr(error, 'description') else "Bad request")
    }), 400


@app.errorhandler(422)
def unprocessable(error):
    """
    Error handler for 422 - Unprocessable Entity.
    """
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable entity"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    """
    Error handler for 500 - Internal Server Error.
    """
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


@app.errorhandler(AuthError)
def auth_error_handler(error):
    """
    Error handler for authentication errors.
    """
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description', 'Authentication error')
    }), error.status_code
