from website import app
from flask import Flask

if __name__ == '__main__':
    app.run(debug=True)

app=Flask(__name__,template_folder='templates')
