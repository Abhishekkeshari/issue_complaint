from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import re
import os
import smtplib

app = Flask(__name__)
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mysql = SQLAlchemy(app)
app.secret_key = 'apple'

class Tickets(mysql.Model):
    id = mysql.Column(mysql.Integer(), unique=True, primary_key=True)
    customer = mysql.Column(mysql.String(30), unique=False, nullable=False)
    customer_name = mysql.Column(mysql.String(40),  nullable=False)
    agent = mysql.Column(mysql.String(30),  nullable=True)
    agent_name = mysql.Column(mysql.String(30),  nullable=True)
    title = mysql.Column(mysql.String(30),  nullable=False)
    description = mysql.Column(mysql.String(100), nullable=False)
    progress = mysql.Column(mysql.String(30), nullable=True)



class Users(mysql.Model):
    id = mysql.Column(mysql.Integer(), unique=True, primary_key=True)
    username = mysql.Column(mysql.String(30), unique=False, nullable=False)
    email = mysql.Column(mysql.String(40),  nullable=False)
    password = mysql.Column(mysql.String(30),  nullable=False)
    role = mysql.Column(mysql.Integer(),  nullable=False)






# routes

# home
@app.route('/')
def index():
    return render_template("index.html")


# dashboard

@app.route("/home", methods=["GET", "POST"])
def home():
    if ('users' not in session.keys()) or (session['users'] is None):
        return redirect(url_for("login"))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE id = % s", [session['users']])
        userdetails = cursor.fetchone()
        if userdetails[4] == 2:
            return render_template("home.html", users=userdetails)
        if userdetails[4] == 5:
            return render_template("home.html", users=userdetails)
        elif userdetails[4] == 1:
            cursor.execute("SELECT * FROM Tickets WHERE agent=%s", [session['users']])
            tickets = cursor.fetchall()
            return render_template("home.html", users=userdetails, tickets=tickets)
        else:
            if request.method == "POST":
                title = request.form['title']
                description = request.form['description']
                cust_id = session['users']
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT username FROM Users WHERE id = % s", [session['users']])
                username = cursor.fetchone()
                cursor.execute("INSERT INTO Tickets(customer,customer_name,title,description) VALUES(%s,%s,%s,%s)",
                               (cust_id, username, title, description))
                mysql.connection.commit()
                cursor.execute("SELECT * FROM Users WHERE id = % s", [session['users']])
                userdetails = cursor.fetchone()
                cursor.execute("SELECT * FROM Tickets WHERE customer = %s", [session['users']])
                tickets = cursor.fetchall()
                return render_template("home.html", msg="Ticket Filed", users=userdetails, tickets=tickets)
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE id = % s", [session['users']])
            userdetails = cursor.fetchone()
            cursor.execute("SELECT * FROM Tickets WHERE customer = %s", [session['users']])
            tickets = cursor.fetchall()
            return render_template("home.html", users=userdetails, tickets=tickets)


# user account registration

@app.route("/register", methods=["GET", "POST"])
def register_account():
    msg = ''
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        stu = Users(username =username , email = email, password =password,role =1)
        # cursor = mysql.connection.cursor()
        mysql.session.add(stu)
        mysql.session.commit()
        return redirect(url_for("login"))

    return render_template('register.html')
        # cursor.execute('SELECT * FROM Users WHERE email = % s', (email,))
        # userdetails = cursor.fetchone()
        #  print(userdetails)
        # if userdetails:
        #     msg = 'Account already exists !'
        # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        #     msg = 'Invalid email address !'
        # elif not re.match(r'[A-Za-z0-9]+', username):
        #     msg = 'name must contain only characters and numbers !'
        # else:
            # cursor.execute("INSERT INTO Users(username,email,password,role) VALUES(% s,% s,% s,% s)",
            #                (username, email, password, 0))
            # mysql.connection.commit()
            # msg = 'You have successfully registered !'
            # mysql.connection.commit()
            # return redirect(url_for("login"))
    # elif request.method == 'POST':
    #     msg = 'Please fill out the form !'
    # return render_template('register.html')


# agent account registration

@app.route("/agent", methods=["GET", "POST"])
def agent_register():
    msg = ''
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = % s', (email,))
        userdetails = cursor.fetchone()
        print(userdetails)
        if userdetails:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute("INSERT INTO Users(username,email,password,role) VALUES(% s,% s,% s,% s)",
                           (username, email, password, 5))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            mysql.connection.commit()
            return redirect("/")
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('agent.html', msg=msg)


# login

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        alldata=Users.query.all()
        # cursor = mysql.connection.cursor()
        # cursor.execute('SELECT * FROM Users WHERE email = % s AND password = % s', (email, password))
        # userdetails = cursor.fetchone()
        # print(userdetails)
        # if userdetails:
            session['loggedin'] = True
            session['users'] = userdetails[0]
            session['username'] = userdetails[1]
            msg = 'Logged in successfully !'
            return redirect(url_for("home"))
        else:
            msg = 'Incorrect username / password !'
            return render_template("login.html", msg=msg)
    return render_template('login.html', msg=msg)


