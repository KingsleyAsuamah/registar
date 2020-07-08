from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import TextField

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///myDB.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False
db=SQLAlchemy(app)

app.secret_key="root"

class formta(FlaskForm):
    fname=TextField("fname")
    sname=TextField("sname")

class formtable(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String)
    sname=db.Column(db.String)

@app.route('/form',methods=['GET','POST'])
def table():
    form =formta()
    if form.validate_on_submit():
        tabble= formtable(fname=form.fname.data, sname=form.sname.data)
        db.session.add(tabble)
        db.session.commit()
    return render_template('table.html', form=form)

@app.route('/display', methods=['POST','GET'])
def display():
    d=formtable.query.all()
    return render_template ('display.html', displa=d)


db.create_all()
if __name__ == '__main__':
 	app.run(debug=True)
