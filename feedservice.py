import os
import ssl
import time
import urllib.request
from datetime import datetime, timezone

import appconfig
import feedparser
import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup

print("Creating image cache directory...")
os.makedirs("imgcache", exist_ok=True)

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
cursor2 = conn.cursor()

def getSites():
	query = "SELECT * from site"
	cursor.execute(query)
	if feeds := cursor.fetchall():
		return feeds

	return []


def getPosts(feedurl, siteid):
	feed = feedparser.parse(feedurl)
	feed_items = []
	for entry in feed.entries:
		thumbnail = getThumbnail(entry.get("link", ""), siteid)
		item = {
			"title": entry.get("title", ""),
			"author": entry.get("author", ""),
			"link": entry.get("link", ""),
			"image": thumbnail,
			"description": entry.get("description", ""),
			"categories": [t.get("term") for t in entry.tags],
			"published": entry.get("published", ""),
			"siteid": siteid,
		}
		feed_items.append(item)
	return feed_items


def getPostId(url):
	query = """SELECT * from posts WHERE post_url = %s"""
	cursor.execute(query, (url,))
	posts = cursor.fetchall()
	if len(posts) > 0:
		post = posts[0]
		return post["post_id"]
	return -1


def getAuthorId(name, siteid):
	query = """SELECT * from author WHERE name = %s AND site_id = %s"""
	cursor.execute(query, (name, siteid))
	authors = cursor.fetchall()
	if len(authors) > 0:
		author = authors[0]
		return author["author_id"]
	return -1


def getAuthor(name, siteid):
	query = """SELECT * from author WHERE name = %s AND site_id = %s"""
	cursor.execute(query, (name, siteid))
	authors = cursor.fetchall()
	if len(authors) > 0:
		author = authors[0]
		return author
	return None


def updateAuthorMeta(authorid, posturl):
	query = (
		""" UPDATE author set mastodon = %s, lastupdated = %s WHERE author_id = %s """
	)
	mastodon = ""
	if meta := getMeta(posturl):
		mastodon = meta["mastodon"]
	cursor2.execute(query, (mastodon, datetime.now(), authorid))
	conn.commit()


def addAuthor(name, siteid, posturl):
	query = """ INSERT INTO author(site_id, name, mastodon, lastupdated) VALUES (%s, %s, %s, %s)"""
	mastodon = ""
	if meta := getMeta(posturl):
		mastodon = meta
	cursor2.execute(query, (siteid, name, mastodon, datetime.now()))
	conn.commit()
	return getAuthorId(name, siteid)


def getMeta(url):
	response = urllib.request.urlopen(url)
	if response.status == 200:
		soup = BeautifulSoup(response.read(), "html.parser")
		mastodon_tag = soup.find("meta", {"name": "fediverse:creator"})
		return mastodon_tag.get("content")
	else:
		print("ERROR: Cannot retrieve meta information for image")
		return None


def getThumbnail(url, siteid):
	response = urllib.request.urlopen(url)
	if response.status == 200:
		soup = BeautifulSoup(response.read(), "html.parser")
		image_tag = soup.find("meta", {"property": "og:image"})
		imgurl =  image_tag.get("content")
		print("Downloading thumbnail: " + imgurl)
		ssl._create_default_https_context = ssl._create_unverified_context
		urllib.request.urlretrieve(imgurl, "./imgcache/"+ str(siteid) + os.path.basename(image_tag.get("content")))
		return str(siteid) + os.path.basename(image_tag.get("content"))
	else:
		print("ERROR: Cannot retrieve meta information")
		return None


def downloadFavIcon(url, siteid):
	print("Downloading Fav Icon for: " + url)
	ssl._create_default_https_context = ssl._create_unverified_context
	urllib.request.urlretrieve(url + "/" + str(siteid) + ".ico", "./imgcache/"+ str(siteid) + ".ico")


def updateLastUpdatedSite(siteid):
	query = """ UPDATE site SET favicon_lastupdated = %s WHERE site_id = %s """
	datenow = datetime.now()
	cursor2.execute(query, (datenow, siteid))
	conn.commit()


def getanimeLid(title):
	query = """SELECT * from anime WHERE title LIKE %s OR synonyms LIKE %s"""
	cursor.execute(query, (title, title))
	animeids = cursor.fetchall()
	if len(animeids) > 0:
		return animeids[0]["anime_id"]
	return -1


def addPostAnimeRelation(postid, animeid):
	print("Adding Post Id relation " + str(postid) + "for Anime ID" + str(animeid))
	query = """ INSERT INTO post_relatedanime(post_id, anime_id) VALUES (%s, %s)"""
	cursor.execute(query, (postid, animeid))
	conn.commit()


def addPost(entry):
	print("Adding Post " + entry["title"])
	if getPostId(entry["link"]) > 0:
		print("Post " + entry["title"] + " exists, skipping...")
		return

	author = getAuthorId(entry["author"], entry["siteid"])
	if author > 0:
		adata = getAuthor(entry["author"], entry["siteid"])
		diff = time.mktime(adata["lastupdated"].timetuple()) - time.mktime(datetime.now().timetuple())
		if diff < -1209600:
			updateAuthorMeta(entry["author"], entry["link"])
	else:
		author = addAuthor(entry["author"], entry["siteid"], entry["link"])

	query = """ INSERT INTO posts(author_id, site_id, title, content, post_url, thumbnail_filename, published_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

	content = entry["description"]
	content = (content[:100] + "...") if len(content) > 100 else content
	link = entry["link"]

	cursor.execute(
		query,
		(author, entry["siteid"], entry["title"], content, link,entry["image"], entry["published"],)
	)
	conn.commit()

	postid = getPostId(link)
	possibletitles = entry["categories"]
	animeids = []

	for possibletitle in possibletitles:
		aniid = getanimeLid(possibletitle)
		if aniid > 0:
			found = False
			for eanimeid in animeids:
				if aniid == eanimeid:
					found = True
					break
			if found:
				continue
		animeids.append(aniid)

	for aid in animeids:
		if aid > 0:
			addPostAnimeRelation(postid, aid)

	print("Post " + entry["title"] + " added")


def main():
	while True:
		sites = getSites()
		print(sites)
		for site in sites:
			print("Checking " + site["name"])
			posts = getPosts(site["feed_url"], site["site_id"])
			for post in posts:
				addPost(post)
			
			downloadfavicon = False
			if site["favicon_lastupdated"]:
				diff = time.mktime(site["favicon_lastupdated"].timetuple()) - time.mktime(datetime.now().timetuple())
				if diff < -1209600:
					downloadfavicon = True
			else:
				downloadfavicon = True
			
			if downloadfavicon:
				print("Downloading new favicon ")	
				updateLastUpdatedSite(updateLastUpdatedSite)

		print("Done adding titles, sleeping 5 minutes ")
		time.sleep(300)
		
if __name__== "__main__":
	main()