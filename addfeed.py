import sys
import getopt
import os

import appconfig
import feedparser
import psycopg2
from datetime import datetime, timezone

conn = psycopg2.connect(
	user=appconfig.db_user,
	password=appconfig.db_user_password,
	host=appconfig.db_host,
	port=appconfig.postgres_port,
	database=appconfig.db_name,
	options="-c search_path=dbo,public",
)

cursor = conn.cursor()

os.makedirs("imgcache", exist_ok=True)

def getFeedMeta(feedurl):
	feed = feedparser.parse(feedurl)
	if feed:
		site_info = {
			"title": feed.feed.get("title", ""),
			"link": feed.feed.get("link", ""),
			"description": feed.feed.get("description", "")
		}
		return site_info
	else:
		print("ERROR: Failed to retrieve feed information ")
		return None
		
def checkFeed(feedurl):
	query = """SELECT * from site WHERE feed_url = %s"""
	cursor.execute(query, (feedurl,))
	feeds = cursor.fetchall()
	if len(feeds) > 0:
		return True
	
	return False
	
def getSiteId(feedurl):
	query = """SELECT * from site WHERE feed_url = %s"""
	cursor.execute(query, (feedurl,))
	feeds = cursor.fetchall()
	if len(feeds) > 0:
		return feed[0]["site_id"]
	
	return -1

try:
	opts, args = getopt.getopt(sys.argv[1:],"hu:",["feedurl="])
except getopt.GetoptError:
	print ('addfeed.py -u <feedurl>')
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print ('addfeed.py -u <feedurl>')
		sys.exit()
	elif opt in ("-u", "--url"):
		feedurl = arg
		if checkFeed(feedurl) == False:
			siteinfo = getFeedMeta(feedurl)
			print("Adding feed " + feedurl)
			query = """ INSERT INTO site(name, description, feed_url, url, favicon_lastupdated) VALUES (%s, %s, %s, %s, %s)"""
			cursor.execute(query, (siteinfo["title"], siteinfo["description"], feedurl, siteinfo["link"], datetime.now(),) )
			conn.commit()
			print("Added feed " + feedurl)
			siteid = getSiteId(feedurl)
			if siteid > 0:
				print("Downloading Fav Icon for: " + url)
				ssl._create_default_https_context = ssl._create_unverified_context
				urllib.request.urlretrieve(url + "/" + str(siteid) + ".ico", "./imgcache/"+ str(siteid) + ".ico")
		else:
			print("Feed " + feedurl + " already exists")
        