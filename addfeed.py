import sys

import appconfig
import feedparser
import psycopg2

def getFeedMeta(feedurl):
	feed = feedparser.parse(rss_url)
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

def main(argv):
	opts, args = getopt.getopt(argv,"hu:",["feedurl="])
	except getopt.GetoptError:
		print ('addfeed.py -u <feedurl>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('addfeed.py -u <feedurl>')
			sys.exit()
		elif opt in ("-u", "--url"):
			feedurl = arg
			siteinfo = getFeedMeta(feedurl)
			print("Adding feed" + feedurl)
			query = """ INSERT INTO site(name, description, feed_url, url) VALUES (%s, %s, %s, %s)"""
			cursor.execute(query, (siteinfo["title"], siteinfo["description"], feedurl, siteinfo["url"]) )
			conn.commit()
			print("Added feed" + feedurl)