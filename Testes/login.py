from flask import Flask, redirect, url_for, render_template
from flask_dance.contrib.google import make_google_blueprint, google
#import os 

#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Configuração do blueprint do Google
blueprint = make_google_blueprint(
    client_id="",
    client_secret="",
    scope=["profile", "email"],
)

app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login")
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    email = resp.json()["email"]
    return f"Logged in as {email}"

if __name__ == "__main__":
    app.run(debug=True)
