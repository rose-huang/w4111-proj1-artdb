#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases

To run locally:

		python server.py

Go to http://localhost:8111 in your browser.

"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import pandas as pd
import numpy as np

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


DATABASEURI = "postgresql://rh2805:8420@35.227.79.146/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)
conn = engine.connect();
#global variable for user login
#note: only one user can log in at a time 
loggedinid = 0

def userlogin(n):
	global loggedinid
	loggedinid = n

def userlogout():
	global loggedinid 
	loggedinid = 0


def update():

	user_names = conn.execute("SELECT user_id, name FROM users")
	names = []
	for result in user_names:
		nameandid = result['name'] + " (user id = " +result['user_id']+")"
		names.append(nameandid)

	art_id = conn.execute("SELECT artwork_id FROM artworks_is_at ORDER BY artwork_id::int")
	art_ids = []
	for result in art_id:
		art_ids.append(result['artwork_id'])

	art_medium = conn.execute("SELECT DISTINCT medium FROM artworks_is_at ORDER BY medium")
	art_mediums = []
	for result in art_medium:
		art_mediums.append(result['medium'])

	art_place = conn.execute("SELECT DISTINCT place_created FROM artworks_is_at  WHERE place_created != 'NULL' ORDER BY place_created")
	art_places = []
	for result in art_place:
		art_places.append(result['place_created'])

	art_title = conn.execute("SELECT DISTINCT title FROM artworks_is_at ORDER BY title")
	art_titles = []
	for result in art_title:
		art_titles.append(result['title'])

	art_year = conn.execute("SELECT DISTINCT year FROM artworks_is_at ORDER BY year")
	art_years = []
	for result in art_year:
		art_years.append(result['year'])

	mus_name = conn.execute("SELECT DISTINCT name FROM museums ORDER BY name")
	mus_names = []
	for result in mus_name:
		mus_names.append(result['name'])

	mov_name = conn.execute("SELECT DISTINCT name FROM movements ORDER BY name")
	mov_names = []
	for result in mov_name:
		mov_names.append(result['name'])

	artid_title = conn.execute("SELECT artwork_id, title FROM artworks_is_at ORDER BY artwork_id::int")
	artid_titles = []
	for result in artid_title:
		idandtitle = result['artwork_id'] + " - " +result['title']
		artid_titles.append(idandtitle)

	artistid_name = conn.execute("SELECT artist_id, name FROM artists ORDER BY artist_id::int")
	artistid_names = []
	for result in artistid_name:
		idandname = result['artist_id'] + " - " +result['name']
		artistid_names.append(idandname)

	museumid_name = conn.execute("SELECT museum_id, name FROM museums ORDER BY museum_id::int")
	museumid_names = []
	for result in museumid_name:
		idandname = result['museum_id'] + " - " +result['name']
		museumid_names.append(idandname)

	print("logged in id is ")
	print(loggedinid)
	context = dict(user_names = names, artwork_ids = art_ids, artwork_mediums = art_mediums, artwork_place_created = art_places, artwork_titles = art_titles, artwork_years = art_years, museum_names = mus_names, movement_names = mov_names, artid_titles = artid_titles, artistid_names = artistid_names, loggedinid = loggedinid, museumid_names = museumid_names)

	return context

@app.before_request
def before_request():

	try:
		g.conn = engine.connect()
	except:
		print "uh oh, problem connecting to database"
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):

	try:
		g.conn.close()
	except Exception as e:
		pass


@app.route('/', methods=['GET','POST'])
def index():

	user = request.form.get('get_user')
	if user:
		userinfo = user.split(" (user id = ")
		user = userinfo[1]
		user = user[:-1]
		userlogin(user)

	if request.form.get("logout") == "Logout":
		userlogout()

	if request.form.get("logout") == "Logout":
		userlogout()

	print request.args

	context = update()

	return render_template("index.html", **context)


