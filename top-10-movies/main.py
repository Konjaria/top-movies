from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///topmovies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)


class Editor(FlaskForm):
    rating = FloatField(label="Your rating out of 10 i.e. 7.5")
    review = StringField(label="Your review")
    ok = SubmitField(label="Save")


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    img_url = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Name %r> {self.title}'


with app.app_context():
#     db.create_all()
#     new_movie = Film(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()
    pass


@app.route("/")
def home():
    all_movies = db.session.query(Film).all()
    return render_template("index.html", bootstrap=bootstrap, movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    all_movies = db.session.query(Film).all()
    all_form = Editor()
    if request.method == "POST":
        if all_form.validate_on_submit():
            film_id = request.args.get('id')
            film_to_update = Film.query.get(film_id)
            film_to_update.rating = all_form.rating.data
            film_to_update.review = all_form.review.data
            db.session.commit() 
            return redirect(url_for('home'))
    return render_template("edit.html", bootstrap=bootstrap, movies=all_movies, form=all_form)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    film_id = request.args.get('id')
    film_to_delete = Film.query.get(film_id)
    db.session.delete(film_to_delete)
    db.session.commit()
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)
