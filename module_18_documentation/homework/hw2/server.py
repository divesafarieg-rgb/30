from flask import Flask
from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__)

@app.route('/api/test')
def test():
    return {"status": "OK", "message": "Hello World"}

if __name__ == '__main__':
    # WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(debug=False, use_reloader=False, port=5000)