from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from dotenv import load_dotenv
import json
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")  # Convert to int
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS")  # Convert to bool
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)

@app.route("/")
def home():
    reviews_path = os.path.join(app.root_path, 'reviews.json')
    with open(reviews_path, 'r', encoding='utf-8') as file:
        reviews = json.load(file)
    return render_template("index.html", reviews=reviews)

@app.route('/schedule_call', methods=['POST'])
def schedule_call():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    place = request.form.get('place')
    program = request.form.get('program')
    # Here, you could save to a database, send email, etc.
    # For now, just flash a message and redirect to home
    # Compose the email
    body = f"""
    New 1:1 Call Request

    Name: {name}
    Email: {email}
    Phone: {phone}
    Place/City: {place}
    Intended Study Program: {program}
    """

    try:
        msg = Message("New 1:1 Call Request", recipients=["sadiqali@zhcet.ac.in"])
        msg.body = body
        mail.send(msg)
        flash("Your call request has been submitted!", "success")
    except Exception as e:
        print("Email send failed:", e)
        flash("Failed to send your request. Please try again later.", "danger")

    return redirect(url_for('home'))
    # flash("Your call request has been submitted!", "success")
    # return redirect(url_for('home'))

@app.route("/ects-calculator", methods=["GET", "POST"])
def ects_calculator():
    if request.method == "POST":
        # Save result to session (temporarily)
        try:
            max_grade = request.form["maxGrade"]
            min_grade = request.form["minGrade"]
            curr_grade = request.form["currGrade"]
            max_grade_f = float(max_grade)
            min_grade_f = float(min_grade)
            curr_grade_f = float(curr_grade)
            if max_grade_f <= min_grade_f or curr_grade_f < min_grade_f or curr_grade_f > max_grade_f:
                session['error'] = "Please enter valid grade values."
            else:
                session['german_grade'] = round(((max_grade_f - curr_grade_f) * 3 / (max_grade_f - min_grade_f)) + 1, 1)
                session['max_grade'] = max_grade
                session['min_grade'] = min_grade
                session['curr_grade'] = curr_grade
        except Exception:
            session['error'] = "Please enter all grades correctly."
        return redirect(url_for("ects_calculator"))

    # On GET, show result if present, then clear session (so refresh clears everything)
    german_grade = session.pop('german_grade', None)
    error = session.pop('error', None)
    max_grade = session.pop('max_grade', "")
    min_grade = session.pop('min_grade', "")
    curr_grade = session.pop('curr_grade', "")
    return render_template(
        "ects_calculator.html",
        max_grade=max_grade,
        min_grade=min_grade,
        curr_grade=curr_grade,
        german_grade=german_grade,
        error=error
    )

@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")

@app.route('/submit-form', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    body = f"""
    New Contact Message

    Name: {name}
    Email: {email}
    Message:
    {message}
    """

    try:
        msg = Message("New Contact Message", recipients=["sadiqali@zhcet.ac.in"])  # Change to your email
        msg.body = body
        mail.send(msg)
        flash("Your message has been sent!", "success")
    except Exception as e:
        print("Email send failed:", e)
        flash("Failed to send your message. Please try again later.", "danger")

    return redirect(url_for('contact'))  # Use the correct route for your contact page

@app.route('/contact', methods=['GET'])
def contact():
    return render_template("contactus.html")

@app.route('/pricing', methods=['GET'])
def pricing():
    return render_template("pricing.html", custom_css="/static/pricing.css")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)  # Debug mode for auto-reload