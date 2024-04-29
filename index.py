import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
import psycopg2
from flask import Flask, jsonify, request

import db

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')

NOT_FOUND_CODE = 401
OK_CODE = 200
SUCCESS_CODE = 201
NO_CONTENT_CODE = 204
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
NOT_FOUND = 404
SERVER_ERROR = 500

@app.route('/', methods = ["GET"])
def home():
    return "Welcome to API!"


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    user = db.login(data['username'], data["password"])

    if user is None:
        return jsonify({"error": "Check credentials"}), NOT_FOUND_CODE

    token = jwt.encode(
        {'user_id': user['id'], 'exp': datetime.utcnow() + timedelta(minutes=40)}, app.config['SECRET_KEY'], 'HS256')

    user["token"] = token.decode('UTF-8')
    #user["token"] = token
    return jsonify(user), OK_CODE


@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()

    if "name" not in data or "email" not in data or "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if (db.user_exists(data)):
        return jsonify({"error": "User already exists"}), BAD_REQUEST_CODE

    #if (db.email_exists(data)):
    #    return jsonify({"error": "Email already exists"}), BAD_REQUEST_CODE

    user = db.add_user(data)

    return jsonify(user), SUCCESS_CODE


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "Authorization" not in request.headers:
            return jsonify({"error": "Token not provided"}), FORBIDDEN_CODE

        token = request.headers['Authorization']
        # Remove Bearer from token
        token = token.split(' ')[1]

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado", "expired": True}), UNAUTHORIZED_CODE
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), FORBIDDEN_CODE

        request.user = db.get_user(data['user_id'])

        return f(*args, **kwargs)

    return decorated


@app.route("/changeUser/<int:id_user>", methods=['PUT'])
@auth_required
def update_user(id_user):
    data = request.get_json()

    if "name" not in data or "email" not in data or "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if (db.user_exists(data)):
        return jsonify({"error": "user already exists"}), BAD_REQUEST_CODE

    if (db.email_exists(data)):
        return jsonify({"error": "email already exists"}), BAD_REQUEST_CODE

    user = db.change_user(id_user, data)

    return jsonify(user), SUCCESS_CODE


@app.route("/getUser/<string:username>", methods=['GET'])
@auth_required
def get_user(username):
    user = db.get_user(username)

    if user is None:
        return jsonify({"Error": "No user found"}), NOT_FOUND_CODE
    
    return jsonify(user), OK_CODE


@app.route("/getRecipe/<int:id_recipe>", methods=['GET'])
@auth_required
def get_recipe(id_recipe):
    recipe = db.getRecipe(id_recipe)

    if recipe is None:
        return jsonify({"Error": "No Recipe found"}), NOT_FOUND_CODE
    
    return jsonify(recipe), OK_CODE


@app.route("/getSavedRecipes_user/<int:id_user>", methods=['GET'])
@auth_required
def get_recipes(id_user):
    recipes = db.getSaved_recipes(id_user)

    if recipes is None:
        return jsonify({"Error": "No saved recipes found in this user"}), NOT_FOUND_CODE
    
    return jsonify(recipes), OK_CODE


@app.route("/addRecipe", methods=['POST'])
@auth_required
def add_saved_recipe():
    data = request.get_json()

    if "name" not in data or "preparation" not in data or "prepTime" not in data or "type" not in data or "picture" not in data or "ingredients" not in data or "idUser" not in data or "idRec" not in data:
        return jsonify({"Error": "Invalid parameters"}), BAD_REQUEST_CODE

    recipe = db.add_recipe(data)

    return jsonify(recipe), SUCCESS_CODE


@app.route('/deleteRecipe/<int:recipe_id>', methods=['DELETE'])
@auth_required
def delete_saved_recipe(recipe_id):
    if db.remove_recipe(recipe_id):
        return jsonify({"message": "Recipe removed with success"}), OK_CODE
    else:
        return jsonify({"error": "Recipe not found"}), FORBIDDEN_CODE


if __name__ == "__main__":
    app.run()
