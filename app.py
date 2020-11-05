from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:123@localhost/pydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = '1234567890'
db = SQLAlchemy(app)


tags = db.Table('tags',
    db.Column('stoty_id', db.ForeignKey('story.id')),
    db.Column('tag_id', db.ForeignKey('tag.id')))

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column (db.String (50), nullable = False)
    creationData=db.Column(db.DateTime,default=datetime.now())
    tags = db.relationship('Tag',
                            secondary=tags,
                            lazy='dynamic',
                            backref=db.backref('story', lazy='dynamic'))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column (db.String (50), nullable = False)
    creationData=db.Column(db.DateTime,default=datetime.now())


class StoryForm(FlaskForm):
    name=StringField('write something', validators=[DataRequired()])
    tag=StringField('tag')
    Btm = SubmitField('Add')


@app.route('/', methods=['GET', 'POST'])
def index():

    story = Story.query.order_by(Story.creationData.desc())
    page=request.args.get('page')

    s=request.args.get('story')
    t=request.args.get('name')

    if t and s:
        stor=Story.query.filter_by(id=int(s)).first()
        tag=Tag(name=t)
        db.session.add(tag)
        db.session.commit()
        stor.tags.append(tag)
        db.session.commit()

    if page and page.isdigit():
        page=int(page)
    else:
        page=1

    pages=story.paginate(page=page,per_page=15)
    return render_template('index.html',story=story,pages =pages)



@app.route('/add', methods=['GET', 'POST'])
def add():
    form = StoryForm()
    name=request.form.get('name')
    tag1=request.form.get('tag')

    if form.validate_on_submit():
        story=Story(name=name)
        tag=Tag(name=tag1)
        db.session.add(story)
        db.session.add(tag)
        story.tags.append(tag)
        db.session.commit()
        return redirect('/')
    return render_template('add.html', form=form)


if __name__=='__main__':
    app.run(debug=True)