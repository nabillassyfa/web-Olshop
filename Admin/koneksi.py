from flask import Flask, redirect, render_template, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['utsolshop']