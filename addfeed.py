import sys
import getopt
import os
import ssl
import urllib.request
from urllib.request import build_opener, install_opener, _opener

import appconfig
import feedparser
import psycopg2
from datetime import datetime, timezone

build_opener, install_opener, _opener

if _opener is None:
	opener = build_opener()
	install_opener(opener)
else:
	opener = _opener

opener.addheaders = [('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15'
)]

conn = psycopg2.connect(
	user=appconfig.db_user,
	password=appconfig.db_user_password,
	host=appconfig.db_host,
	port=appconfig.postgres_port,
	database=appconfig.db_name,
	options="-c search_path=dbo,public",
)

cursor = conn.cursor()

os.makedirs(",/static/imgcache", exist_ok=True)

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
		return feeds[0]["site_id"]
	
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
			query = """ INSERT INTO site(name, description, feed_url, url, favicon_lastupdated, sitetype_id) VALUES (%s, %s, %s, %s, %s, 1)"""
			cursor.execute(query, (siteinfo["title"], siteinfo["description"], feedurl, siteinfo["link"], datetime.now(),) )
			conn.commit()
			print("Added feed " + feedurl)
			siteid = getSiteId(feedurl)
			if siteid > 0:
				print("Downloading Fav Icon for: " + url)
				ssl._create_default_https_context = ssl._create_unverified_context
				opener.retrieve(url + "/favicon.ico")
				img = opener.open(imgurl)
				with open("./static/imgcache/"+ str(siteid) + ".ico", 'b+w') as f:
					f.write(img.read())
		else:
			print("Feed " + feedurl + " already exists")
        