import appconfig
import psycopg2
from flask import Flask, jsonify, render_template, request

print("Connecting to database...")
connection = psycopg2.connect(
	user=appconfig.db_user,
	password=appconfig.db_user_password,
	host=appconfig.db_host,
	port=appconfig.postgres_port,
	database="postgres_db",
	options="-c search_path=dbo,public",
)

cursor = conn.cursor()

app = Flask(__name__)


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/feeds/", methods=["GET"])
def get_feed():
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT title, content, post_url, thumbnail_url, published_date, author.name AS 'author', mastodon, site.name AS 'websitename', url, sitetype.name AS 'type' FROM posts LIMIT 20 OFFSET i% INNER JOIN site post.site_id = site.site_id; INNER JOIN author post.author_id = author.author_id INNER JOIN sitetype site.sitetype_id = sitetype_id ORDER BY posts.published_date DSC;"
	cursor.execute(query,(20 * page))
	feeditems = cursor.fetchall()
	totalitems = getPageCount(query)
	pagedict = {
		"next": (totalitems - page)
		if page + 20 > totalitems
		else (None)
		if page == totalitems
		else page + 20,
		"prev": (page - 20) if page - 20 > 0 else None,
	}
	return jsonify({"items": feeditems, "page": pagedict}), 200


@app.route("/search/", methods=["GET"])
def get_searchfeed():
	squery = request.args["q"]
	if len(query) < 1:
		return jsonify({"error": "Missing query text."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT title, content, post_url, thumbnail_url, published_date, author.name AS 'author', mastodon, site.name AS 'websitename', url, sitetype.name AS 'type' FROM posts WHERE LIKE %s OR content LIKE %s LIMIT 20 OFFSET i% INNER JOIN site post.site_id = site.site_id; INNER JOIN author post.author_id = author.author_id INNER JOIN sitetype site.sitetype_id = sitetype_id ORDER BY posts.published_date DSC;"
	cursor.execute(query, (squery, squery, 10 * page))
	feeditems = cursor.fetchall()
	totalitems = getSearchPageCount(query)
	pagedict = {
		"next": (totalitems - page)
		if page + 20 > totalitems
		else (None)
		if page == totalitems
		else page + 20,
		"prev": (page - 20) if page - 20 > 0 else None,
	}
	return jsonify({"items": feeditems, "page": pagedict}), 200
	
@app.route('/feeds/sites/<siteid>', methods=['GET'])
def get_browseBySiteId(siteid):
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT title, content, post_url, thumbnail_url, published_date, author.name AS 'author', mastodon, site.name AS 'websitename', url, sitetype.name AS 'type' FROM posts WHERE posts.site_id = i% LIMIT 20 OFFSET i% INNER JOIN site post.site_id = site.site_id; INNER JOIN author post.author_id = author.author_id INNER JOIN sitetype site.sitetype_id = sitetype_id ORDER BY posts.published_date DSC;"
	cursor.execute(query, (siteid, 20 * page))
	feeditems = cursor.fetchall()
	totalitems = getSiteIdPageCount(siteid)
	pagedict = {
		"next": (totalitems - page)
		if page + 20 > totalitems
		else (None)
		if page == totalitems
		else page + 20,
		"prev": (page - 20) if page - 20 > 0 else None,
	}
	return jsonify({"items": feeditems, "page": pagedict}), 200
	
@app.route('/feeds/<sitetype>', methods=['GET'])
def get_browseByType(sitetype):
	if len(sitetype) < 1:
		return jsonify({"error": "Missing type."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT title, content, post_url, thumbnail_url, published_date, author.name AS 'author', mastodon, site.name AS 'websitename', url, sitetype.name AS 'type' FROM posts WHERE sitetype.name LIKE s% LIMIT 20 OFFSET i% INNER JOIN site post.site_id = site.site_id; INNER JOIN author post.author_id = author.author_id INNER JOIN sitetype site.sitetype_id = sitetype_id ORDER BY posts.published_date DSC;"
	cursor.execute(query, (sitetype, 20 * page)
	feeditems = cursor.fetchall()
	totalitems = getSiteTypePageCount(sitetype)
	pagedict = {
		"next": (totalitems - page)
		if page + 20 > totalitems
		else (None)
		if page == totalitems
		else page + 20,
		"prev": (page - 20) if page - 20 > 0 else None,
	}
	return jsonify({"items": feeditems, "page": pagedict}), 200

@app.route('/feeds/anime/<id>', methods=['GET'])
def get_browseByAnimeTitle(aniid):
	
@app.route('/feeds/anime/<service>/id', methods=['GET'])
def get_browseByAnimeTitleAndService(service, aniid):

def getSearchPageCount(squery):
	query = "SELECT count(*) AS 'count' from posts WHERE title LIKE %s OR content LIKE %s ORDER BY published_date DSC;"
	cursor.execute(query, (squery, squery))
	items = cursor.fetchall()
	return items[0]["count"]

def getSiteIdPageCount(siteid):
	query = "SELECT count(*) AS 'count' from posts WHERE site_id = i% ORDER BY published_date DSC;"
	cursor.execute(query, (query))
	items = cursor.fetchall()
	return items[0]["count"]

def getSiteTypePageCount(type):
	query = "SELECT count(*) AS 'count' from posts WHERE sitetype.name = s% INNER JOIN site post.site_id = site.site_id; INNER JOIN author post.author_id = author.author_id INNER JOIN sitetype site.sitetype_id = sitetype_id ORDER BY published_date DSC;"
	cursor.execute(query, type)
	items = cursor.fetchall()
	return items[0]["count"]

def getPageCount():
	query = "SELECT count(*) AS 'count' from posts ORDER BY published_date DSC;"
	cursor.execute(query)
	items = cursor.fetchall()
	return items[0]["count"]


if __name__ == "__main__":
	app.run()
