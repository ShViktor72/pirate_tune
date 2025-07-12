from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/api/address")
def get_address():
    return jsonify({"address": "https://piratetunes.onrender.com"})  # можно убрать эту часть или заглушку оставить

def search_tracks(query):
    url = f"https://muzofond.fm/search/{query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    query_words = query.lower().split("+")

    tracks = []
    play_buttons = soup.select("li.play")

    for i, play_btn in enumerate(play_buttons):
        parent_li = play_btn.find_parent("li")

        artist_element = parent_li.select_one("div.desc h3 span.artist")
        track_element = parent_li.select_one("div.desc h3 span.track")
        mp3_url = play_btn.get("data-url")

        if artist_element and track_element and mp3_url:
            artist = artist_element.text.strip()
            title = track_element.text.strip()
            match_count = sum(1 for word in query_words if word in (artist + " " + title).lower())

            tracks.append({
                "id": i + 1,
                "artist": artist,
                "title": title,
                "url": mp3_url,
                "matches": match_count
            })

    tracks.sort(key=lambda x: (-x['matches'], x['id']))

    for track in tracks:
        track.pop('matches')

    return tracks

@app.route("/api/search")
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing 'q' parameter"}), 400

    tracks = search_tracks(query)
    return jsonify(tracks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
