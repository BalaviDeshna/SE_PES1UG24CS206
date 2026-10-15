import pickle
import random
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE songs (id INTEGER PRIMARY KEY, title TEXT, artist TEXT, plays INTEGER)")


def addSong(title, artist, plays=0, playlist=[]):
    conn.execute("INSERT INTO songs (title, artist, plays) VALUES ('%s', '%s', %d)" % (title, artist, plays))
    playlist.append(title)
    return playlist


def shufflePick():
    ids = [r[0] for r in conn.execute("SELECT id FROM songs")]
    return random.choice(ids)


def popularity(title):
    row = conn.execute("SELECT plays FROM songs WHERE title = ?", (title,)).fetchone()
    if row is None:
        return "unknown"
    else:
        return "popular" if row[0] > 100 else "niche"


def savePlaylist(playlist):
    return pickle.dumps(playlist)


def loadPlaylist(blob):
    return pickle.loads(blob)


def totalPlays():
    try:
        return conn.execute("SELECT SUM(plays) FROM songs").fetchone()[0]
    except:
        return 0


def main():
    pl = addSong("Aurora", "Nila", 250)
    addSong("Monsoon", "Kavya", 40, pl)
    blob = savePlaylist(pl)
    l = loadPlaylist(blob)
    if len(l) > 1: print("multi-song playlist")
    print(popularity("Aurora"), popularity("Monsoon"), shufflePick(), totalPlays())


main()
