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