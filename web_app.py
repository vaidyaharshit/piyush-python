
from flask import Flask, render_template, request, redirect, url_for, flash
import database

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"

database.init_db()


@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    if search:
        contacts = database.search_contacts(search)
    else:
        contacts = database.get_all_contacts()

    stats = database.get_stats()
    return render_template(
        "index.html",
        contacts=contacts,
        stats=stats,
        search=search
    )


@app.route("/add", methods=["POST"])
def add():
    success, message, _ = database.add_contact(
        request.form.get("name", ""),
        request.form.get("phone", ""),
        request.form.get("email", ""),
        request.form.get("address", ""),
        request.form.get("notes", "")
    )
    flash(message, "success" if success else "error")
    return redirect(url_for("index"))


@app.route("/update/<int:contact_id>", methods=["POST"])
def update(contact_id):
    success, message = database.update_contact(
        contact_id,
        request.form.get("name", ""),
        request.form.get("phone", ""),
        request.form.get("email", ""),
        request.form.get("address", ""),
        request.form.get("notes", "")
    )
    flash(message, "success" if success else "error")
    return redirect(url_for("index"))


@app.route("/delete/<int:contact_id>", methods=["POST"])
def delete(contact_id):
    success, message = database.delete_contact(contact_id)
    flash(message, "success" if success else "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
