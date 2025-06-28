import os
import ssl
import time
import urllib.request
import re
from urllib.request import build_opener, install_opener, _opener
from datetime import datetime, timezone

import appconfig
import feedparser
import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

build_opener, install_opener, _opener

if _opener is None:
	opener = build_opener()
	install_opener(opener)
else:
	opener = _opener

useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15'

opener.addheaders = [('User-Agent', useragent)]
feedparser.USER_AGENT = useragent

print("Creating image cache directory...")
os.makedirs(",/static/imgcache", exist_ok=True)

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
		if getPostId(entry.get("link", "")) > 0:
			print("Post " + entry["title"] + " exists, skipping...")
			continue
		
		tmpcontent = ""
		if hasattr(entry, "content"):
			tmpcontent = entry.content[0]["value"]
		else:
			tmpcontent = entry.get("description", "")
		thumbnail = getThumbnail(entry.get("link", ""), tmpcontent, siteid)
		tags = []
		if hasattr(entry, "tags"):
			tags = [t.get("term") for t in entry.tags]
		item = {
			"title": entry.get("title", ""),
			"author": entry.get("author", ""),
			"link": entry.get("link", ""),
			"image": thumbnail,
			"description": entry.get("description", ""),
			"categories": tags ,
			"published": entry.get("published", ""),
			"siteid": siteid,
		}
		print("Queuing post " + entry["title"] + " to be added...")
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
		mastodon = meta
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
	try:
		response = opener.open(url)
		if response.status == 200:
			soup = BeautifulSoup(response.read(), "html.parser")
			mastodon_tag = soup.find("meta", {"name": "fediverse:creator"})
			if mastodon_tag:
				return mastodon_tag.get("content")
			return ""
		else:
			print("ERROR: Cannot retrieve meta information for image")
			return None
	except:
		print("An exception occurred trying to retrieve metadata.")
		return None


def getThumbnail(url, content, siteid):
	imgurl_search = re.search('(http|https)?://[^\s]+(jpg|jxt|png|webm|webp|avif|gif|bmp|tif)', content)
	imgurl = ""
	if imgurl_search is None:
		try:
			response = opener.open(url)
			if response.status == 200:
				soup = BeautifulSoup(response.read(), "html.parser")
				image_tag = soup.find("meta", {"property": "og:image"})
				imgurl =  image_tag.get("content")
				imgurl = re.search('(http|https)?://[^\s]+(jpg|jxt|png|webm|webp|avif|gif|bmp|tif)', imgurl).group()
				time.sleep(10)
			else:
				print("ERROR: Cannot retrieve meta information")
				return None
		except Exception:
			print("ERROR: Cannot retrieve image")
			return ""
	else:
		imgurl = imgurl_search.group()
		print()
		
	return getThumbnailImage(imgurl, siteid)
	
def getThumbnailImage(imgurl, siteid):
	filename =  os.path.basename(imgurl)
	if os.path.isfile("./static/imgcache/"+ str(siteid) + filename):
		print("Thumbnail exists, skipping...")
	else:
		print("Downloading thumbnail: " + imgurl)
		ssl._create_default_https_context = ssl._create_unverified_context
		try:
			img = opener.open(imgurl)
			with open("./static/imgcache/"+ str(siteid) + filename, 'b+w') as f:
				f.write(img.read())
		except:
			print("An exception occurred trying to download thumbnail")
			return ""
	return str(siteid) + filename

def downloadFavIcon(url, siteid):
	print("Downloading Fav Icon for: " + url)
	ssl._create_default_https_context = ssl._create_unverified_context
	opener.retrieve(url + "/favicon.ico")
	img = opener.open(imgurl)
	with open("./static/imgcache/"+ str(siteid) + ".ico", 'b+w') as f:
		f.write(img.read())


def updateLastUpdatedSite(siteid):
	query = """ UPDATE site SET favicon_lastupdated = %s WHERE site_id = %s """
	cursor2.execute(query, (datetime.now(), siteid))
	conn.commit()


def getanimeLid(title):
	query = """SELECT * from anime"""
	cursor.execute(query,)
	animeids = cursor.fetchall()
	for animeid in animeids:
		synonyms = animeid["synonyms"].split(',')
		animetitle = animeid["title"]
		res = SequenceMatcher(None, title.lower(), animetitle.lower()).ratio()
		if res >= .75:
			return animeid["anime_id"]
		else:
			for synonym in synonyms:
				res = SequenceMatcher(None, title.lower(), synonym.lower()).ratio()
				if res >= .75:
					return animeid["anime_id"]
	return -1
	
def addPostAnimeRelation(postid, animeid):
	print("Adding Post Id relation " + str(postid) + "for Anime ID" + str(animeid))
	query = """ INSERT INTO post_relatedanime(post_id, anime_id) VALUES (%s, %s)"""
	cursor.execute(query, (postid, animeid))
	conn.commit()


def addPost(entry):
	print("Adding Post " + entry["title"])
	if getPostId(entry["link"]) > 0:
		return

	author = getAuthorId(entry["author"], entry["siteid"])
	if author > 0:
		adata = getAuthor(entry["author"], entry["siteid"])
		diff = time.mktime(adata["lastupdated"].timetuple()) - time.mktime(datetime.now().timetuple())
		if diff < -1209600:
			updateAuthorMeta(author, entry["link"])
	else:
		author = addAuthor(entry["author"], entry["siteid"], entry["link"])

	query = """ INSERT INTO posts(author_id, site_id, title, content, post_url, thumbnail_filename, published_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

	content = entry["description"]
	soup = BeautifulSoup(content, "html.parser")
	content = soup.get_text()
	content = (content[:300] + "...") if len(content) > 300 else content
	link = entry["link"]
	
	tsoup = BeautifulSoup(entry["title"], "html.parser")
	title = tsoup.get_text()
	title = (title[:300] + "...") if len(title) > 300 else title

	cursor.execute(
		query,
		(author, entry["siteid"], title, content, link,entry["image"], entry["published"],)
	)
	conn.commit()

	postid = getPostId(link)
	possibletitles = entry["categories"]
	animeids = []
	
	ignorewords = ["anime", "animation", "review", "comedy", "adventure", "mystery", "commentary", "opinion", "fanart", "fan art", "art", "magical girl", "mahou shoujo", "music", "idol", "drama" , "food", "manga", "Episodic Anime posts", "reviews", "manga reviews", "action", "uncategorized", "articles", "analysis", "essay", "opinion", "sci-fi", "awards", "commentary", "news", "anime news", "movies", "manga", "lifestyle", "europe", "japan", "north america", "moe", "RPG", "video games", "roundup"]
	increment = 0;
	for possibletitle in possibletitles:
		hasIgnoreWord = False
		for iword in ignorewords:
			if possibletitle.lower() in iword:
				hasIgnoreWord = True
				break
		
		if hasIgnoreWord:
			continue
			
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
		increment += 1
		if increment > 4:
			break;

	for aid in animeids:
		if aid > 0:
			addPostAnimeRelation(postid, aid)

	print("Post " + entry["title"] + " added")

def main():
	while True:
		print("Checking feeds for new posts...")
		sites = getSites()
		for site in sites:
			if len(site["feed_url"]) == 0:
				continue
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
				updateLastUpdatedSite(site["site_id"])

		print("Done adding titles, sleeping 15 minutes ")
		time.sleep(900)
		
if __name__== "__main__":
	main()