@app.route('/adduser',methods=['POST'])
def adduser():
	new_user_name = request.form.get('new_user_name')
	if len(new_user_name) != 0:
		countusers = conn.execute("SELECT COUNT(*) FROM users")
		count = 0
		for u in countusers:
			count = u[0]
		count += 1
		conn.execute("INSERT INTO users VALUES (%s,%s)", count, new_user_name)
	return redirect('/')
	
@app.route('/addartworkpref',methods=['POST'])
def addartworkpref():
	art_pref = request.form.get('art_pref')
	art_prefs = art_pref.split(" - ")
	art_pref_id = art_prefs[0] 

	pref = conn.execute("SELECT COUNT(*) FROM likes1 WHERE user_id = %s AND artwork_id = %s", loggedinid, art_pref_id)
	for u in pref:
		count = u[0]
	if count == 0:
		conn.execute("INSERT INTO likes1 VALUES (%s,%s)", loggedinid, art_pref_id)
	return redirect('/')

@app.route('/addartistpref',methods=['POST'])
def addartistpref():
	artist_pref = request.form.get('artist_pref')
	artist_prefs = artist_pref.split(" - ")
	artist_pref_id = artist_prefs[0] 

	pref = conn.execute("SELECT COUNT(*) FROM likes2 WHERE user_id = %s AND artist_id = %s", loggedinid, artist_pref_id)
	for u in pref:
		count = u[0]
	if count == 0:
		conn.execute("INSERT INTO likes2 VALUES (%s,%s)", loggedinid, artist_pref_id)
	return redirect('/')

@app.route('/addmovementpref',methods=['POST'])
def addmovementpref():
	movement_pref = request.form.get('movement_pref')

	pref = conn.execute("SELECT COUNT(*) FROM likes3 WHERE user_id = %s AND name = %s", loggedinid, movement_pref)
	for u in pref:
		count = u[0]
	if count == 0:
		conn.execute("INSERT INTO likes3 VALUES (%s,%s)", movement_pref, loggedinid)
	return redirect('/')

@app.route('/addvismus',methods=['POST'])
def addvismus():
	visited_mus = request.form.get('visited_mus')
	visitedmuss = visited_mus.split(" - ")
	visitedmus_id = visitedmuss[0] 

	pref = conn.execute("SELECT COUNT(*) FROM visited WHERE user_id = %s AND museum_id = %s", loggedinid, visitedmus_id)
	for u in pref:
		count = u[0]
	if count == 0:
		conn.execute("INSERT INTO visited VALUES (%s,%s)", loggedinid, visitedmus_id)
	return redirect('/')


@app.route('/recommendmuseum',methods = ['POST'])
def recommendmuseum():
	museumname = request.form.get('get_museumname')
	museumdiscount = request.form.get('get_museumdiscount')
	if museumdiscount == "all":
		if museumname == "all":
			museumquery = conn.execute("SELECT M.name as mname, M.location as mlocation, M.cu_discount as mdiscount FROM museums M")
		else:
			museumquery = conn.execute("SELECT M.name as mname, M.location as mlocation, M.cu_discount as mdiscount FROM museums M WHERE M.name = '{}'".format(museumname))
	else:
		if museumname == "all":
			museumquery = conn.execute("SELECT M.name as mname, M.location as mlocation, M.cu_discount as mdiscount FROM museums M WHERE M.cu_discount = '{}'".format(museumdiscount))
		else:
			museumquery = conn.execute("SELECT M.name as mname, M.location as mlocation, M.cu_discount as mdiscount FROM museums M WHERE M.name = '{}' and M.cu_discount = '{}'".format(museumname, museumdiscount))
	m_name = []
	m_location = []
	m_free = []

	for q in museumquery:
		m_name.append(q['mname'])
		m_location.append(q['mlocation'])
		m_free.append(q['mdiscount'])
	
	mnames = np.asarray(m_name)
	mlocations = np.asarray(m_location)
	mdiscounts = np.asarray(m_free)

	df = pd.DataFrame(list(zip(mnames,mlocations,mdiscounts)),columns=['Museum Name', 'Museum Location', 'Discount'])
	df.index = np.arange(1, len(df) + 1) 
	
	context = update()
	return render_template("index.html", museumtable = df.to_html(), **context)

