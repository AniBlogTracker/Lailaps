import os
import ssl
import urllib.request
from datetime import datetime, timezone

import appconfig
import feedparser
import psycopg2
from bs4 import BeautifulSoup

print("Creating image cache directory...")
os.makedirs("imgcache", exist_ok=True)

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


def getSites():
	query = "SELECT * from site"
	cursor.execute(query)
	if feeds := cursor.fetchall():
		return feeds

	return []


def getPosts(feedurl, siteid):
	feed = feedparser.parse(rss_url)
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


def getPostId(url):
	query = "SELECT * from posts WHERE url = %s"
	cursor.execute(query, (url))
	posts = cursor.fetchall()
	if len(posts) > 0:
		post = posts[0]
		return post["post_id"]
	return -1


def getAuthorId(name, siteid):
	query = "SELECT * from author WHERE name = %s AND site_id = %i"
	cursor.execute(query, (name, siteid))
	authors = cursor.fetchall()
	if len(authors) > 0:
		author = authors[0]
		return author["author_id"]
	return -1


def getAuthor(name, siteid):
	query = "SELECT * from author WHERE name = %s AND site_id = %i"
	cursor.execute(query, (name, siteid))
	authors = cursor.fetchall()
	if len(authors) > 0:
		author = authors[0]
		return author
	return None


def updateAuthorMeta(authorid, posturl):
	query = (
		""" UPDATE author set mastodon = %s, lastupdated = %s WHERE author_id = %i """
	)
	mastodon = ""
	if meta := getMeta(posturl):
		mastodon = meta["mastodon"]
	cursor.execute(query, mastodon, datetime.now(timezone.utc), authorid)
	conn.commit()


def addAuthor(name, siteid, posturl):
	query = """ INSERT INTO author(site_id, name, mastodon, lastupdated) VALUES (%s, %i, %s, %s)"""
	mastodon = ""
	if meta := getMeta(posturl):
		mastodon = meta["mastodon"]
	cursor.execute(query, siteid, name, mastodon, datetime.now(timezone.utc))
	conn.commit()
	return getAuthorId(name, siteid)


def getMeta(url):
	response = requests.get(url)
	if response.status_code == 200:
		soup = BeautifulSoup(response.content, "html.parser")
		mastodon_tag = soup.find("meta", {"name": "fediverse:creator"})
		return image_tag.get("content")
	else:
		print("ERROR: Cannot retrieve meta information for image")
		return None


def getThumbnail(url, siteid):
	response = requests.get(url)
	if response.status_code == 200:
		soup = BeautifulSoup(response.content, "html.parser")
		image_tag = soup.find("meta", {"property": "og:image"})
		imgurl =  image_tag.get("content")
		print("Downloading thumbnail: " + imgurl)
		ssl._create_default_https_context = ssl._create_unverified_context
		urllib.request.urlretrieve(imgurl, "./imgcache/"+ siteid + os.path.basename(image_tag.get("content")))
		return siteid + os.path.basename(image_tag.get("content"))
	else:
		print("ERROR: Cannot retrieve meta information")
		return None


def downloadFavIcon(url, siteid):
	print("Downloading Fav Icon for: " + url)
	ssl._create_default_https_context = ssl._create_unverified_context
	urllib.request.urlretrieve(url + "/" + siteid + ".ico", "./imgcache/"+ siteid + ".ico")


def updateLastUpdatedSite(siteid):
	query = """ UPDATE site set favicon_lastupdated = %s WHERE site_id = %i """
	cursor.execute(query, (datetime.now(timezone.utc), siteid))
	conn.commit()


def getanimeLid(title):
	query = "SELECT * from anime WHERE title = %s OR english_title = %s"
	cursor.execute(query, title, title)
	animeids = cursor.fetchall()
	if len(animeids) > 0:
		return animeids[0]["anime_id"]
	return -1


def addPostAnimeRelation(postid, animeid):
	print("Adding Post Id relation " + postid + "for Anime ID" + animeid)
	query = """ INSERT INTO post_relatedanime(post_id, anime_id) VALUES (%i, %i)"""
	cursor.execute(query, (postid, animeid))
	conn.commit()


def addAuthor(siteid, name):
	print("Adding Author " + name + " to " + siteid)
	query = """ INSERT INTO author(site_id, name, mastodon, lastupdated) VALUES (%s, %i, %s, %s)"""
	cursor.execute(query, siteid, name, mastodon, datetime.now(timezone.utc))
	conn.commit()
	return getAuthorId(name, siteid)


def addPost(entry):
	print("Adding Post " + entry["title"])
	if getPostId(entry["link"]) > 0:
		print("Post " + entry["title"]) + " exists, skipping..."
		return

	author = getAuthorId(entry["author"], entry["siteid"])
	authorid = 0
	if author:
		authorid = author["author_id"]
		if author["lastupdated"].timestamp() - datetime.timestamp() < -1209600:
			updateAuthorMeta(entry["author"], entry["siteid"])
	else:
		authorid = addAuthor(entry["author"], entry["siteid"], entry["posturl"])

	query = """ INSERT INTO posts(author_id, site_id, title, content, post_url, thumbnail_url, published_date) VALUES ()"""

	content = entry["description"]
	content = (content[:100] + "...") if len(content) > 100 else content
	link = entry["link"]

	cursor.execute(
		authorid, entry["siteid"], entry["title"], content, link, entry["published"]
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
		elif found:
			continue

		animeids.append(aniid)

	for aid in animeids:
		addPostAnimeRelation(postid, aid)

	print("Post " + entry["title"] + " added")


def main():
	while True:
		sites = getSites()
		for site in sites:
			print("Checking " + site["name"])
			posts = getPosts(site["feed_url"], feed["site_id"])
			for post in posts:
				addPost(post)

			if (
				site["favicon_lastupdated"].timestamp() - datetime.timestamp()
				< -1209600
			):
				print("Downloading new favicon ")
				updateLastUpdatedSite(updateLastUpdatedSite)

		print("Done adding titles, sleeping 5 minutes ")
		sleep(300)