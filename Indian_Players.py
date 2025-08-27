import requests
import pandas as pd
import sqlite3

url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/2/players"

headers = {
	"x-rapidapi-key": "5312fc3650msh1646940cf7fb715p1200d3jsnb7c320c2f03e",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

data=response.json()

players = []
current_role = None

for item in data["player"]:
    if "id" not in item:  # category
        current_role = item["name"]
    else:  # player details
        players.append({
            "p_id":item.get("id"),
            "name": item.get("name"),
            "battingStyle": item.get("battingStyle", None),
            "bowlingStyle": item.get("bowlingStyle", None),
            "role": current_role
        })

# Convert to DataFrame
df = pd.DataFrame(players)
print(df)
print(item.get("id"))

# Store in SQLite
conn = sqlite3.connect("cricbuzz.db")
cursor = conn.cursor()
# Insert data
df.to_sql('IndianPlayers', conn, if_exists='replace', index=False)

conn.commit()
conn.close()
print(" Data stored in SQLite successfully!")