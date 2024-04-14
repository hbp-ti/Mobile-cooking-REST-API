import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
import psycopg2
from flask import Flask, jsonify, request

import db

app = Flask(__name__)
app.debug = True

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

if __name__ == "__main__":
    app.run()
