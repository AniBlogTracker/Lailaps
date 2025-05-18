import appconfig

import json
import psycopg2
import ssl
import urllib.request
from datetime import datetime, timezone

print("Connecting to database...")
conn = psycopg2.connect(
    user=appconfig.db_user,
    password=appconfig.db_user_password,
    host=appconfig.db_host,
    port=appconfig.postgres_port,
    database=appconfig.db_name,
    options="-c search_path=dbo,public",
)

cursor = conn.cursor()


def downloadTitleIDs():
    print("Downloading Title Ids")
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(
        "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json"
    )
    if response.status == 200:
        return json.load(response)
    else:
        print("ERROR: Cannot retrieve meta information")
        return None


def loadMALIds():
    print("Loading titles")
    titledata = downloadTitleIDs()
    sql = "SELECT * FROM anime WHERE mal_id IS NULL;"
    cursor.execute(sql)
    results = cursor.fetchall()
    if len(titledata) > 0:
        for ntitle in titledata["data"]:
            match = False
            anilistid = 0
            malid = 0
            for source in ntitle["sources"]:
                if "anilist" in source:
                    anilistid = int(source.replace("https://anilist.co/anime/", ""))
                elif "myanimelist" in source:
                    malid = int(source.replace("https://myanimelist.net/anime/", ""))
            for title in results:
                if title["mal_id"] == malid:
                    match = True
                    break
            if match:
                continue
            animeseason = ntitle["animeSeason"]
            query = """ INSERT INTO anime(title, synonyms, mal_id, anilist_id, season, year) VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query,(ntitle["title"],",".join(map(str, ntitle["synonyms"])),malid,anilistid,animeseason["season"],animeseason["year"]))
        conn.commit()
        print("Loading anime title ids done")
    else:
        print("ERROR: Can't retrieve anime data")


def main():
    loadMALIds()

if __name__== "__main__":
    main()
