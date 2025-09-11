#!/usr/bin/env python3
"""
Ultra-simple test server to debug Flask issues
"""
from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Test Server Working</h1><p><a href='/api/test'>Test API</a></p>"

@app.route('/api/test')
def api_test():
    return json.dumps({"status": "working", "message": "API is functional"})

if __name__ == '__main__':
    print("Starting test server on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
