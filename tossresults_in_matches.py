import sqlite3
import requests
import time

headers = {
	"x-rapidapi-key": "63de28c479msh3320af327e85d52p172e0bjsn32e414ebf74e",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}


conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()

cursor.execute('''Select match_id from matches''')
match_ids=cursor.fetchall()
match_ids_f=[mid[0]for mid in match_ids]
match_ids_total=list(set(match_ids_f))


for mid in match_ids_total:
    try:
       url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{mid}/overs"
       response = requests.get(url, headers=headers)
       data=response.json()
       time.sleep(1)
       # tossresults
       tosswinner_id=data['matchheaders']['tossresults']['tosswinnerid']
       # tosswinner_name=data['matchheaders']['tossresults']['tosswinnername']
       toss_decision=data['matchheaders']['tossresults']['decision']
       # print('tosswinner_id:',tosswinner_id,"\n",'toss_decision:',toss_decision)
       winningTeamId=data['matchheaders']['winningteamid']
       status=data['matchheaders']['status']
       # print('winningTeamId:',winningTeamId,'\n','status:',status)
       cursor.execute('''
            UPDATE matches
            SET toss_winner_id = ?,
                toss_decision = ?,
                winner_id = ?,
                Status = ?
            WHERE match_id = ? AND (toss_winner_id IS NULL OR toss_decision IS NULL OR winner_id IS NULL OR status IS NULL);
        ''', (tosswinner_id, toss_decision, winningTeamId, status, mid))
       print('tosswin_id:',tosswinner_id,"\n",'toss_d:',toss_decision,'winningTeamId:',
             winningTeamId,"S:",status,"mid:",mid)
       conn.commit()
    except Exception as e:
        print(f"Error in match {id}: {e}") 

conn.close()       
       