from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Python  اهلا وسهلا بك في موقع عبد خالق ..!"

if __name__ == "__main__":
    app.run()