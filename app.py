
from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'loginpage'

mysql = MySQL(app)
mysql.init_app(app)

s_time = "Apr 7, 2015 1:30:25"
end_time = "Apr 7, 2020 1:30:25"

def count(): 
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM questions;")
    data = cur.fetchone()
    cur.close()
    return data

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connect().cursor()
        cur.execute("SELECT * FROM users WHERE email=%s",(email))
        user = cur.fetchone()
        cur.close()

        if user > 0:
            if password == user[3] :
                session['name'] = user[0]
                session['lname'] = user[1]
                session['email'] = user[2]
                session['username'] = user[6]
                session['user_marks'] = 0
                session['i'] = 1


                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")

@app.route('/ps_login',methods=["GET","POST"])
def ps_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "ps@admin.com" and password == "password" :
            session['ps'] = 1;
            return redirect(url_for('ps_portal'))
        else:
            return "Error password or email not match"

    else:
        return render_template("ps_login.html")

@app.route('/ps_logout')
def ps_logout():
    session['ps'] = 0
    return redirect(url_for('home'))

@app.route('/ps_portal', methods=["GET","POST"])
def ps_portal():
    total_Q = count()
    session['q'] = total_Q[0] + 1
    if request.method == 'POST':
        q_no = request.form['q_no']
        question = request.form['question']
        a = request.form['A']
        b = request.form['B']
        c = request.form['C']
        d = request.form['D']
        correct_option = request.form['Correct_answer']
        marks = request.form['marks']

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO questions values (%s,%s,%s,%s,%s,%s,%s,%s);",(q_no,question,a,b,c,d,correct_option,marks))
        conn.commit()
        cur.close()
        return render_template("ps_portal.html",total=total_Q[0]+2)
    else:
        
        return render_template("ps_portal.html",total=total_Q[0]+1)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        fname = request.form['first_name']
        lname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        dob = request.form['birthday']
        username = request.form['username']
        phone = request.form['phone']


        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(fname,lname,email,password,gender,dob,username,phone))
        cur.execute("INSERT INTO leaderboard(username) VALUES (%s)",(username))
        #cur.execute("CREATE TABLE %s (q_no int,marked_response char,primary key(q_no));",(username))
        conn.commit()
        cur.close()
        session['fname'] = request.form['first_name']
        session['email'] = request.form['email']
        return redirect(url_for('login'))

@app.route('/Developer')
def developer():
    return render_template("Developer.html")

@app.route('/instructions')
def instruction():   
    total_Q = count()

    for k in range(1,total_Q[0]+1):
        l = str(k)
        session[l] = 0                  #set all the flags corresponding to questions in db = 0 => marks not awarded

    return render_template("instructions.html",sTime = s_time,eTime = end_time,total_Q=total_Q[0])

@app.route('/questions', methods=["GET", "POST"])
def questions():
    global s_time
    global end_time
    total_Q = count()

    if request.method == 'POST':
        opt = request.form['option']
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("select correct_answer,marks from questions WHERE q_no=%s;",(session['i']))
        x = cur.fetchone()
        conn.commit()
        cur.close()

        k = str(session['i'])               #session dictionary's key INT is allowed but cannot be accessed by other links/functions 

        if opt == x[0] and session[k] == 0 :              #answer is correct and marks is not awarded
            session['user_marks'] = session['user_marks'] + x[1]
            session[k] = 1                               #marks awarded

        if opt != x[0] and session[k] == 1 :
            session['user_marks'] = session['user_marks'] - x[1]
            session[k] = 0
        
        return render_template("question.html",sTime = s_time,eTime = end_time,total_Q=total_Q[0])
    else:
    
        
        cur = mysql.connect().cursor()
        cur.execute("SELECT q_no,question,a,b,c,d,marks FROM questions WHERE q_no=%s",(session['i']))
        data = cur.fetchone()
        cur.close()


        if data > 0:
                session['q_no'] = data[0]
                session['Q'] = data[1]
                session['A'] = data[2]
                session['B'] = data[3]
                session['C'] = data[4]
                session['D'] = data[5]
                session['q_mark'] = data[6]
        return render_template("question.html",sTime = s_time,eTime = end_time,total_Q=total_Q[0])

