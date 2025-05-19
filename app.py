import appconfig
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, render_template, request

print("Connecting to database...")
conn = psycopg2.connect(
	user=appconfig.db_user,
	password=appconfig.db_user_password,
	host=appconfig.db_host,
	port=appconfig.postgres_port,
	database=appconfig.db_name,
	options="-c search_path=dbo,public",
)

cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

app = Flask(__name__)


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/sites/", methods=["GET"])
def get_sites():
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT * FROM site ORDER BY name asc OFFSET %s LIMIT 20"
	cursor.execute(query, (20 * (int(page)-1),))
	siteitems = cursor.fetchall()
	totalitems = getSitesPageCount()
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": siteitems, "page": pagedict}), 200


@app.route("/feeds/", methods=["GET"])
def get_feed():
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"
	cursor.execute(query, ((int(page)-1)*20 ,))
	feeditems = cursor.fetchall()
	print(feeditems)
	totalitems = getPageCount()
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


@app.route("/search/", methods=["GET"])
def get_searchfeed():
	squery = request.args["q"]
	if len(query) < 1:
		return jsonify({"error": "Missing query text."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts WHERE LIKE %s OR content LIKE %s LIMIT 20 OFFSET %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id e.sitetype_id ORDER BY posts.published_date DESC;"
	cursor.execute(query, (squery, squery, 10 * page))
	feeditems = cursor.fetchall()
	totalitems = getSearchPageCount(query)
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


@app.route("/feeds/sites/<siteid>", methods=["GET"])
def get_browseBySiteId(siteid):
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts WHERE posts.site_id = %s LIMIT 20 OFFSET %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id ORDER BY posts.published_date DESC;"
	cursor.execute(query, (siteid, 20 * (int(page)-1)))
	feeditems = cursor.fetchall()
	totalitems = getSiteIdPageCount(siteid)
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


@app.route("/feeds/author/<authorid>/", methods=["GET"])
def get_browseByAuthorId(authorid):
	page = request.args["p"]
	if page == None:
		page = 0
	query = """SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts WHERE posts.author_id = %s LIMIT 20 OFFSET %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id ORDER BY posts.published_date DESC;"""
	cursor.execute(query, (authorid, 20 * (int(page)-1)))
	feeditems = cursor.fetchall()
	totalitems = getAuthorCount(authorid)
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


@app.route("/feeds/<sitetype>", methods=["GET"])
def get_browseByType(sitetype):
	if len(sitetype) < 1 and type(service) != str:
		return jsonify({"error": "Missing type."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	query = """SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts WHERE sitetype.name LIKE %s LIMIT 20 OFFSET %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id ORDER BY posts.published_date DESC;"""
	cursor.execute(query, (sitetype, 20 * (int(page)-1)))
	feeditems = cursor.fetchall()
	totalitems = getSiteTypePageCount(sitetype)
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


@app.route("/feeds/anime/<id>", methods=["GET"])
def get_browseByAnimeTitle(aniid):
	if len(aniid) < 1:
		return jsonify({"error": "Missing Anime Title ID."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	query = """SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts WHERE anime.anime_id = i$ LIMIT 20 OFFSET %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id ORDER BY posts.published_date DESC;"""
	cursor.execute(query, (sitetype, 20 * (int(page)-1)))
	feeditems = cursor.fetchall()
	totalitems = getAnimeTitlePageCount(aniid)
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


@app.route("/feeds/anime/<service>/id", methods=["GET"])
def get_browseByAnimeTitleAndService(service, aniid):
	if len(service) < 1 and type(service) != str:
		return jsonify({"error": "Missing service or invalid input."}), 400
	elif len(aniid) < 1:
		return jsonify({"error": "Missing Anime Title ID."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	lowercaseService = lower(service)
	servicewhereclause = ""
	if lowercaseService == "mal":
		servicewhereclause = "anime.mal_id = %s"
	elif lowercaseService == "anilist":
		servicewhereclause == "anime.anilist_id = %s"
	else:
		return (
			jsonify(
				{"error": "Invalid service specificed. Choices are mal and anilist."}
			),
			400,
		)
	query = (
		"""SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, mastodon, site.name AS websitename, url, sitetype.name AS type FROM posts WHERE """
		+ servicewhereclause
		+ """ LIMIT 20 OFFSET %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id ORDER BY posts.published_date DESC;"""
	)
	cursor.execute(query, (aniid, 20 * (int(page)-1)))
	feeditems = cursor.fetchall()
	totalitems = getAnimeTitlePageCount(aniid)
	pagedict = {
		"next": (totalitems - int(page))
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 > 0 else None,
	}
	return jsonify({"items": addAnimeRelationInfo(feeditems), "page": pagedict}), 200


def getSearchPageCount(squery):
	query = """SELECT count(*) AS count from posts WHERE title LIKE %s OR content LIKE %s;"""
	cursor.execute(query, (squery, squery))
	items = cursor.fetchall()
	return items[0]["count"]


def getSiteIdPageCount(siteid):
	query = """SELECT count(*) AS count from posts WHERE site_id = %s;"""
	cursor.execute(query, (query,))
	items = cursor.fetchall()
	return items[0]["count"]


def getSiteTypePageCount(type):
	query = """SELECT count(*) AS count from posts WHERE sitetype.name = %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id;"""
	cursor.execute(query, (type,))
	items = cursor.fetchall()
	return items[0]["count"]


def getAuthorCount(authorid):
	query = """SELECT count(*) AS count from posts WHERE sposts.author_id = %s INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id;"""
	cursor.execute(query, (authorid,))
	items = cursor.fetchall()
	return items[0]["count"]


def getAnimeTitlePageCount(aniid):
	query = """SELECT count(*) AS count FROM posts WHERE anime.anime_id = i$ INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id;"""
	cursor.execute(query, (aniid,))
	items = cursor.fetchall()
	return items[0]["count"]


def getPageCount():
	query = "SELECT count(*) AS count from posts;"
	cursor.execute(query)
	items = cursor.fetchall()
	return items[0]["count"]


def getSitesPageCount():
	query = "SELECT count(*) AS count from site;"
	cursor.execute(query)
	items = cursor.fetchall()
	return items[0]["count"]


def getServiceAnimePageAcount(whereserviceclause):
	query = (
		"SELECT count(*) AS count FROM posts WHERE "
		+ servicewhereclause
		+ " INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id;"
	)
	cursor.execute(query)
	items = cursor.fetchall()
	return items[0]["count"]


def addAnimeRelationInfo(feeditems):
	for post in feeditems:
		query = "SELECT * from anime INNER JOIN post_relatedanime ON anime.anime_id = post_relatedanime.anime_id WHERE post_relatedanime.post_id = %s;"
		cursor.execute(query, (post["post_id"],))
		items = cursor.fetchall()
		if len(items) > 0:
			post["related_anime"] = items
		else:
			post["related_anime"] = []

	return feeditems


if __name__ == "__main__":
	app.run(debug=True)
