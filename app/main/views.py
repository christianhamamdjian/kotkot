from flask import Flask,render_template, request, jsonify
from . import main


@main.route('/')
def index():
    return render_template('index.html')