# Recommend Artwork By Artwork ID
@app.route('/recommendartworkbyid',methods = ['POST'])
def recommendartworkbyid():
	artwork_id = request.form.get('get_artwork_id')

	if artwork_id != "all":
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE A1.artwork_id = '{}' and C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id".format(artwork_id))
	else:
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id")

	artwork_id_list = []
	title_list = []
	place_created_list = []
	medium_list = []
	year_list = []
	artist_name_list = []
	museum_name_list = []
	exhibition_name_list = []

	for q in artworkquery:
		artwork_id_list.append(q['artwork_id'])
		title_list.append(q['title'])
		place_created_list.append(q['place_created'])
		medium_list.append(q['medium'])
		year_list.append(q['year'])
		artist_name_list.append(q['artist_name'])
		museum_name_list.append(q['museum_name'])
		exhibition_name_list.append(q['exhibition_name'])

	
	artwork_id_array = np.asarray(artwork_id_list)
	title_array = np.asarray(title_list)
	place_created_array = np.asarray(place_created_list)
	medium_array = np.asarray(medium_list)
	year_array = np.asarray(year_list)
	artist_name_array = np.asarray(artist_name_list)
	museum_name_array = np.asarray(museum_name_list)
	exhibition_name_array = np.asarray(exhibition_name_list)

	df = pd.DataFrame(list(zip(artwork_id_array,title_array,place_created_array,medium_array,year_array,artist_name_array,museum_name_array, exhibition_name_array)),columns=['Artwork ID', 'Title', 'Place Created', 'Medium', 'Year', 'Artist Name', 'Museum Name', 'Exhibition Name'])
	df.index = np.arange(1, len(df) + 1) 
	
	context = update()
	return render_template("index.html", artworkidtable = df.to_html(), **context)

# Recommend Artwork by Title
@app.route('/recommendartworkbytitle',methods = ['POST'])
def recommendartworkbytitle():
	title = request.form.get('get_title')

	if title != "all":
		q = "SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE A1.title = %s and C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id;".format(title)
		artworkquery = conn.execute(q, (title))

	else:
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id")

	artwork_id_list = []
	title_list = []
	place_created_list = []
	medium_list = []
	year_list = []
	artist_name_list = []
	museum_name_list = []
	exhibition_name_list = []

	for q in artworkquery:
		artwork_id_list.append(q['artwork_id'])
		title_list.append(q['title'])
		place_created_list.append(q['place_created'])
		medium_list.append(q['medium'])
		year_list.append(q['year'])
		artist_name_list.append(q['artist_name'])
		museum_name_list.append(q['museum_name'])
		exhibition_name_list.append(q['exhibition_name'])

	
	artwork_id_array = np.asarray(artwork_id_list)
	title_array = np.asarray(title_list)
	place_created_array = np.asarray(place_created_list)
	medium_array = np.asarray(medium_list)
	year_array = np.asarray(year_list)
	artist_name_array = np.asarray(artist_name_list)
	museum_name_array = np.asarray(museum_name_list)
	exhibition_name_array = np.asarray(exhibition_name_list)

	df = pd.DataFrame(list(zip(artwork_id_array,title_array,place_created_array,medium_array,year_array,artist_name_array,museum_name_array,exhibition_name_array)),columns=['Artwork ID', 'Title', 'Place Created', 'Medium', 'Year', 'Artist Name', 'Museum Name', 'Exhibition Name'])
	df.index = np.arange(1, len(df) + 1) 
	
	context = update()
	return render_template("index.html", artworktitletable = df.to_html(), **context)

