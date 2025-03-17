from flask import Flask, request, render_template, redirect, url_for
import json
import os
app = Flask(__name__)

def load_questions():
    with open("questions.json","r",encoding="utf-8")as file:
        return json.load(file)
questions = load_questions()

STUDENT_FILE = "students.txt"

def load_students():
    try:
        with open(STUDENT_FILE, "r") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_student(name):
    with open(STUDENT_FILE, "a") as file:
        file.write(name + "\n")

@app.route("/", methods=["GET", "POST"])
def login():
    student_name = ""  # مقداردهی اولیه برای جلوگیری از UnboundLocalError

    if request.method == "POST":
        student_name = request.form.get("name", "").strip()

        if not student_name:
            return render_template("login.html", error="Please enter your name.")

        students = load_students()
        if student_name in students:
            return render_template("login.html", error="This name is already taken. Try another.")

        save_student(student_name)
        return redirect(url_for("exam_info", student=student_name))

    return render_template("login.html")  # در درخواست GET، فقط صفحه را نمایش بده

@app.route("/exam_info")
def exam_info():
    return render_template("exam_info.html")
@app.route("/exam")
def exam():
    questions =load_questions()
    return render_template("exam.html",questions=questions)
SCORES_FILE = "scores.json"  # مسیر فایل ذخیره نمرات

def load_scores():
    """ نمرات را از فایل بخواند و برگرداند """
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return []

def save_scores(scores):
    """ نمرات را در فایل ذخیره کند """
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=4)

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    global questions
    scores = load_scores()  # دریافت نمرات قبلی

    score = 0
    total_questions = len(questions)

    for question in questions:
        q_id = f"q{question['id']}"
        user_answer = request.form.get(q_id, "")
        if user_answer == question['correct_option']:
            score += 1

    # دریافت نام دانش‌آموز
    student_name = request.form.get("student_name", "Anonymous")

    # ذخیره نمره جدید
    scores.append({"name": student_name, "score": score})

    # مرتب کردن لیست بر اساس نمرات از بالا به پایین
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)

    # ذخیره در فایل
    save_scores(scores)
    print(scores)
    return render_template('result.html', student_name=student_name, student_score=score, scores=scores, total=total_questions)



if __name__ == "__main__":
    app.run(debug=True)