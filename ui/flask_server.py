from flask import Flask
import importlib.util
spec = importlib.util.spec_from_file_location("main", "../src/main.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

app = Flask(__name__)

# @app.route('/')
# def home():
  # return "Flask server"

@app.route('/flask', methods=['GET'])
def index():
  return script.main()

if __name__ == "__main__":
  app.run(port=7000, debug=True)