# ticket detail

@app.route("/ticket/<int:id>", methods=["GET", "POST"])
def ticket_detail(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Tickets WHERE id = % s", [id])
    ticket = cursor.fetchone()
    cursor.execute("SELECT * FROM Users WHERE id = % s", [session['users']])
    users = cursor.fetchone()
    cursor.execute("SELECT * FROM Users WHERE role = 1")
    all_users = cursor.fetchall()
    if users is None:
        return redirect(url_for("login"))
    if request.method == "POST":
        agent = request.form['agent']
        print(agent, id)
        cursor.execute("SELECT username FROM Users WHERE id= % s", (agent,))
        agent_name = cursor.fetchone()
        agt = str(agent_name)
        cursor.execute("SELECT customer_name FROM Tickets WHERE id= % s", [id])
        customer_name = cursor.fetchone()
        cust = str(customer_name)
        cursor.execute("UPDATE Tickets SET agent= %s,agent_name= % s WHERE id = %s", (agent, agent_name, id))
        cursor.execute("UPDATE Tickets SET progress='assigned' WHERE id = %s", [id])
        mysql.connection.commit()
        cursor.execute("SELECT email FROM Users WHERE id=(SELECT customer FROM Tickets WHERE id= % s)", [id])
        email = cursor.fetchall()
        text = "Hello "+cust+",\n\n"+"Agent "+agt+" is successfully assigned to you.The Agent will contact you soon. To keep a track of your ticket, please visit our website dashboard."
        subject = "Agent Assigned"
        message = 'subject: {}\n\n{}'.format(subject, text)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("customercareabhishek3098@gmail.com", "etqdxetafazenqyu")
        server.sendmail("customercareabhishek3098@gmail.com", email, message)
        return redirect(url_for("panel"))
    return render_template("details.html", ticket=ticket, users=users, all_users=all_users)


# admin register

@app.route("/admin", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        secret_key = request.form['secret']
        if secret_key == "12345":
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO Users(username,email,password,role) VALUES(% s,% s,% s,% s)",
                           (username, email, password, 2))
            mysql.connection.commit()
            return redirect(url_for("login"))
        else:
            return render_template("admin_register.html", msg="Inlaid Secret")
    return render_template("admin_register.html")


# promote agent

@app.route("/panel", methods=["GET", "POST"])
def panel():
    id = session['users']
    if id is None:
        return redirect(url_for("login"))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE id= % s", [id])
    user_details = cursor.fetchone()
    if user_details[4] != 2:
        return "You do not have administrator privileges"
    else:
        cursor.execute("SELECT * FROM Users WHERE role=5")
        all_users = cursor.fetchall()
        cursor.execute("SELECT * FROM Tickets WHERE progress IS NULL")
        tickets = cursor.fetchall()
        if request.method == "POST":
            user_id = request.form['admin-candidate']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE Users SET role=1 WHERE id = % s", (user_id,))
            mysql.connection.commit()
            return redirect(url_for("panel"))
        return render_template("panel.html", all_users=all_users, users=user_details, tickets=tickets)


# accept ticket

@app.route("/accept/<int:ticket_id>/<int:user_id>")
def accept(ticket_id, user_id):
    # print("ticket_id ==",ticket_id)
    # print("user_id ==", user_id)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE id = % s", [user_id])
    agent = cursor.fetchone()
    print("agent ==", agent)
    cursor.execute("SELECT * FROM Tickets WHERE id = % s", [ticket_id])
    ticket = cursor.fetchone()
    # print("ticket ==", ticket)
    # print(agent[0])
    # print(ticket[3])
    if agent[0] == int(ticket[3]):
        # print("Abhishek")
        cursor.execute("UPDATE Tickets SET progress='accepted' WHERE id = % s", [ticket_id])
        mysql.connection.commit()
    return redirect(url_for("home"))


# delete ticket

@app.route("/delete/<int:ticket_id>/<int:user_id>")
def delete(ticket_id, user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE id = % s", [user_id])
    agent = cursor.fetchone()
    cursor.execute("SELECT * FROM Tickets WHERE id=% s", [ticket_id])
    ticket = cursor.fetchone()
    if agent[0] == int(ticket[3]):
        cursor.execute("DELETE FROM Tickets WHERE id=%s", [ticket_id])
        mysql.connection.commit()
    return redirect(url_for("home"))


# logout

@app.route("/logout")
def logout():
    session['users'] = None
    return redirect(url_for("home"))


# run server
if __name__ == "__main__":
    app.run(debug=True)


