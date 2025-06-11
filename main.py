from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Welcome to your simple Flask API!"}

@app.route("/hello/<name>")
def hello(name):
    return {"message": f"Hello, {name}!"}

@app.route("/add")
def add():
    a = int(request.args.get("a", 5))
    b = int(request.args.get("b", 11))
    return {"result": a + b}

if __name__ == "__main__":
    app.run(debug=True)