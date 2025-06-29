import os
print("Database file path:", os.path.abspath('your_database.db'))

import requests 
from flask import Flask, request,jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session 
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # ใช้สำหรับ session
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='phumiphatasunee478@gmail.com',          # Gmail ของคุณ
    MAIL_PASSWORD='wmxu aukn mmdw abbj'     # App Password ที่ได้
)   


API_KEY = "H2fktarAnLlNSuZjSzrs3ba3AWiZshu4"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # จะได้ path ของโฟลเดอร์ที่ไฟล์นี้อยู่ (คือ Time-hack)
DATABASE = os.path.join(BASE_DIR, 'users.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ----------- สร้างตารางผู้ใช้ ----------
def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                points INTEGER DEFAULT 0
            )
        ''')
        db.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                skill_name TEXT,
                minutes INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')
        db.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                is_done BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                skill TEXT,
                target_minutes INTEGER,
                points INTEGER
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                email TEXT PRIMARY KEY,
                otp TEXT,
                expires_at DATETIME
            )
        ''')
        db.commit()

init_db()
# ----------------------------------------

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        gender = request.form['gender']
        age = request.form['age']

        with get_db() as db:
            try:
                db.execute(
                    "INSERT INTO users (username, email, password, gender, age) VALUES (?, ?, ?, ?, ?)",
                    (username, email, password, gender, age)
                )
                db.commit()
                flash("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "success")
                return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError:
                flash("ชื่อผู้ใช้หรืออีเมลนี้ถูกใช้ไปแล้ว", "danger")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash("เข้าสู่ระบบสำเร็จ", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("กรุณาเข้าสู่ระบบก่อน", "warning")
        return redirect(url_for('login'))

    db = get_db()
    user = db.execute("SELECT points FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    points = user['points'] if user['points'] is not None else 0

    return render_template('dashboard.html', points=points)


@app.route('/logout')
def logout():
    session.clear()
    flash("ออกจากระบบเรียบร้อยแล้ว", "info")
    return redirect(url_for('login'))

def update_user_points(username):
    db = get_db()
    
    # ดึงชาเลนจ์ทั้งหมด
    challenges = db.execute("SELECT * FROM challenges").fetchall()
    
    # รวมเวลาที่ user ทำในแต่ละ skill
    skill_data = db.execute("""
        SELECT skill_name, SUM(minutes) AS total_minutes
        FROM activities
        WHERE username = ?
        GROUP BY skill_name
    """, (username,)).fetchall()

    skill_map = {row['skill_name']: row['total_minutes'] for row in skill_data}

    total_points = 0
    for ch in challenges:
        done_minutes = skill_map.get(ch['skill'], 0)
        if done_minutes >= ch['target_minutes']:
            total_points += ch['points']
    
    # อัพเดตคะแนนรวมในตาราง users
    db.execute("UPDATE users SET points = ? WHERE username = ?", (total_points, username))
    db.commit()


@app.route('/log_activity', methods=['POST'])
def log_activity():
    if 'username' not in session:
        flash("กรุณาเข้าสู่ระบบก่อน", "warning")
        return redirect(url_for('login'))

    data = request.get_json()
    skill = data.get('skill')
    minutes = data.get('minutes')

    with get_db() as db:
        db.execute(
            "INSERT INTO activities (username, skill_name, minutes) VALUES (?, ?, ?)",
            (session['username'], skill, minutes)
        )
        db.commit()

    update_user_points(session['username'])  # คำนวณคะแนนใหม่หลังเพิ่มกิจกรรม

    return jsonify({'status': 'success'})
    
from datetime import datetime, timedelta
def format_thai_date(date):
    months_th = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    return f"{date.day} {months_th[date.month - 1]} {date.year + 543}"

from datetime import datetime, timedelta

@app.route('/statistic')
def statistic():
    if 'username' not in session:
        flash("กรุณาเข้าสู่ระบบก่อน", "warning")
        return redirect(url_for('login'))

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week_str = start_of_week.strftime('%d %b %Y')

    with get_db() as db:
        # ดึงข้อมูลกิจกรรมตาม skill
        rows = db.execute("""
            SELECT skill_name, SUM(minutes) AS total_minutes
            FROM activities
            WHERE username = ?
            AND DATE(timestamp) >= DATE(?)
            GROUP BY skill_name
        """, (session['username'], start_of_week.date())).fetchall()

        # **ดึงคะแนนรวมของผู้ใช้จากตาราง user หรือคะแนน (แก้ชื่อและโครงสร้างตามฐานข้อมูลจริง)**
        points_row = db.execute("""
            SELECT points FROM users WHERE username = ?
        """, (session['username'],)).fetchone()

    data = [dict(row) for row in rows]

    points = points_row['points'] if points_row else 0  # กำหนด 0 ถ้าไม่มีข้อมูลคะแนน

    return render_template('statistic.html', data=data, start_date=start_of_week_str, points=points)



def reset_weekly_activities_if_needed(username):
    db = get_db()

    # ดึงเวลาที่บันทึกกิจกรรมแรกสุดของ user
    first_activity = db.execute("""
        SELECT MIN(timestamp) as first_time
        FROM activities
        WHERE username = ?
    """, (username,)).fetchone()

    if not first_activity or not first_activity['first_time']:
        # ไม่มีข้อมูลกิจกรรมเลย ไม่ต้องรีเซ็ต
        return

    first_date = datetime.strptime(first_activity['first_time'], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()

    # ถ้าผ่านมาเกิน 7 วัน
    if now - first_date >= timedelta(days=7):
        # ลบกิจกรรมของ user
        db.execute("DELETE FROM activities WHERE username = ?", (username,))
        db.commit()



@app.route('/get_todos', methods=['GET'])
def get_todos():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    with get_db() as db:
        rows = db.execute(
            "SELECT id, content, is_done FROM todos WHERE username = ?",
            (session['username'],)
        ).fetchall()

    todos = [dict(row) for row in rows]
    return jsonify(todos)


@app.route('/add_todo', methods=['POST'])
def add_todo():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO todos (username, content) VALUES (?, ?)",
            (session['username'], content)
        )
        db.commit()
        todo_id = cursor.lastrowid  # 👈 เอา ID กลับ

    return jsonify({'message': 'Todo added successfully', 'id': todo_id})

@app.route('/delete_todo/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    with get_db() as db:
        db.execute("DELETE FROM todos WHERE id = ? AND username = ?", (todo_id, session['username']))
        db.commit()

    return jsonify({'status': 'deleted'})


@app.route('/update_todo/<int:todo_id>', methods=['POST'])
def update_todo(todo_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    is_done = data.get('is_done', False)

    with get_db() as db:
        db.execute(
            "UPDATE todos SET is_done = ? WHERE id = ? AND username = ?",
            (1 if is_done else 0, todo_id, session['username'])
        )
        db.commit()

    return jsonify({'status': 'updated'})

@app.route('/challenge')
def challenge():
    if 'username' not in session:
        flash("กรุณาเข้าสู่ระบบก่อน", "warning")
        return redirect(url_for('login'))

    db = get_db()

    challenges = db.execute("SELECT * FROM challenges").fetchall()

    skill_data = db.execute("""
        SELECT skill_name, SUM(minutes) AS total_minutes
        FROM activities
        WHERE username = ?
        GROUP BY skill_name
    """, (session['username'],)).fetchall()

    skill_map = {row['skill_name']: row['total_minutes'] for row in skill_data}

    result = []
    for ch in challenges:
        done_minutes = skill_map.get(ch['skill'], 0)
        target_minutes = ch['target_minutes']

        percent = int((done_minutes / target_minutes) * 100) if target_minutes else 0
        completed = percent >= 100
        print(f"Challenge {ch['title']}: done={done_minutes}, target={target_minutes}, percent={percent}, completed={completed}")

        result.append({
            'id': ch['id'],
            'title': ch['title'],
            'description': ch['description'],
            'progress': min(100, percent),
            'completed': percent >= 100,
            'points': ch['points']
        })

    # ✅ ดึงคะแนนรวมของ user
    user = db.execute("SELECT points FROM users WHERE username = ?", (session['username'],)).fetchone()
    points = user['points'] if user and user['points'] is not None else 0

    return render_template(
    'challenge.html',
    challenges=result,
    is_admin=session.get('is_admin'),
    points=points
)

    



@app.route('/add_challenge', methods=['POST'])
def add_challenge():
    if not session.get('is_admin'):
        flash("คุณไม่มีสิทธิ์เพิ่มภารกิจ", "danger")
        return redirect(url_for('challenge'))

    title = request.form.get('title')
    description = request.form.get('description')
    skill = request.form.get('skill')
    target_minutes = request.form.get('target_minutes', type=int)
    points = request.form.get('points', type=int)

    if not all([title, description, skill, target_minutes, points]):
        flash("กรุณากรอกข้อมูลให้ครบทุกช่อง", "danger")
        return redirect(url_for('challenge'))

    db = get_db()
    db.execute(
        "INSERT INTO challenges (title, description, skill, target_minutes, points) VALUES (?, ?, ?, ?, ?)",
        (title, description, skill, target_minutes, points)
    )
    db.commit()

    # **หลังเพิ่มภารกิจใหม่แล้ว อัพเดตคะแนนให้ user ทุกคนที่เคยทำกิจกรรม skill นี้**
    users = db.execute("SELECT DISTINCT username FROM activities WHERE skill_name = ?", (skill,)).fetchall()
    for user_row in users:
        update_user_points(user_row['username'])

    flash("เพิ่มภารกิจเรียบร้อยแล้ว และอัพเดตคะแนนผู้ใช้ที่เกี่ยวข้อง", "success")
    return redirect(url_for('challenge'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('admin_password')
        if password == '12345':  # รหัสผ่านฟิกตรงนี้
            session['is_admin'] = True
            flash('เข้าสู่โหมดแอดมินแล้ว', 'success')
            return redirect(url_for('challenge'))
        else:
            flash('รหัสผ่านไม่ถูกต้อง', 'danger')
            return redirect(url_for('admin_login'))
        
    return render_template('admin_login.html')




@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    flash("ออกจากโหมดแอดมินแล้ว", "info")
    return redirect(url_for('challenge'))

@app.route('/delete_challenge/<int:challenge_id>', methods=['POST'])
def delete_challenge(challenge_id):
    if not session.get('is_admin'):
        flash("คุณไม่มีสิทธิ์ลบภารกิจ", "danger")
        return redirect(url_for('challenge'))

    db = get_db()
    db.execute("DELETE FROM challenges WHERE id = ?", (challenge_id,))
    db.commit()

    flash("ลบภารกิจเรียบร้อยแล้ว", "success")
    return redirect(url_for('challenge'))


from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

import random
from datetime import datetime, timedelta

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        with get_db() as db:
            user = db.execute("SELECT username FROM users WHERE email = ?", (email,)).fetchone()
            if user:
                otp = f"{random.randint(100000, 999999)}"
                expires_at = datetime.now() + timedelta(minutes=10)
                db.execute("""
                    INSERT INTO password_resets (email, otp, expires_at) VALUES (?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET otp=excluded.otp, expires_at=excluded.expires_at
                """, (email, otp, expires_at))
                db.commit()
                
                msg = Message(subject="รหัส OTP สำหรับรีเซ็ตรหัสผ่าน Timehack",
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[email],
                              body=f'รหัส OTP ของคุณคือ: {otp} \nใช้ได้ภายใน 10 นาที')
                mail.send(msg)
                session['reset_email'] = email  # เพิ่มบรรทัดนี้
                flash('ส่งรหัส OTP ไปยังอีเมลของคุณแล้ว', 'success')
            else:
                flash('ไม่พบอีเมลนี้ในระบบ', 'danger')
        return redirect(url_for('verify_otp'))
    return render_template('forgot_password.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        flash('กรุณากรอกอีเมลก่อน', 'warning')
        return redirect(url_for('forgot_password'))

    email = session['reset_email']

    if request.method == 'POST':
        otp_input = request.form['otp']
        with get_db() as db:
            row = db.execute("SELECT otp, expires_at FROM password_resets WHERE email = ?", (email,)).fetchone()

        if row and row['otp'] == otp_input and datetime.now() < datetime.strptime(row['expires_at'], "%Y-%m-%d %H:%M:%S.%f"):

            session['otp_verified'] = True
            flash('ยืนยันรหัส OTP สำเร็จ กรุณาตั้งรหัสผ่านใหม่', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('รหัส OTP ไม่ถูกต้องหรือหมดอายุ', 'danger')

    return render_template('verify_otp.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email or not session.get('otp_verified'):
        flash('กรุณายืนยัน OTP ก่อน', 'warning')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        hashed_pw = generate_password_hash(new_password)
        with get_db() as db:
            db.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
            db.commit()
            db.execute("DELETE FROM password_resets WHERE email = ?", (email,))
            db.commit()
        
        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        flash('รีเซ็ตรหัสผ่านเรียบร้อยแล้ว กรุณาเข้าสู่ระบบใหม่', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')


if __name__ == '__main__':
    app.run(debug=True)
