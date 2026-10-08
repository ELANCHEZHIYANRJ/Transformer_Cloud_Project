import os
from flask import Flask, send_from_directory

app = Flask(__name__)

# The simplest possible route to serve your index.html file
@app.route('/')
def home():
    # Looks for index.html in the exact same directory where this server.py file runs
    current_folder = os.getcwd()
    return send_from_directory(current_folder, 'index.html')

if __name__ == '__main__':
    # Dynamically reads the environment port provided by Render to prevent deployment crashes
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
