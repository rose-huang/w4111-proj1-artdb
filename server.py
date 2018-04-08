#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

		python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import pandas as pd
import numpy as np

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.227.79.146/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.227.79.146/proj1part2"
#

DATABASEURI = "postgresql://rh2805:8420@35.227.79.146/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)
conn = engine.connect();
#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.



#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print "uh oh, problem connecting to database"
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print request.args


	#
	# example of a database query
	#
	cursor = g.conn.execute("SELECT artwork_id FROM artworks_is_at")
	names = []
	for result in cursor:
		names.append(result['artwork_id'])  # can also be accessed using result[0]
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


#@app.route('/another')
#def another():
#  return render_template("another.html")

#@app.route('/newuser')
#def newuser():
#  return render_template("newuser.html")


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
	
	if len(df)!=0:
			rec = 'Here are our recommendations:'
	else:
			rec = 'Sorry! Our database is too small to give you any helpful recommendations.'

	return render_template("index.html", rec = rec, table = df.to_html())

@app.route('/recommendartworkbyid',methods = ['POST'])
def recommendartworkbyid():
	artwork_id = request.form.get('get_artwork_id')
	#title = request.form.get('title')
	#place_creatd = request.form.get('place_creatd')
	#medium = request.form.get('get_medium')
	#year = request.form.get('year')

	if artwork_id != "all":
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name FROM artworks_is_at A1, artists A2, museums M, creates C WHERE A1.artwork_id = '{}' and C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id".format(artwork_id))
	else:
		artworkquery = conn.execute("SELECT A1.artwork_id, A1.title, A1.place_created, A1.medium, A1.year, A2.name AS artist_name, M.name AS museum_name FROM artworks_is_at A1, artists A2, museums M, creates C WHERE C.artwork_id = A1.artwork_id and C.artist_id = A2.artist_id and A1.museum_id = M.museum_id")

	artwork_id_list = []
	title_list = []
	place_created_list = []
	medium_list = []
	year_list = []
	artist_name_list = []
	museum_name_list = []

	for q in artworkquery:
		artwork_id_list.append(q['artwork_id'])
		title_list.append(q['title'])
		place_created_list.append(q['place_created'])
		medium_list.append(q['medium'])
		year_list.append(q['year'])
		artist_name_list.append(q['artist_name'])
		museum_name_list.append(q['museum_name'])

	
	artwork_id_array = np.asarray(artwork_id_list)
	title_array = np.asarray(title_list)
	place_created_array = np.asarray(place_created_list)
	medium_array = np.asarray(medium_list)
	year_array = np.asarray(year_list)
	artist_name_array = np.asarray(artist_name_list)
	museum_name_array = np.asarray(museum_name_list)

	df = pd.DataFrame(list(zip(artwork_id_array,title_array,place_created_array,medium_array,year_array,artist_name_array,museum_name_array)),columns=['Artwork ID', 'Title', 'Place Created', 'Medium', 'Year', 'Artist Name', 'Museum Name'])
	df.index = np.arange(1, len(df) + 1) 
	
	if len(df)!=0:
			rec = 'Here are our recommendations:'
	else:
			rec = 'Sorry! Our database is too small to give you any helpful recommendations.'

	return render_template("index.html", rec = rec, artworktable = df.to_html())

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
	return redirect('/')


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
