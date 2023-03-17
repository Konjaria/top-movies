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
my_api_key = "466fc630876802bd35999439a87b1d24"


class Selector:
    def __init__(self, whole_data):
        self.movie_id = whole_data["id"]
        self.title = whole_data["original_title"]
        self.review = whole_data["overview"]
        self.img_url = "https://image.tmdb.org/t/p/original/{}".format(whole_data["poster_path"])
        self.rate = whole_data["vote_average"]
        self.release_date = whole_data["release_date"]


class Add(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Save")


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


# with app.app_context():
    # db.create_all()



@app.route("/")
def home():
    all_movies = db.session.query(Film).order_by(Film.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", bootstrap=bootstrap, movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    all_movies = db.session.query(Film).all()
    all_form = Editor()
    if request.method == "POST":
        if all_form.validate_on_submit():
            film_id = request.args.get('movie_id')
            record = db.session.query(Film).filter_by(id=film_id).first()
            found = False
            if record is None:
                response = requests.get(url="https://api.themoviedb.org/3/search/movie",
                                        params={"api_key": my_api_key, "query": request.args.get('movie_title')})
                response.raise_for_status()
                big_data = response.json()["results"]
                for i, data in enumerate(big_data):
                    print(f"#{i}: ", film_id, ",  ", data["id"], "\n")
                    if str(film_id).strip() == str(data["id"]).strip():
                        found = True
                        whole_data = data
                        new_movie = Film(
                            title=whole_data.get("title"),
                            year=whole_data.get("release_date"),
                            description=whole_data.get("overview"),
                            rating=all_form.rating.data,
                            ranking=whole_data.get("vote_average"),
                            review=all_form.review.data,
                            img_url="https://image.tmdb.org/t/p/original/{}".format(whole_data.get("poster_path"))
                        )
                        db.session.add(new_movie)
                        db.session.commit()
                        print("Successfully Added to Database ✅")
                        return redirect(url_for('home'))
            if not record or not found or record is not None:
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


@app.route("/add", methods=["GET", "POST"])
def add():
    all_movies = db.session.query(Film).all()
    all_form = Add()

    if request.method == "POST":
        return redirect(url_for('select', movie_title=all_form.title.data))
    return render_template('add.html', bootstrap=bootstrap, movies=all_movies, form=all_form)


@app.route("/select", methods=["GET", "POST"])
def select():
    response = requests.get(url="https://api.themoviedb.org/3/search/movie",
                            params={"api_key": my_api_key, "query": request.args.get('movie_title')})
    response.raise_for_status()
    return render_template('select.html', bootstrap=bootstrap,
                           search_results=response.json()["results"])


if __name__ == '__main__':
    app.run(debug=True)
