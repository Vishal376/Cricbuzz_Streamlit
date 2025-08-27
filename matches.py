import requests
import pandas as pd
import time
import sqlite3

conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()
headers = {
    "x-rapidapi-key": "84d42b9ce6msh30b169e489b0d8fp1235d1jsneb9a9f83ef44",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

cursor.execute('''SELECT series_id FROM series_id_name''')
series_ids = cursor.fetchall()
flat_ids = [sid[0] for sid in series_ids]

def save_matches(data):
    for block in data.get("matchDetails", []):
        md_map = block.get("matchDetailsMap", {})
        for match in md_map.get("match", []):
            info = match.get("matchInfo", {})
            venue = info.get("venueInfo", {})

            match_id = info.get("matchId")
            series_id = info.get("seriesId")
            description = info.get("matchDesc")
            team1_id = info.get("team1", {}).get("teamId")
            team2_id = info.get("team2", {}).get("teamId")
            venue_id = venue.get("id")
            match_date = pd.to_datetime(int(info.get("startDate")), unit="ms").date() if info.get("startDate") else None

            # toss, winner, victory margin etc. abhi ke liye NULL
            toss_winner_id = None
            toss_decision = None
            winner_id = None
            victory_margin = None
            victory_type = None
            # print(match_id,team1_id,team2_id,venue_id)

            cursor.execute("""
                INSERT INTO matches 
                (match_id, series_id, description, team1_id, team2_id, venue_id, match_date,
                 toss_winner_id, toss_decision, winner_id, victory_margin, victory_type)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                match_id, series_id, description, team1_id, team2_id, venue_id, match_date,
                toss_winner_id, toss_decision, winner_id, victory_margin, victory_type
            ))

for sid in flat_ids:
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{sid}"

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"=== Series {sid} inserted ===")
            save_matches(data)
            # conn.commit()
            break
        elif response.status_code == 429:
            print(f"Series {sid} → 429 Too Many Requests, retrying...")
            time.sleep(5)
        else:
            print(f"Series {sid} → API error {response.status_code}")
            break

conn.commit()
conn.close()
