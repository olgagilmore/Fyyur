#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import backref
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    image_link = db.Column(db.String(700))
    facebook_link = db.Column(db.String(700))
    website=db.Column(db.String(700))
    genres= db.Column(db.ARRAY(db.String))   #(db.String(700))
    seeking_talent=db.Column(db.Boolean, default=True)
    seeking_description=db.Column(db.String(700))
    
    shows =db.relationship('Show', backref='venue', lazy='dynamic')
    
    def get_venue(self):
        
        count= db.session.query(Show).filter(Show.venue_id==self.id).filter(Show.start_time> datetime.now()).count()
        
        return ({'id': self.id,
                'name': self.name,
                'num_upcoming_shows': count
                 })
    def details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String)) #(db.String(700))
    image_link = db.Column(db.String(700))
    facebook_link = db.Column(db.String(700))
    website=db.Column(db.String(700))
    seeking_venue=db.Column(db.Boolean, default=True)
    seeking_description=db.Column(db.String(700))
    
    shows=db.relationship('Show', backref='artist', lazy='dynamic')
    
  

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__='Show'
    
    id= db.Column(db.Integer, primary_key=True)
    start_time= db.Column(db.DateTime)
    venue_id=db.Column(db.Integer, db.ForeignKey(Venue.id, ondelete='CASCADE'), nullable=False)
    artist_id=db.Column(db.Integer, db.ForeignKey(Artist.id, ondelete='CASCADE'), nullable=False)
    
    def get_details(self):
        data={}
        myVenue= Venue.query.get(self.venue_id)
        
        data["venue_name"]= myVenue.name
        data["venue_image_link"]= myVenue.image_link
        
        data["id"]=self.id
        data["start_time"]= self.start_time
        data["venue_id"]= self.venue_id
        data["artist_id"]= self.artist_id
        
        myArtist=Artist.query.get(self.artist_id)
        data["artist_name"]= myArtist.name
        data["artist_image_link"]= myArtist.image_link    
        return data
    
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# def convert_babel_datetime(input):
#     #returns datetime from string object formatted by babel medium above
#     return datetime.datetime.strptime(input, '%a %m, %d, %Y %I:%M%p')

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
#   venues = Venue.query.all() 
#   group={}
#   for venue in venues:    
#       print(venue.id)      
#       group['venues'].append({  
#           'id': venue.id,       
#           'name': venue.name,   
#           'num_upcoming_show': Venue.query.filter_by(id=venue.id).join(Shows).count()       
#           })  
#         
#   result.append(group)
  
  areas = Venue.query.distinct('city','state').all()
  data = []
  for area in areas:
      venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
      record = {
        'city': area.city,
        'state': area.state,
        'venues': [venue.get_venue() for venue in venues],
      }
      data.append(record)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term='%' + request.form.get('search_term', '') + '%'
  response= {
      "count" :Venue.query.filter(Venue.name.ilike(search_term)).count(),
      "data":Venue.query.filter(Venue.name.ilike(search_term)).all()
      }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  record= Venue.query.get(venue_id)
  
  data= record.__dict__
  past_shows= Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time< datetime.now()).all()
  upcoming_shows= Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time>= datetime.now()).all()
  
  data["past_shows_count"]= Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time< datetime.now()).count()
  data["upcoming_shows_count"]= Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time>= datetime.now()).count()
  data["past_shows"]=[]
  for row in past_shows:
      this_id= row.id
      show_details=Show.query.get(this_id).get_details()
      data["past_shows"].append(show_details)
      
  data["upcoming_shows"]=[]    
  for row in upcoming_shows:
      this_id= row.id
      show_details=Show.query.get(this_id).get_details()
      data["upcoming_shows"].append(show_details)
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))   [0]
  return render_template('pages/show_venue.html', venue=data) #data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
 
  if form.validate_on_submit() :
      try:
          print("HI")
          new_venue = Venue(
              name=form.name.data,
              genres=form.genres.data,
              address=form.address.data,
              city=form.city.data,
              state=form.state.data,
              phone=form.phone.data,
              #website=form.website,
              facebook_link=form.facebook_link.data,
              image_link=form.image_link.data
              #seeking_talent=seeking_talent,
              #seeking_description=seeking_description,
            )
          #Venue.insert(new_venue)
          db.session.add(new_venue)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
         
      except SQLAlchemyError as e:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        print(e)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')
  #on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
#   TODO: on unsuccessful db insert, flash an error instead.
#   e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
#   see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term='%' + request.form.get('search_term', '') + '%'
  response= {
      "count" :Artist.query.filter(Artist.name.ilike(search_term)).count(),
      "data":Artist.query.filter(Artist.name.ilike(search_term)).all()
      }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  
  record= Artist.query.get(artist_id)
  
  data= record.__dict__
  past_shows= Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time< datetime.now()).all()
  upcoming_shows= Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time>= datetime.now()).all()
  
  data["past_shows_count"]= Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time< datetime.now()).count()
  data["upcoming_shows_count"]= Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time>= datetime.now()).count()
  data["past_shows"]=[]
  for row in past_shows:
      this_id= row.id
      show_details=Show.query.get(this_id).get_details()
      data["past_shows"].append(show_details)
      
  data["upcoming_shows"]=[]    
  for row in upcoming_shows:
      this_id= row.id
      show_details=Show.query.get(this_id).get_details()
      data["upcoming_shows"].append(show_details)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
#   try:
#       print("HI")
#   except SQLAlchemyError as e:
#       print(e)
#       flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
#     
    
  if form.validate_on_submit() :
      try:
          print("HI")
          new_artist = Artist(
              name=form.name.data,
              genres=form.genres.data,
              
              city=form.city.data,
              state=form.state.data,
              phone=form.phone.data,
              #website=form.website,
              facebook_link=form.facebook_link.data,
              image_link=form.image_link.data
              #seeking_talent=seeking_talent,
              #seeking_description=seeking_description,
            )
          #Artist.insert(new_Artist)
          db.session.add(new_artist)
          db.session.commit()
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
         
      except SQLAlchemyError as e:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        print(e)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
       
      finally:
     #db.session.close()
        return render_template('pages/home.html')  
  #return render_template('pages/home.html')
  #on successful db insert, flash success

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
#   data=[{
#     "venue_id": 1,
#     "venue_name": "The Musical Hop",
#     "artist_id": 4,
#     "artist_name": "Guns N Petals",
#     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     "start_time": "2019-05-21T21:30:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 5,
#     "artist_name": "Matt Quevedo",
#     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#     "start_time": "2019-06-15T23:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-01T20:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-08T20:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-15T20:00:00.000Z"
#   }]

    #shows1= Artist.query.join(Show)
    #shows = db.session.query(Show, Artist.image_link.label('artist_image_link')).join(Artist)
    #shows = db.session.query(Show, Artist.image_link.label('artist_image_link')).filter(Show.artist_id==Artist.id)
    shows = db.session.query(Show.id, Show.start_time, Show.artist_id, Show.venue_id, \
                Artist.image_link.label('artist_image_link'), Artist.name.label('artist_name'), Venue.name.label('venue_name')) \
                .filter(Show.artist_id==Artist.id) \
                .filter(Show.venue_id==Venue.id)
    return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  #print(form.artist_id)
  try:
   added_show=Show(
    artist_id=form.artist_id.data,
    venue_id=form.venue_id.data,
    start_time=form.start_time.data
    )
   db.session.add(added_show)
   db.session.commit()
   # on successful db insert, flash success
   flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. show could not be listed.')
  finally:
     #db.session.close()
     return render_template('pages/home.html')


  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

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
