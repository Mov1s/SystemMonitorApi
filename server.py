from flask import Flask
from systemApi import api

app = Flask(__name__)
app.register_blueprint(api)
app.run(host='192.168.0.110', port=9000, debug=True)
