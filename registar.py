#Imports
from flask import Flask, render_template, flash, redirect, url_for, request,  session, logging
from data import Events
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#DB Credentials
app.config['MYSQL_USER'] = 'sql2351305'
app.config['MYSQL_PASSWORD'] = 'yV6%uM2*'
app.config['MYSQL_DB'] = 'sql2351305'
app.config['MYSQL_HOST'] = 'sql2.freemysqlhosting.net'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql=MySQL(app)

Events = Events()

#Routes
@app.route('/')
def index():
 return render_template ('home.html')


@app.route('/login')
def login():
 return render_template ('login.html')

#Create and Insert into DB
@app.route('/about')
def about():
 #cur=mysql.connection.cursor()
 #cur.execute('''CREATE TABLE users (id INTEGER AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), email VARCHAR(30), username VARCHAR(30), password VARCHAR(30), reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
 #cur.execute('''CREATE TABLE users (id INTEGER AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), email VARCHAR(30), username VARCHAR(30), password VARCHAR(30), reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

 #Insert
 #cur.execute('''INSERT INTO users VALUES (2, 'Sri', 'sri@yopmail.com', 'Srimukhi', 'password', '' )''')
 #cur.execute('''INSERT INTO eventstable VALUES (2, 'Dinner & Dance', 'Good food, party and networking', 'Kessy', '2020-09-12', 'Athlone Tents')''')
 #mysql.connection.commit()

 #Output
 #cur.execute('''SELECT * FROM users''')
 #results=cur.fetchall()
 #print(results)
 #return results[1]['email']
 #return 'DONE'
 return render_template ('about.html')

#Events
@app.route('/articles')
def articles():
 #Create Cursor
 cur=mysql.connection.cursor()

 #Get Articles
 result=cur.execute("SELECT * FROM eventstable")

 articles=cur.fetchall()

 if result>0:
     return render_template('articles.html', articles=articles)
 else:
     msg='No Events Found'
 return render_template('articles.html', msg=msg)
 #Close connection
 cur.close()



#Each Events
@app.route('/article/<string:id>/')
def article(id):
    #Create Cursor
    cur=mysql.connection.cursor()

    #Get Articles
    result=cur.execute("SELECT * FROM eventstable WHERE id = %s ", [id])

    article=cur.fetchone()

    return render_template ('article.html', article=article)
#Register Form and Validations
class RegisterForm(Form):
    name=StringField('Name',[validators.Length(min=2, max=50)])
    username=StringField('username',[validators.Length(min=4, max=25)])
    email=StringField('Email',[validators.Length(min=6, max=50)])
    password=PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm=PasswordField('Confirm Password')
#User Registration
@app.route('/register', methods=['GET','POST'])
def register():
    form=RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        #password=sha256_crypt.encrypt(str(form.password.data))
        password=form.password.data
        #Create Cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password) )

        #Commit to DB
        mysql.connection.commit()
        #cur.close()

        #Output

        flash('You have been registered', 'success')

        return redirect(url_for('loginx'))
    return render_template('register.html', form=form)

#User login
@app.route('/loginx', methods=['GET','POST'])
def loginx():
    if request.method=='POST':
        #Get form fields
        username=request.form['username']
        password_candidate=request.form['password']

        #Create cursor
        cur=mysql.connection.cursor()

        #Get user by username
        result=cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result>0:
            #Get Stored hash
            data=cur.fetchone()
            password=data['password']


            #Compare password
            #if sha256_crypt.verify(password_candidate, password):
            if password_candidate == data['password']:
                app.logger.info('PASSWORD MATCHED')
                session['logged_in']=True
                session['username']=username
                #return render_template ('about.html')
                flash('Login Successful', 'success')
                return redirect(url_for('dashboard'))


            else:
                error='Invalid Login'
                return render_template ('loginx.html', error=error)
            cur.close()
        else:
            error='Username not found'
            return render_template ('loginx.html', error=error)

    return render_template('loginx.html')

#Check If User is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized, You need to login first', 'danger')
            return redirect(url_for('loginx'))
    return wrap



