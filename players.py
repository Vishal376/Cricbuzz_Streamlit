import sqlite3
import requests
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()

cursor.execute('''Select player_id from bowling_stats''')
series_ids = cursor.fetchall()
flat_ids = [sid[0] for sid in series_ids]
ids=list(set(flat_ids))
# print(ids)

cursor.execute('''Select player_id from batting_stats''')
series_ids2 = cursor.fetchall()
flat_ids2= [sid[0] for sid in series_ids2]
ids2=list(set(flat_ids2))
final_ids=ids+ids2
headers = {
	"x-rapidapi-key": "812748c71cmsh199f92268d98729p1fc9ddjsn3e28b8f054bb",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

for id in final_ids:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{id}"
    
        response = requests.get(url, headers=headers)

        data=response.json()

        player_id=data.get('id',"")
        full_name=data.get('name',"")
        country=data.get('intlTeam',"")
        playing_role=data.get('role',"")
        batting_style=data.get('bat')  if data.get('bat') else None
        bowling_style=data.get('bowl') if data.get('bowl') else None
        cursor.execute('''Insert OR IGNORE INTO players(player_id,full_name,country,playing_role,batting_style,bowling_style)
                       VALUES(?,?,?,?,?,?)''',(player_id,full_name,country,playing_role,batting_style,bowling_style))
        print(player_id,full_name,country,playing_role)
        conn.commit()



conn.close()