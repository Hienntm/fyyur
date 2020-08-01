#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import pytz

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_time = db.Column(db.String(120))
    venue = db.relationship('Venue', backref=db.backref('artist', lazy=True))
    artist = db.relationship('Artist', backref=db.backref('venue', lazy=True))

    def __init__(self, artist_id, venue_id, start_time):
      self.artist_id = artist_id
      self.venue_id = venue_id
      self.start_time = start_time

    def insert(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.Text))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(300))

    def __init__(self, name, city, state, address, image_link, phone, genres, facebook_link):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.image_link = image_link
      self.phone = phone
      self.genres = genres
      self.facebook_link = facebook_link

    def insert(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.Text))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(300))

    def __init__(self, name, city, state, address, phone, image_link, genres, facebook_link):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.image_link = image_link
      self.genres = genres
      self.facebook_link = facebook_link

    def insert(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  result = []
  def groupByCity(venues):
    cities = set(map(lambda venue : venue.city, venues))
    for city in cities:
      item = {
        "city": "",
        "state": "",
        "venues": []
      }
      for venue in venues:
        if (venue.city == city):
          item["city"] = venue.city
          item["state"] = venue.state
          item["venues"].append({
            "id": venue.id,
            "name": venue.name,
            # "num_upcoming_shows": len(venue.upcoming_shows)
          })
      result.append(item)
    return result  
    
  data = groupByCity(venues)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {
    "count": 0,
    "data": []
  }

  venues = Venue.query.all()
  count = 0
  search_term = request.form.get('search_term', '').lower()
  for venue in venues:
    if (venue.name.lower().find(search_term) != -1):
      response["data"].append(venue)
      count += 1
  
  response["count"] = count

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  shows = Show.query.all()
  venues = Venue.query.all()
  venue = list(filter(lambda d: d.id == venue_id, venues))[0]
  venue_shows = list(filter(lambda s: s.venue.id == venue_id, shows))
  present_time = pytz.utc.localize(datetime.utcnow()).isoformat()
  venue.upcoming_shows = list(filter(lambda s: dateutil.parser.parse(s.start_time) > dateutil.parser.parse(present_time), venue_shows))
  venue.past_shows = list(filter(lambda s: dateutil.parser.parse(s.start_time) < dateutil.parser.parse(present_time), venue_shows))
  venue.upcoming_shows_count = len(venue.upcoming_shows)
  venue.past_shows_count = len(venue.past_shows)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')

  try:
    venue = Venue(name, city, state, address, image_link, phone, genres, facebook_link)
    venue.insert()
    # jsonify({
    #   'success': True
    # })
    flash('Venue ' + request.form['name'] + ' was successfully listed!') # on successful db insert, flash success
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venues = Venue.query.all()
    venue = list(filter(lambda d: d.id == venue_id, venues))[0]
    venue.delete()
    # jsonify({
    #   'success': True
    # })
    flash('Venue ' + request.form['name'] + ' was successfully deleted!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be deleted.')
  finally:
    return render_template('pages/home.html')  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {
    "count": 0,
    "data": []
  }

  artists = Artist.query.all()
  count = 0
  search_term = request.form.get('search_term', '').lower()
  for artist in artists:
    if (artist.name.lower().find(search_term) != -1):
      response["data"].append(artist)
      count += 1
  
  response["count"] = count

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  shows = Show.query.all()
  artists = Artist.query.all()
  artist = list(filter(lambda a: a.id == artist_id, artists))[0]
  artist_shows = list(filter(lambda s: s.artist.id == artist_id, shows))
  present_time = pytz.utc.localize(datetime.utcnow()).isoformat()
  artist.upcoming_shows = list(filter(lambda s: dateutil.parser.parse(s.start_time) > dateutil.parser.parse(present_time), artist_shows))
  artist.past_shows = list(filter(lambda s: dateutil.parser.parse(s.start_time) < dateutil.parser.parse(present_time), artist_shows))
  artist.upcoming_shows_count = len(artist.upcoming_shows)
  artist.past_shows_count = len(artist.past_shows)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists = Artist.query.all()
  artist = list(filter(lambda d: d.id == artist_id, artists))[0]
  
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.address.data = artist.address
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artists = Artist.query.all()
  artist = list(filter(lambda d: d.id == artist_id, artists))[0]

  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.address = request.form.get('address')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form.get('image_link')
  artist.facebook_link = request.form.get('facebook_link')

  artist.update()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues = Venue.query.all()
  venue = list(filter(lambda d: d.id == venue_id, venues))[0]
  
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venues = Venue.query.all()
  venue = list(filter(lambda d: d.id == venue_id, venues))[0]

  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.genres = request.form.getlist('genres')
  venue.image_link = request.form.get('image_link')
  venue.facebook_link = request.form.get('facebook_link')

  venue.update()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')

  try:
    artist = Artist(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link)
    artist.insert()
    flash('Artist ' + request.form['name'] + ' was successfully listed!') # on successful db insert, flash success
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  try:
    show = Show(artist_id=int(artist_id), venue_id=int(venue_id), start_time=start_time)
    show.insert()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