@app.route('/next')
def Next():
    total_Q = count()
    
    if session['i'] == total_Q[0]:
        return  redirect(url_for('questions'))
    else:    
        session['i'] = session['i'] + 1
    return redirect(url_for('questions'))

@app.route('/prev')
def prev():
    global i
    if session['i'] == 1:
        return redirect(url_for('questions'))
    else :
        session['i'] = session['i'] - 1
    return redirect(url_for('questions'))

@app.route('/final_submit')
def final_submit():
    global user_marks
    session['i'] = 1
    conn = mysql.connect()
    cur = conn.cursor() 
    cur.execute("select marks from questions;")
    x = cur.fetchall()
    conn.commit()
    cur.close()

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("update leaderboard set marks=%s where username=%s;",(session['user_marks'],session['username']))
    conn.commit()
    cur.close()

    y = list(sum(x, ()))
    total_marks = sum(y)
    session['total_marks'] = total_marks
    user_marks = 0
    return render_template("result.html")

@app.route('/results')
def results():
    return render_template("result.html")

@app.route('/ps_view',methods=["GET","POST"])
def ps_view():
    if request.method == 'GET' :
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("select q_no,question,a,b,c,d,correct_answer,marks from questions;")
        Qdata = cur.fetchall()
        conn.commit()
        cur.close()
        return render_template('ps_view.html',Qdata=Qdata)
    else :
        return render_template('ps_view.html')

@app.route('/edit_q',methods=["POST"])
def edit_q():
    q_no = request.form['edit']

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select question,a,b,c,d,correct_answer,marks from questions where q_no=%s;",(q_no))
    Qdata = cur.fetchone()
    conn.commit()
    cur.close()

    return render_template("edit.html",total=q_no,Qdata=Qdata)

@app.route('/edit',methods=["POST"])
def edit():
    q_no = request.form['q_no']
    question = request.form['question']
    a = request.form['A']
    b = request.form['B']
    c = request.form['C']
    d = request.form['D']
    correct_option = request.form['Correct_answer']
    marks = request.form['marks']

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("UPDATE questions SET question = %s,a=%s,b=%s,c=%s,d=%s,correct_answer=%s,marks=%s where q_no=%s;",(question,a,b,c,d,correct_option,marks,q_no))
    conn.commit()
    cur.close()
    return redirect(url_for('ps_view'))

@app.route('/delete_q',methods=["POST"])
def delete():
    q_no = request.form['delete']

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("Update questions set question=NULL,a=NULL,b=NULL,c=NULL,d=NULL,correct_answer=NULL,marks=0 where q_no=%s;",(q_no))
    conn.commit()
    cur.close()
    return redirect(url_for('ps_view'))

@app.route('/myprofile')
def myprofile():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select gender,dob,username,phone from users where email=%s;",(session['email']))
    Pdata = cur.fetchone()
    conn.commit()
    cur.close()
    return render_template('myprofile.html',Pdata=Pdata)

@app.route('/leaderboard')
def leaderboard():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select username,marks,fname,lname from leaderboard natural join users where username = username order by marks desc;")
    Ldata = cur.fetchall()
    conn.commit()
    cur.close()
    print(Ldata)
    size = len(Ldata)

    List1 = []
    for i,_ in enumerate(Ldata):
        List1.append(Ldata[i] + (i+1,)) 

    return render_template('leaderboard.html',data=List1)
 
@app.route('/reset_lb',methods=["POST"])
def clear_lb():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("update leaderboard set marks=0;")
    conn.commit()
    cur.close()
    return "success"

@app.route('/test_timings',methods=["POST","GET"])
def test_timings():
    global s_time
    global end_time

    if request.method == 'POST':
        s_time = request.form['s_time']
        end_time = request.form['end_time']

        return render_template("set_time.html",sTime = s_time,eTime = end_time)
    else :
        return render_template("set_time.html",sTime = s_time,eTime = end_time)

@app.route('/prohibited')
def prohibited():
    global s_time
    return render_template("prohibited.html",sTime = s_time)

if __name__ == '__main__':
    app.secret_key = "^A%DJAJU^JJ123"
    app.run(host="127.0.0.1", port=5000 , debug=True)
