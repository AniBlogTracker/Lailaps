import appconfig
import psycopg2
from flask import Flask, request, jsonify, render_template

print("Connecting to database...")
connection = psycopg2.connect(user=appconfig.db_user,
  password=appconfig.db_user_password,
  host=appconfig.db_host,
  port=appconfig.postgres_port,
  database="postgres_db",
  options="-c search_path=dbo,public")
  
cursor = conn.cursor()

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")
	
@app.route('/feeds/', methods=['GET'])
def get_feed():
	page = request.args['p']
	if page == None;
		page = 0
	query = "SELECT * from anime LIMIT 10 OFFSET rows_to_skip ORDER BY published_date DSC;"
	cursor.execute(10*page)
	feeditems = cursor.fetchall()
	totalitems = getPageCount(query)
	return jsonify({ "items" : feeditems, "page" : {"next" : page+10 > totalitems ? totalitems-page : page == totalitems ? totalitems : page+10 , "prev" : page-10 > 0 ? page-10 : 0, }}, 200
	
@app.route('/search/', methods=['GET'])
def get_searchfeed():
	query = request.args['q']
	if len(query) < 1:
		return sonify({ "error" : "Missing query text."}, 200
	page = request.args['p']
	if page == None;
		page = 0
	query = "SELECT * from anime WHERE title LIKE %s OR content LIKE %s LIMIT 10 OFFSET rows_to_skip ORDER BY published_date DSC;"
	cursor.execute(query, query, 10*page)
	feeditems = cursor.fetchall()
	totalitems = getSearchPageCount(query)
	return jsonify({ "items" : feeditems, "page" : {"next" : page+10 > totalitems ? totalitems-page : page == totalitems ? totalitems : page+10 , "prev" : page-10 > 0 ? page-10 : 0, }}, 200
	
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
	
if __name__ == '__main__':
	app.run()