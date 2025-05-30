import appconfig
import psycopg2
import psycopg2.extras
from json_tricks import dumps
from flask import Flask, jsonify, render_template, request, send_from_directory
from datetime import datetime

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
	page = request.args.get('p') or '0'
	query = "SELECT * FROM site ORDER BY name asc OFFSET %s LIMIT 20"
	try:
		cursor.execute(query, (int(page),))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	siteitems = cursor.fetchall()
	totalitems = getSitesPageCount()
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : siteitems}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/feeds/", methods=["GET"])
def get_feed():
	page = request.args.get('p') or '0'
	exclude = request.args.get('extypeid') or "";
	
	if type(exclude) is not str:
		exclude = str(exclude)
	
	query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"
	if len(exclude) > 0:
		texcludearray = exclude.split(",")
		fexclude = []
		for typeid in texcludearray:
			if typeid.isnumeric():
				fexclude.append(typeid)
		if len(fexclude) > 0:		
			query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE site.sitetype_id != ALL(%s) ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"
			excludestrarray = (",".join(fexclude)) if len(fexclude) > 1 else fexclude[0]
			excludestrarray = "{" + excludestrarray + "}"
			try:
				cursor.execute(query, (excludestrarray, int(page)))
			except Exception as e:
				conn.rollback()
				return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
		else:
			try:
				cursor.execute(query, (int(page) ,))
			except Exception as e:
				conn.rollback()
				return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
			exclude = ""
	else:
		cursor.execute(query, (int(page) ,))
	feeditems = cursor.fetchall()
	print(feeditems)
	totalitems = getPageCount(exclude)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/search/", methods=["GET"])
def get_searchfeed():
	squery = request.args["q"]
	squery = "%" + squery + "%"
	if len(squery) < 1:
		return jsonify(data={"error": "Missing query text."}), 400
	page = request.args.get('p') or '0'
	query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE title LIKE %s OR content LIKE %s ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"
	try:
		cursor.execute(query, (squery, squery, int(page),))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	feeditems = cursor.fetchall()
	totalitems = getSearchPageCount(query)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/feeds/sites/<siteid>", methods=["GET"])
def get_browseBySiteId(siteid):
	page = request.args.get('p') or '0'
	query = "SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE posts.site_id = %s ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"
	try:
		cursor.execute(query, (siteid, int(page)))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	feeditems = cursor.fetchall()
	totalitems = getSiteIdPageCount(siteid)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/feeds/author/<authorid>/", methods=["GET"])
def get_browseByAuthorId(authorid):
	page = request.args.get('p') or '0'
	query = """SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE posts.author_id = %s ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"""
	try:
		cursor.execute(query, (authorid, int(page)))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	feeditems = cursor.fetchall()
	totalitems = getAuthorCount(authorid)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/feeds/<sitetype>/", methods=["GET"])
def get_browseByType(sitetype):
	if len(sitetype) < 1 and type(service) != str:
		return jsonify(data={"error": "Missing type."}), 400
	page = request.args.get('p') or '0'
	query = """SELECT post_id, title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE sitetype.name LIKE %s ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s ;"""
	try:
		cursor.execute(query, (sitetype,int(page)))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	feeditems = cursor.fetchall()
	totalitems = getSiteTypePageCount(sitetype)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/feeds/anime/<aniid>", methods=["GET"])
def get_browseByAnimeTitle(aniid):
	if len(aniid) < 1:
		return jsonify(data={"error": "Missing Anime Title ID."}), 400
	page = request.args.get('p') or '0'
	query = """SELECT posts.post_id as post_id, posts.title as title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id WHERE anime.anime_id = %s ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s ;"""
	try:
		cursor.execute(query, (aniid,int(page)))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	feeditems = cursor.fetchall()
	totalitems = getAnimeTitlePageCount(aniid)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/feeds/anime/<service>/<aniid>", methods=["GET"])
