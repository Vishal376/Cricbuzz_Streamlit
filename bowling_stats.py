import requests
import sqlite3
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()

cursor.execute('''Select match_id from matches''')
match_ids=cursor.fetchall()
flat_ids=[mid[0]for mid in match_ids]

headers = {
	"x-rapidapi-key": "9a04624b33msh5e522b7a063b778p1390c7jsn6161d21b8b89",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

for id in flat_ids:
   try:
     url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{id}/scard"
     response = requests.get(url, headers=headers)
     data=response.json()
     for item in data.get("scorecard", []):
       inning_no = item.get("inningsid")
    
    # batting order list
       bowler = item.get("bowler", [])
    
       for bow in bowler:  # enumerate start=1 se karega
         match_id = id
         player_id = bow.get("id")
         overs=bow.get('overs')
         maidens=bow.get('maidens')
         runs_conceded=bow.get('runs')
         wickets=bow.get('wickets')
         economy=bow.get('economy')
         print(match_id,player_id,overs,maidens,runs_conceded,wickets,economy,inning_no)

         cursor.execute('''INSERT OR IGNORE INTO bowling_stats (
            match_id, player_id, overs, maidens, runs_conceded, wickets, economy, innings_no
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
         (match_id, player_id, overs,maidens,runs_conceded,wickets,economy, inning_no))
         conn.commit()
        
   except Exception as e:
        print(f"Error in match {id}: {e}")  

conn.close()