# recommend artwork by place created
@app.route('/recommendartworkbyplacecreated',methods = ['POST'])
def recommendartworkbyplacecreated():

	place_created = request.form.get('get_place_created')

	if place_created != "all":
		q = "SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE A1.place_created = %s and C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id;".format(place_created)
		artworkquery = conn.execute(q, (place_created))
	else:
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id")

	artwork_id_list = []
	title_list = []
	place_created_list = []
	medium_list = []
	year_list = []
	artist_name_list = []
	museum_name_list = []
	exhibition_name_list = []

	for q in artworkquery:
		artwork_id_list.append(q['artwork_id'])
		title_list.append(q['title'])
		place_created_list.append(q['place_created'])
		medium_list.append(q['medium'])
		year_list.append(q['year'])
		artist_name_list.append(q['artist_name'])
		museum_name_list.append(q['museum_name'])
		exhibition_name_list.append(q['exhibition_name'])
	
	artwork_id_array = np.asarray(artwork_id_list)
	title_array = np.asarray(title_list)
	place_created_array = np.asarray(place_created_list)
	medium_array = np.asarray(medium_list)
	year_array = np.asarray(year_list)
	artist_name_array = np.asarray(artist_name_list)
	museum_name_array = np.asarray(museum_name_list)
	exhibition_name_array = np.asarray(exhibition_name_list)

	df = pd.DataFrame(list(zip(artwork_id_array,title_array,place_created_array,medium_array,year_array,artist_name_array,museum_name_array,exhibition_name_array)),columns=['Artwork ID', 'Title', 'Place Created', 'Medium', 'Year', 'Artist Name', 'Museum Name', 'Exhibition Name'])
	df.index = np.arange(1, len(df) + 1) 
	
	context = update()
	return render_template("index.html", artworkplacecreatedtable = df.to_html(), **context)

@app.route('/recommendartworkbymedium',methods = ['POST'])
def recommendartworkbymedium():
	medium = request.form.get('get_medium')

	if medium != "all":
		q = "SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE A1.medium = %s and C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id;".format(medium)
		artworkquery = conn.execute(q, (medium))

	else:
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id")

	artwork_id_list = []
	title_list = []
	place_created_list = []
	medium_list = []
	year_list = []
	artist_name_list = []
	museum_name_list = []
	exhibition_name_list = []

	for q in artworkquery:
		artwork_id_list.append(q['artwork_id'])
		title_list.append(q['title'])
		place_created_list.append(q['place_created'])
		medium_list.append(q['medium'])
		year_list.append(q['year'])
		artist_name_list.append(q['artist_name'])
		museum_name_list.append(q['museum_name'])
		exhibition_name_list.append(q['exhibition_name'])
	
	artwork_id_array = np.asarray(artwork_id_list)
	title_array = np.asarray(title_list)
	place_created_array = np.asarray(place_created_list)
	medium_array = np.asarray(medium_list)
	year_array = np.asarray(year_list)
	artist_name_array = np.asarray(artist_name_list)
	museum_name_array = np.asarray(museum_name_list)
	exhibition_name_array = np.asarray(exhibition_name_list)

	df = pd.DataFrame(list(zip(artwork_id_array,title_array,place_created_array,medium_array,year_array,artist_name_array,museum_name_array,exhibition_name_array)),columns=['Artwork ID', 'Title', 'Place Created', 'Medium', 'Year', 'Artist Name', 'Museum Name', 'Exhibition Name'])
	df.index = np.arange(1, len(df) + 1) 
	
	context = update()
	return render_template("index.html", artworkmediumtable = df.to_html(), **context)

