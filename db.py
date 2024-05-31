import os
from re import I
import psycopg2

def getConnection():
	return psycopg2.connect(host=os.environ.get("DB_HOST"), database = os.environ.get("DB_NAME"), user = os.environ.get("DB_USER"), password = os.environ.get("DB_PASS"))

def login(username, password):
	try:
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "SELECT * FROM Users WHERE username = %s AND password = crypt(%s, password)"
				cur.execute(query, [username, password])
				userRow = cur.fetchone()
				user = None
				if userRow is None:
					return None
				user = {
					"id": userRow[0],
					"username": userRow[3],
				}
	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
		return user

def user_exists(user):
    count = 0
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", [user["username"]])
                count = cur.rowcount
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
    return count > 0

def email_exists(user):
    count = 0
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", [user["email"]])
                count = cur.rowcount
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
    return count > 0


def get_user(id):
	try:
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "SELECT * FROM Users WHERE id = %s"
				cur.execute(query, [id])
				userRow = cur.fetchone()
				user = {
					"id": userRow[0],
					"name": userRow[1],
					"email": userRow[2],
					"username": userRow[3],
				}
	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
		return user

def add_user(user):
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "INSERT INTO Users (name, email, username, password) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf'))) RETURNING *"
                cur.execute(query, [user["name"], user["email"], user["username"], user["password"]])
                conn.commit()
                userRow = cur.fetchone()
                user_data = {
                    "id": userRow[0],
                    "name": userRow[1],
                    "email": userRow[2],
                    "username": userRow[3],
                }
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
    return user_data


def get_user_by_username(username):
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM Users WHERE username = %s"
                cur.execute(query, [username])
                user_row = cur.fetchone()
                if user_row:
                    return {
                        "id": user_row[0],
                        "name": user_row[1],
                        "email": user_row[2],
                        "username": user_row[3],
                    }
                else:
                    return None
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()

def get_user_by_email(email):
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM Users WHERE email = %s"
                cur.execute(query, [email])
                user_row = cur.fetchone()
                if user_row:
                    return {
                        "id": user_row[0],
                        "name": user_row[1],
                        "email": user_row[2],
                        "username": user_row[3],
                    }
                else:
                    return None
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
	

def change_user(id, user):
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "UPDATE Users SET name = %s, username = %s, email = %s WHERE id = %s RETURNING *"
                cur.execute(query, [user["name"], user["username"], user["email"], id])
                conn.commit()
                userRow = cur.fetchone()
                user = {
                    "id": userRow[0],
                    "name": userRow[1],
                    "email": userRow[2],
                    "username": userRow[3],
                }
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
        return user


def change_password(id, user):
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "UPDATE Users SET password = crypt(%s, gen_salt('bf')) WHERE id = %s RETURNING *"
                cur.execute(query, [user["password"], id])
                conn.commit()
                userRow = cur.fetchone()
                user = {
                    "id": userRow[0],
                    "name": userRow[1],
                    "email": userRow[2],
                    "username": userRow[3],
                }
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
        return user

def SavedRecipe_exists(id_recipe, id_user):
    count = 0
    try:        
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM SavedRecipe WHERE idrec = %s AND iduser = %s"
                cur.execute(query, [id_recipe, id_user])
                count = cur.rowcount
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
    return count > 0


def getRecipes(name_recipe):
    recipes = []
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM Recipe WHERE name ILIKE %s"
                cur.execute(query, ['%' + name_recipe + '%'])
                for recipe in cur.fetchall():
                    recipe = {
                        "id": recipe[0],
                        "name": recipe[1],
                        "preparation": recipe[2],
                        "prepTime": recipe[3],
                        "type": recipe[4],
                        "picture": recipe[5],
                        "ingredients": recipe[6],
                    }
                    recipes.append(recipe)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
    return recipes


def getAllRecipes():
    try:
        with getConnection() as conn:
            with conn.cursor() as cur:
                query="SELECT * FROM Recipe"
                cur.execute(query)
                recipes = []
                for recipe in cur.fetchall():
                    recipe = {
                        "id": recipe[0],
                        "name": recipe[1],
                        "preparation": recipe[2],
                        "prepTime": recipe[3],
                        "type": recipe[4],
                        "picture": recipe[5],
                        "ingredients": recipe[6],
                    }
                    recipes.append(recipe)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
    return recipes


def getSaved_recipes(id_user):
    try:        
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM SavedRecipe WHERE idUser = %s"
                cur.execute(query, [id_user])
                rows = cur.fetchall()
                recipes = []

                for recipe in rows:
                    recipe = {
                        "id": recipe[0],
                        "name": recipe[1],
                        "preparation": recipe[2],
                        "prepTime": recipe[3],
                        "type": recipe[4],
                        "picture": recipe[5],
                        "ingredients": recipe[6],
                        "id_recipe": recipe[7],
                    }
                    recipes.append(recipe)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
        return recipes


def add_recipe(recipe):
    try:        
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "INSERT INTO SavedRecipe (name, preparation, preptime, type, picture, ingredients, iduser, idrec) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *"
                cur.execute(query, [recipe["name"], recipe["preparation"], recipe["prepTime"], recipe["type"], recipe["picture"], recipe["ingredients"] ,recipe["idUser"], recipe["idRec"]])
                recipe = None
                recipe = cur.fetchone()

                recipe = {
                    "id": recipe[0],
                    "name": recipe[1],
                    "preparation": recipe[2],
                    "prepTime": recipe[3],
                    "type": recipe[4],
                    "picture": recipe[5],
                    "ingredients": recipe[6],
                    "id_user": recipe[7],
                    "id_recipe": recipe[8],
                    }
                conn.commit()
                return recipe
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()


def remove_recipe(id_recipe, idUser):
    try:        
        with getConnection() as conn:
            with conn.cursor() as cur:
                query = "DELETE FROM SavedRecipe WHERE id = %s AND iduser = %s "
                cur.execute(query, [id_recipe, idUser])
                conn.commit()

                value = None
                if cur.rowcount > 0:
                    value = cur.rowcount

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
        return value