def get_browseByAnimeTitleAndService(service, aniid):
	if len(service) < 1 and type(service) != str:
		return jsonify(data={"error": "Missing service or invalid input."}), 400
	elif len(aniid) < 1:
		return jsonify(data={"error": "Missing Anime Title ID."}), 400
	page = request.args.get('p') or '0'
	lowercaseService = service.lower()
	servicewhereclause = ""
	if lowercaseService == "mal":
		servicewhereclause = "anime.mal_id = %s"
	elif lowercaseService == "anilist":
		servicewhereclause == "anime.anilist_id = %s"
	else:
		return (
			jsonify(data=
				{"error": "Invalid service specificed. Choices are mal and anilist."}
			),
			400,
		)
	query = (
		"""SELECT posts.post_id as post_id, posts.title as title, content, post_url, thumbnail_filename, published_date, author.name AS author, author.author_id AS author_id, mastodon, site.name AS websitename, site.site_id AS site_id, url, sitetype.name AS type FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id WHERE """
		+ servicewhereclause
		+ """ ORDER BY posts.published_date DESC LIMIT 20 OFFSET %s;"""
	)
	try:
		cursor.execute(query, (aniid,int(page)))
	except Exception as e:
		conn.rollback()
		return dumps({"error": "{e}"}, ensure_ascii=False).encode('utf8'), 500, {'Content-Type': 'application/json; charset=utf-8'}
	feeditems = cursor.fetchall()
	totalitems = getAnimeTitlePageCount(aniid)
	pagedict = {
		"next": (None)
		if int(page) + 20 > totalitems
		else (None)
		if int(page) == totalitems
		else int(page) + 20,
		"prev": (int(page) - 20) if int(page) - 20 >= 0 else None,
	}
	data = {"data" : addAnimeRelationInfo(feeditems)}
	data["page"] = pagedict
	return dumps(data, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/seasons/", methods=["GET"])
def get_season():
	month = datetime.now().month
	year = datetime.now().year
	if month <= 3:
		data = {
			"current_season" : "winter",
			"winter": {"year": year, "data": None},
			"spring": {"year": year - 1, "data": None},
			"summer": {"year": year - 1, "data": None},
			"fall": {"year": year - 1, "data": None},
		}
	elif month <= 6:
		data = {
			"current_season" : "spring",
			"winter": {"year": year, "data": None},
			"spring": {"year": year, "data": None},
			"summer": {"year": year - 1, "data": None},
			"fall": {"year": year - 1, "data": None},
		}
	elif month <= 0:
		data = {
			"current_season" : "summer",
			"winter": {"year": year, "data": None},
			"spring": {"year": year, "data": None},
			"summer": {"year": year, "data": None},
			"fall": {"year": year - 1, "data": None},
		}
	else:
		data = {
			"current_season" : "fall",
			"winter": {"year": year, "data": None},
			"spring": {"year": year, "data": None},
			"summer": {"year": year, "data": None},
			"fall": {"year": year, "data": None},
		}

	for seasonstr in ["winter", "spring", "summer", "fall"]:
		query = "SELECT anime.anime_id AS anime_id, title, season, year, count(*) AS count FROM post_relatedanime INNER JOIN anime ON post_relatedanime.anime_id  = anime.anime_id WHERE anime.season LIKE %s AND year = %s  GROUP BY anime.anime_id, anime.title, anime.season , anime.\"year\" ORDER BY count DESC"
		try:
			cursor.execute(query, (seasonstr.upper(), data[seasonstr]["year"]))
		except Exception as e:
			conn.rollback()
			return (
				dumps({"error": str(e)}, ensure_ascii=False).encode("utf8"),
				500,
				{"Content-Type": "application/json; charset=utf-8"},
			)
		items = cursor.fetchall()
		seasondict = data[seasonstr]
		seasondict["data"] = items
		data[seasonstr] = seasondict

	return (
		dumps(data, ensure_ascii=False).encode("utf8"),
		200,
		{"Content-Type": "application/json; charset=utf-8"},
	)


def getSearchPageCount(squery):
	squery = "%" + squery + "%"
	query = """SELECT count(*) AS count from posts WHERE title LIKE %s OR content LIKE %s;"""
	cursor.execute(query, (squery, squery))
	items = cursor.fetchall()
	return items[0]["count"]


def getSiteIdPageCount(siteid):
	query = """SELECT count(*) AS count from posts WHERE site_id = %s;"""
	cursor.execute(query, (siteid,))
	items = cursor.fetchall()
	return items[0]["count"]


def getSiteTypePageCount(type):
	query = """SELECT count(*) AS count from posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE sitetype.name = %s;"""
	cursor.execute(query, (type,))
	items = cursor.fetchall()
	return items[0]["count"]


def getAuthorCount(authorid):
	query = """SELECT count(*) AS count from posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id WHERE posts.author_id = %s;"""
	cursor.execute(query, (authorid,))
	items = cursor.fetchall()
	return items[0]["count"]


def getAnimeTitlePageCount(aniid):
	query = """SELECT count(*) AS count FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id WHERE anime.anime_id = %s;"""
	cursor.execute(query, (aniid,))
	items = cursor.fetchall()
	return items[0]["count"]


def getPageCount(exclude):
	if len(exclude) > 0:
		texcludearray = exclude.split(",")
		fexclude = []
		for typeid in texcludearray:
			if typeid.isnumeric():
				fexclude.append(typeid)
		query = "SELECT count(*) AS count FROM posts INNER JOIN site ON posts.site_id = site.site_id WHERE site.sitetype_id != ALL(%s);"
		excludestrarray = (",".join(fexclude)) if len(fexclude) > 1 else fexclude[0]
		excludestrarray = "{" + excludestrarray + "}"
		cursor.execute(query, (excludestrarray, ))
	else:
		query = "SELECT count(*) AS count FROM posts;"
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
		"SELECT count(*) AS count FROM posts INNER JOIN site ON posts.site_id = site.site_id INNER JOIN author ON posts.author_id = author.author_id INNER JOIN sitetype ON site.sitetype_id = sitetype.sitetype_id INNER JOIN post_relatedanime ON posts.post_id = post_relatedanime.post_id INNER JOIN anime ON anime.anime_id = post_relatedanime.anime_id WHERE "
		+ servicewhereclause
		+ ";"
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
	
@app.route('/static/imgcache/<path:path>')
def send_report(path):
	return send_from_directory('static/imgcache', path)


if __name__ == "__main__":
	app.run(debug=True)