@app.route('/recommendartworkbyyear',methods = ['POST'])
def recommendartworkbyyear():
	year = request.form.get('get_year')

	if year != "all":
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE A1.year = '{}' and C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id".format(year))
	else:
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name, E.name AS exhibition_name FROM artworks_is_at A1, artists A2, museums M, creates C, exhibitions_is_in2 E, is_in3 I WHERE C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id and I.artwork_id = A1.artwork_id and I.exhibition_id = E.exhibition_id")

	artwork_id_list = []
	title_list = []
	place_created_list = []
	medium_list = []
	year_list = []
	artist_name_list = []
	museum_name_list = []
	exhibition_name_list = []

	for q in artworkquery:
		artwork_id_list.append(q['artwork_id'])
		title_list.append(q['title'])
		place_created_list.append(q['place_created'])
		medium_list.append(q['medium'])
		year_list.append(q['year'])
		artist_name_list.append(q['artist_name'])
		museum_name_list.append(q['museum_name'])
		exhibition_name_list.append(q['exhibition_name'])
	
	artwork_id_array = np.asarray(artwork_id_list)
	title_array = np.asarray(title_list)
	place_created_array = np.asarray(place_created_list)
	medium_array = np.asarray(medium_list)
	year_array = np.asarray(year_list)
	artist_name_array = np.asarray(artist_name_list)
	museum_name_array = np.asarray(museum_name_list)
	exhibition_name_array = np.asarray(exhibition_name_list)

	df = pd.DataFrame(list(zip(artwork_id_array,title_array,place_created_array,medium_array,year_array,artist_name_array,museum_name_array,exhibition_name_array)),columns=['Artwork ID', 'Title', 'Place Created', 'Medium', 'Year', 'Artist Name', 'Museum Name', 'Exhibition Name'])
	df.index = np.arange(1, len(df) + 1) 
	
	context = update()
	return render_template("index.html", artworkyeartable = df.to_html(), **context)

