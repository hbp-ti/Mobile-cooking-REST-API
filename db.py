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
					"username": userRow[5],
				}
	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
		return user

def user_exists(user):
	try:
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "SELECT COUNT(*) FROM Users WHERE username = %s"
				cur.execute(query, [user["username"]])
				count = cur.rowcount
	except (Exception, psycopg2.Error) as error:
		print ("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
	return count > 0

def get_user(username):
	try:
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "SELECT * FROM Users WHERE username = %s"
				cur.execute(query, [username])
				userRow = cur.fetchone()
				user = {
					"id": userRow[0],
					"name": userRow[1],
					"email": userRow[2],
					"username": userRow[3],
					"password": userRow[4],
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
				user = {
					"id": userRow[0],
					"name": userRow[1],
					"email": userRow[2],
				}
	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
		return user



def getRecipe(id_recipe):
	try:
		with getConnection() as conn:
			with conn.cursor() as cur:
				query="SELECT * FROM Recipe WHERE id = %s"
				cur.execute(query, [id_recipe])
				recipe = cur.fetchone()

				recipe = {
					"id": recipe[0],
					"name": recipe[1],
					"preparation": recipe[2],
					"prepTime": recipe[3],
					"type": recipe[4],
					"picture": recipe[5],
					"ingredients": recipe[6],
				}

	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
		return recipe


def getSaved_recipes(id_user):
	try:		
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "SELECT * FROM SavedRecipe WHERE idUser = %s"
				cur.execute(query, [id_user])
				rows = cur.fetchall()
				recipes = None

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
				return recipes
	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()


def add_recipe(recipe):
	try:		
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "INSERT INTO SavedRecipe VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *"
				cur.execute(query, [recipe["id"], recipe["name"], recipe["preparation"], recipe["prepTime"], recipe["type"], recipe["picture"], recipe["idUser"], recipe["idRec"]])
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
	finally:
		if conn:
			cur.close()
			conn.close()

def remove_recipe(id_recipe):
	try:		
		with getConnection() as conn:
			with conn.cursor() as cur:
				query = "DELETE FROM SavedRecipe WHERE id = %s"
				cur.execute(query, [id_recipe])
				conn.commit()

				value = None
				if cur.rowcount > 0:
				    value = cur.rowcount

	except (Exception, psycopg2.Error) as error:
		print("Error while connecting to PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
		return value