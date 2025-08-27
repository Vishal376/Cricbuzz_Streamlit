import requests
import pandas as pd
import sqlite3
import time
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()
headers = {
    "x-rapidapi-key": "84d42b9ce6msh30b169e489b0d8fp1235d1jsneb9a9f83ef44",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# series_ids = [7572, 8788, 8802, 9107]
cursor.execute('''SELECT series_id FROM series_id_name''')
series_ids = cursor.fetchall()
flat_ids = [sid[0] for sid in series_ids]

for sid in flat_ids:
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{sid}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Series {sid} → API error {response.status_code}")
        time.sleep(2)
        continue

    data = response.json()

    matches = []
    for block in data.get("matchDetails", []):
        md_map = block.get("matchDetailsMap", {})
        if not isinstance(md_map, dict):
            time.sleep(2)
            continue

        for match in md_map.get("match", []):
            info = match.get("matchInfo", {})
            venue = info.get("venueInfo", {})

            series_id = info.get("seriesId")
            series_name = info.get("seriesName")
            host_country = venue.get("country", "")
            match_format = info.get("matchFormat")
            start_date = pd.to_datetime(int(info.get("startDate")), unit="ms").date() if info.get("startDate") else None

            matches.append((series_id, series_name, host_country, match_format, start_date))

    # ab ek hi row per series insert karna hai (with total_matches)
    if matches:
        total_matches = len(matches)
        first = matches[0]  # series info same rahega
        cursor.execute('''INSERT INTO seriesmatches 
                          (series_id, series_name, host_country, match_type, start_date, total_matches)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (first[0], first[1], first[2], first[3], first[4], total_matches))
        conn.commit()
        print(f"Inserted series {sid} with {total_matches} matches")
time.sleep(2)