#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have logged out', 'success')
    return redirect(url_for('loginx'))

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #Create Cursor
    cur=mysql.connection.cursor()

    #Get Articles
    result=cur.execute("SELECT * FROM eventstable")

    articles=cur.fetchall()

    if result>0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg='No Events Found'
    return render_template('dashboard.html', msg=msg)
    #Close connection
    cur.close()


#Add Event Form
class ArticleForm(Form):
    title=StringField('Title',[validators.Length(min=2, max=100)])
    description=TextAreaField('Description',[validators.Length(min=10)])
    location=StringField('Location',[validators.Length(min=2, max=100)])


#Add Event Route
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form=ArticleForm(request.form)
    if request.method=='POST' and form.validate():
        title=form.title.data
        description=form.description.data
        location=form.location.data

        #Create Cursor
        cur=mysql.connection.cursor()

        #execute
        #cur.execute("INSERT INTO eventstable(title, description, host) VALUES(%s, %s, %s)", (title, description, session['username']) )
        cur.execute("INSERT INTO eventstable(id, title, description, location, host) VALUES(%s, %s, %s, %s, %s)", (id, title, description,location, session['username']) )
        #cur.execute('''INSERT INTO eventstable VALUES (4, 'Bikes & Booze', 'Bikers, food and networking', 'Kizzzolo', '2020-07-12', 'Dublin Arcade')''')


        #Commit
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Event has been created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)


#Edit Event
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):

    cur=mysql.connection.cursor()

    #Get Article by id
    result=cur.execute("SELECT * FROM eventstable WHERE id = %s", [id])

    article=cur.fetchone()

    #Get form
    form=ArticleForm(request.form)

    #Populate Article Form fields
    form.title.data=article['title']
    form.location.data=article['location']
    form.description.data=article['description']


    if request.method=='POST' and form.validate():
        title=request.form['title']
        description=request.form['location']
        location=request.form['description']

        #Create Cursor
        cur=mysql.connection.cursor()

        #execute
        #cur.execute("UPDATE eventstable SET title=%s, location=%s, description=%s WHERE id=%s", (title, location, description) )


        #Commit
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Event has been Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


#Delete Article
@app.route('/delete_article/<string:id>', methods=['post'])
@is_logged_in
def delete_article(id):
    #create cursor
    cur=mysql.connection.cursor()

    #execute
    cur.execute("DELETE FROM eventstable WHERE id = %s", [id])
    #Commit
    mysql.connection.commit()

    #close connection
    cur.close()

    flash('Event has been Deleted', 'success')

    return redirect(url_for('dashboard'))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

#Attendees dashboard
@app.route('/attendees')
@is_logged_in
def attendees():
    #Create Cursor
    cur=mysql.connection.cursor()

    #Get Articles
    result=cur.execute("SELECT * FROM attendees")

    attendees=cur.fetchall()

    if result>0:
        return render_template('attendees.html', attendees=attendees)
    else:
        msg='No Events Found'
    return render_template('attendees.html', msg=msg)
    #Close connection
    cur.close()


#Add Attendees Form
class AttendeesForm(Form):
    name=StringField('Name',[validators.Length(min=2, max=30)])
    email=StringField('Email',[validators.Length(min=10, max=30)])
    about=TextAreaField('Tell Us About You',[validators.Length(min=2)])


#Add Attendees Route
@app.route('/attend', methods=['GET', 'POST'])
#@is_logged_in
def attend():
    form=AttendeesForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        about=form.about.data

        #Create Cursor
        cur=mysql.connection.cursor()

        #execute
        #cur.execute("INSERT INTO eventstable(title, description, host) VALUES(%s, %s, %s)", (title, description, session['username']) )
        cur.execute("INSERT INTO attendees(name, email, about) VALUES(%s, %s, %s)", (name, email, about) )
        #cur.execute('''INSERT INTO eventstable VALUES (4, 'Bikes & Booze', 'Bikers, food and networking', 'Kizzzolo', '2020-07-12', 'Dublin Arcade')''')


        #Commit
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Registration Successful. See you at the event!', 'success')

        return redirect(url_for('articles'))

    return render_template('attend.html', form=form)


if __name__ == '__main__':
    app.secret_key='password'
    app.run(debug=True)
