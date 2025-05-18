import yaml
import psycopg2

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

def downloadTitleIDs():
    print('Downloading Title Ids')
    ssl._create_default_https_context = ssl._create_unverified_context
	response = requests.get('https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json')
    	if response.status_code == 200:
		return titledata = json.load(response)
	else:
		print("ERROR: Cannot retrieve meta information")
		return None

def loadMALIds():
    print('Loading titles')
    titledata = downloadTitleIDs()
    sql = "SELECT * FROM anime WHERE mal_id IS NULL;"
    cursor.execute(sql)
    results = cursor.fetchall()
    if results:
        if len(results) > 0:
            for ntitle in titledata["data"]:
                match = false
                anilistid = 0
                malid = 0
                for source in ntitle["sources"]
                    if "anilist" in source:
                        anilistid = int(string.replace("https://anilist.co/anime/"))
                    elif if "anilist" in source:
                        malid = int(string.replace("https://myanimelist.net/anime/"))
                for title in anime:
                    if title["mal_id"] = malid:
                        match = true
                        break
                if match:
                    continue
                print("Adding Post Id relation " + postid + "for Anime ID" + animeid)
                animeseason = ntitle["animeSeason"]
                query = """ INSERT INTO anime(title, synonyms, mal_id, anilist_id, season, year) VALUES (%s, %s, %i, %i, %s, %i)"""
                cursor.execute(query, (ntitle["title"] , ','.join(map(str, ntitle["synonyms"])), malid, anilistid, animeseason["season"], animeseason["year"]))
            
            conn.commit()
            print('Loading anime title ids done')
    else:
        print("ERROR: Can't retrieve anime data")

def main():
    loadMALIds()