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
	query = (
		"SELECT * from anime LIMIT 10 OFFSET rows_to_skip ORDER BY published_date DSC;"
	)
	cursor.execute(10 * page)
	feeditems = cursor.fetchall()
	totalitems = getPageCount(query)
	pagedict = {
		"next": (totalitems - page)
		if page + 10 > totalitems
		else (totalitems)
		if page == totalitems
		else page + 10,
		"prev": (page - 10) if page - 10 > 0 else 0,
	}
	return jsonify({"items": feeditems, "page": pagedict}), 200


@app.route("/search/", methods=["GET"])
def get_searchfeed():
	query = request.args["q"]
	if len(query) < 1:
		return jsonify({"error": "Missing query text."}), 400
	page = request.args["p"]
	if page == None:
		page = 0
	query = "SELECT * from anime WHERE title LIKE %s OR content LIKE %s LIMIT 10 OFFSET rows_to_skip ORDER BY published_date DSC;"
	cursor.execute(query, query, 10 * page)
	feeditems = cursor.fetchall()
	totalitems = getSearchPageCount(query)
	pagedict = {
		"next": (totalitems - page)
		if page + 10 > totalitems
		else (totalitems)
		if page == totalitems
		else page + 10,
		"prev": (page - 10) if page - 10 > 0 else 0,
	}
	return jsonify({"items": feeditems, "page": pagedict}), 200


def getSearchPageCount(query):
	query = "SELECT count(*) AS 'count' from anime WHERE title LIKE %s OR content LIKE %s ORDER BY published_date DSC;"
	cursor.execute(query, query)
	items = cursor.fetchall()
	return items[0]["count"]


def getPageCount(query):
	query = "SELECT count(*) AS 'count' from anime WHERE title LIKE %s OR content LIKE %s ORDER BY published_date DSC;"
	cursor.execute(query, query)
	items = cursor.fetchall()
	return items[0]["count"]


if __name__ == "__main__":
	app.run()