@app.route('/getuserinfo',methods = ['POST'])
def getuserinfo():

	# user's artworks
	qlikes1 = "SELECT A.title FROM users U, likes1 L, artworks_is_at A WHERE U.user_id = %s and U.user_id = L.user_id and L.artwork_id = A.artwork_id;".format(loggedinid)
	userartworkquery = conn.execute(qlikes1, (loggedinid))

	title_list = []

	for q in userartworkquery:
		title_list.append(q['title'])

	title_array = np.asarray(title_list)

	df_artwork = pd.DataFrame(list(zip(title_array)),columns=['Artwork Title'])
	df_artwork.index = np.arange(1, len(df_artwork) + 1) 
	
	# user's artists
	qlikes2 = "SELECT A.name FROM users U, likes2 L, artists A WHERE U.user_id = %s and U.user_id = L.user_id and L.artist_id = A.artist_id;".format(loggedinid)
	userartistquery = conn.execute(qlikes2, (loggedinid))

	artistname_list = []

	for q in userartistquery:
		artistname_list.append(q['name'])

	artistname_array = np.asarray(artistname_list)

	df_artist = pd.DataFrame(list(zip(artistname_array)),columns=['Artist Name'])
	df_artist.index = np.arange(1, len(df_artist) + 1) 
	
	# user's movement
	qlikes3 = "SELECT M.name FROM users U, likes3 L, movements M WHERE U.user_id = %s and U.user_id = L.user_id and L.name = M.name;".format(loggedinid)
	usermovementquery = conn.execute(qlikes3, (loggedinid))

	movement_list = []

	for q in usermovementquery:
		movement_list.append(q['name'])

	movement_array = np.asarray(movement_list)

	df_movement = pd.DataFrame(list(zip(movement_array)),columns=['Movement Name'])
	df_movement.index = np.arange(1, len(df_movement) + 1) 
	
	if len(df_movement)!=0:
			rec = 'Here are our recommendations:'
	else:
			rec = 'Sorry! Our database is too small to give you any helpful recommendations.'

	# user's visited museums
	visited = "SELECT M.name FROM museums M, visited V, users U WHERE U.user_id = %s and U.user_id = V.user_id and M.museum_id = V.museum_id;".format(loggedinid)
	uservisitedquery = conn.execute(visited, (loggedinid))

	visted_list = []

	for q in uservisitedquery:
		visted_list.append(q['name'])

	visited_array = np.asarray(visted_list)

	df_visited = pd.DataFrame(list(zip(visited_array)), columns=['Visited Museum Name'])
	df_visited.index = np.arange(1, len(df_visited) + 1) 


	#the actual recommendations
	qrec = "(SELECT Art.title AS art_title, Artist.name AS artist_name, M.name AS mov_name, Mus.name AS mus_name FROM Artworks_is_at Art, Artists Artist, Creates C, Is_in1 I, movements M, Museums Mus WHERE Art.museum_id = Mus.museum_id and C.artist_id = Artist.artist_id and C.artwork_id = Art.artwork_id and I.name = M.name and I.artwork_id = Art.artwork_id and Artist.name in (SELECT A.name FROM users U, likes2 L, artists A WHERE U.user_id = %s and U.user_id = L.user_id and L.artist_id = A.artist_id)) UNION (SELECT Art.title AS art_title, Artist.name AS artist_name, M.name AS mov_name, Mus.name AS mus_name FROM Artworks_is_at Art, Artists Artist, Creates C, Is_in1 I, movements M, Museums Mus WHERE Art.museum_id = Mus.museum_id and C.artist_id = Artist.artist_id and C.artwork_id = Art.artwork_id and I.name = M.name and I.artwork_id = Art.artwork_id and M.name in (SELECT M.name FROM users U, likes3 L, movements M WHERE U.user_id = %s and U.user_id = L.user_id and L.name = M.name))"
	userrecquery = conn.execute(qrec, (loggedinid), (loggedinid)) 

	userrec_art_title_list = []
	userrec_artist_name_list = []
	userrec_move_name_list = []
	userrec_mus_name_list = []

	for q in userrecquery:
		userrec_art_title_list.append(q['art_title'])
		userrec_artist_name_list.append(q['artist_name'])
		userrec_move_name_list.append(q['mov_name'])
		userrec_mus_name_list.append(q['mus_name'])

	userrec_art_title_array = np.asarray(userrec_art_title_list)
	userrec_artist_name_array = np.asarray(userrec_artist_name_list)
	userrec_move_name_array = np.asarray(userrec_move_name_list)
	userrec_mus_name_array = np.asarray(userrec_mus_name_list)


	df_userrec = pd.DataFrame(list(zip(userrec_art_title_array, userrec_artist_name_array, userrec_move_name_array, userrec_mus_name_array)),columns=['Artwork Title', 'Artist Name', 'Movement Name', 'Museum Name'])
	df_userrec.index = np.arange(1, len(df_userrec) + 1) 

	context = update()
	likemsg = "You have indicated that you like: "
	recmsg = "Based on your preferences, we recommend these artworks: "
	musmsg = "You have visited these museums: "
	return render_template("index.html", userartworktable = df_artwork.to_html(), userartisttable = df_artist.to_html(), usermovementtable = df_movement.to_html(), uservisitedtable = df_visited.to_html(), userrectable = df_userrec.to_html(), likemessage = likemsg, recmessage = recmsg, musmessage = musmsg, **context)


@app.route('/searchartistbymovement',methods = ['POST'])
def searchartistbymovement():
	movement = request.form.get('get_movement')

	if movement != "all":
		artistquery = conn.execute("SELECT A.name AS artist_name FROM participates_in P, artists A, Movements M WHERE M.name = '{}' and M.name = P.name and P.artist_id = A.artist_id".format(movement))
	else:
		artistquery = conn.execute("SELECT A.name AS artist_name FROM participates_in P, artists A, Movements M WHERE M.name = P.name and P.artist_id = A.artist_id")

	artist_list = []

	for q in artistquery:
		artist_list.append(q['artist_name'])

	artist_array = np.asarray(artist_list)

	df_artist = pd.DataFrame(list(zip(artist_array)),columns=['Artist Name'])
	df_artist.index = np.arange(1, len(df_artist) + 1) 
	
	context = update()
	return render_template("index.html", artisttable = df_artist.to_html(), **context)

@app.route('/login')
def login():
		abort(401)
		this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

				python server.py

		Show the help text using:

				python server.py --help

		"""

		HOST, PORT = host, port
		print "running on %s:%d" % (HOST, PORT)
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


	run()
