from flask import Flask
from flask import render_template
from static.user_model.Final_Project import write_html

app = Flask(__name__)
write_html()

@app.route("/")
def home():
    return render_template("./index.html")
app.debug = True
app.run()