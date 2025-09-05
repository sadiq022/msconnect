from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from dotenv import load_dotenv
import json
import os
from blog_data import blog_posts

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

@app.route("/grade-calculator", methods=["GET", "POST"])
def grade_calculator():
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
        return redirect(url_for("grade_calculator"))

    # On GET, show result if present, then clear session (so refresh clears everything)
    german_grade = session.pop('german_grade', None)
    error = session.pop('error', None)
    max_grade = session.pop('max_grade', "")
    min_grade = session.pop('min_grade', "")
    curr_grade = session.pop('curr_grade', "")
    return render_template(
        "grade_calculator.html",
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

@app.route('/services/sop-writing')
def sop_writing():
    return render_template('service_sop.html', custom_css="/static/services.css")

@app.route('/services/university-shortlisting')
def university_shortlisting():
    return render_template('service_university_shortlisting.html', custom_css="/static/services.css")

@app.route('/services/lor-writing')
def lor_writing():
    return render_template('service_LOR.html', custom_css="/static/services.css")

@app.route('/services/cv-preparation')
def cv_prepare():
    return render_template('service_cv.html', custom_css="/static/services.css")

@app.route('/services/visa-sop')
def visa_sop():
    return render_template('service_visa_sop.html', custom_css="/static/services.css")

@app.route('/services/visa-cover-letter')
def visa_cover_letter():
    return render_template('service_cover_letter.html', custom_css="/static/services.css")

@app.route('/shop')
def shop():
    return render_template('shop.html', custom_css='/static/shop.css')

@app.route('/blog')
def blog():
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/blog/post/<int:post_id>')
def blog_post(post_id):
    # Find the post with the matching ID
    post = next((p for p in blog_posts if p['id'] == post_id), None)
    
    if post:
        return render_template('blog-post.html', post=post)
    else:
        # Post not found - redirect to blog listing
        return redirect(url_for('blog'))

@app.route('/ects-calculator', methods=['GET', 'POST'])
def ects_calculator():
    ects = None
    error = None
    lecture_hours = self_study_hours = weeks = None
    if request.method == 'POST':
        try:
            lecture_hours = float(request.form.get('lecture_hours'))
            self_study_hours = float(request.form.get('self_study_hours'))
            weeks = float(request.form.get('weeks'))
            if lecture_hours < 0 or self_study_hours < 0 or weeks <= 0:
                error = "Please enter valid (positive) values for all fields."
            else:
                total_hours = (lecture_hours + self_study_hours) * weeks
                ects = round(total_hours / 30, 2)   # Only 30, as per Germany
        except Exception:
            error = "Please enter valid numbers."
    return render_template(
        "ects_calculator.html",
        custom_css="/static/ects_calculator.css",
        ects=ects,
        error=error,
        lecture_hours=request.form.get('lecture_hours'),
        self_study_hours=request.form.get('self_study_hours'),
        weeks=request.form.get('weeks')
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)  # Debug mode for auto-reload