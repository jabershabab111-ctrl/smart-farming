from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            res = supabase.table("users").select("*").eq("email", email).execute()

            if not res.data:
                return "No account found."

            user = res.data[0]
            stored = user["password_hash"]

            ok = bcrypt.checkpw(
                password.encode(),
                stored.encode()
            )

            if ok:
                return redirect("/dashboard")
            else:
                return "Wrong password."

        except Exception as e:
            return f"Error: {e}"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/farmers")
def farmers():
    res = supabase.table("users").select("*").execute()
    return render_template("farmers.html", farmers=res.data)


@app.route("/fields")
def fields():
    res = supabase.table("fields").select("*").execute()
    return render_template("fields.html", fields=res.data)

@app.route("/crops")
def crops():
    res = supabase.table("crops").select("*").execute()
    return render_template("crops.html", crops=res.data)


@app.route("/sensors")
def sensors():
    res = supabase.table("sensors").select("*").execute()
    return render_template("sensors.html", sensors=res.data)


@app.route("/irrigation")
def irrigation():
    res = supabase.table("irrigation_logs").select("*").execute()
    return render_template("irrigation.html", irrigation=res.data)


if __name__ == "__main__":
    app.run(debug=True)