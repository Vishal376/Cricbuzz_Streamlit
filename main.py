import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import concurrent.futures
# Database connection
conn = sqlite3.connect("cricbuzz.db")
cursor = conn.cursor()

# All questions + queries dict
questions = {
    "Find all players who represent India":
    """SELECT *
       FROM IndianPlayers """,

    "Show all cricket matches played in last 30 days":
    """SELECT m.description, t1.team_name AS team1, t2.team_name AS team2, 
              v.name AS venue, v.city, m.match_date
       FROM matches m
       JOIN teams t1 ON m.team1_id = t1.team_id
       JOIN teams t2 ON m.team2_id = t2.team_id
       JOIN venues v ON m.venue_id = v.venue_id
       WHERE m.match_date >= DATE('now','-30 day')
       ORDER BY m.match_date DESC;""",

      "List the top 10 highest run scorers in ODI cricket.":'''SELECT p.full_name,
       SUM(b.runs) AS total_runs,
       ROUND(AVG(CAST(b.runs AS FLOAT)), 2) AS batting_average,
       SUM(CASE WHEN b.runs >= 100 THEN 1 ELSE 0 END) AS centuries
FROM batting_stats b
JOIN players p ON b.player_id = p.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE m.description LIKE '%ODI%'
GROUP BY p.player_id
ORDER BY total_runs DESC
LIMIT 10;
''',
      
      "Display all cricket venues that have a seating capacity of more than 50,000 spectators.":'''SELECT name, city, country, capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;
''',
    "How many matches each team has won. Show team name and total number of wins.":'''
SELECT t.team_name,
       COUNT(m.winner_id) AS total_wins
FROM matches m
JOIN teams t ON m.winner_id = t.team_id
GROUP BY t.team_name
ORDER BY total_wins DESC;''',

"How many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper)":'''
SELECT playing_role,
       COUNT(*) AS total_players
FROM players
GROUP BY playing_role;''',

"The Highest individual batting score achieved in each cricket format (Test, ODI, T20I)":'''SELECT m.description AS format,
       MAX(b.runs) AS highest_score
FROM batting_stats b
JOIN matches m ON b.match_id = m.match_id
GROUP BY m.description;
''',

"All Cricket series that started in the year 2024":'''
SELECT series_name,
       host_country,
       match_type,
       start_date,
       total_matches
FROM seriesmatches
WHERE strftime('%Y', start_date) = '2024';''',

"All-Rounder Players who have scored more than 1000 runs AND taken more than 50 wickets":'''SELECT p.full_name,
       SUM(b.runs) AS total_runs,
       SUM(bw.wickets) AS total_wickets
FROM players p
LEFT JOIN batting_stats b ON p.player_id = b.player_id
LEFT JOIN bowling_stats bw ON p.player_id = bw.player_id
WHERE p.playing_role LIKE '%Allrounder%'
GROUP BY p.player_id, p.full_name
HAVING total_runs > 1000 AND total_wickets > 50;''',

"Details of the last 20 completed matches":'''SELECT m.description,
       t1.team_name AS team1,
       t2.team_name AS team2,
       tw.team_name AS winner,
       m.Status,
       v.name AS venue_name
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
LEFT JOIN teams tw ON m.winner_id = tw.team_id
JOIN venues v ON m.venue_id = v.venue_id
where m.Status IS NOT NULL
ORDER BY m.match_date DESC
LIMIT 20;
''',

"Player's performance across different cricket formats":'''
SELECT p.full_name,
       SUM(CASE WHEN m.description LIKE '%Test%' THEN b.runs ELSE 0 END) AS test_runs,
       SUM(CASE WHEN m.description LIKE '%ODI%' THEN b.runs ELSE 0 END) AS odi_runs,
       SUM(CASE WHEN m.description LIKE '%T20%' THEN b.runs ELSE 0 END) AS t20_runs,
       AVG(b.runs * 1.0) AS overall_avg
FROM players p
JOIN batting_stats b ON p.player_id = b.player_id
JOIN matches m ON b.match_id = m.match_id
GROUP BY p.player_id, p.full_name
HAVING ( (test_runs > 0) + (odi_runs > 0) + (t20_runs > 0) ) >= 2;''',

"International Team's performance":'''SELECT t.team_name,
       SUM(CASE WHEN v.country = t.country AND m.winner_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
       SUM(CASE WHEN v.country != t.country AND m.winner_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
FROM matches m
JOIN teams t ON t.team_id IN (m.team1_id, m.team2_id)
JOIN venues v ON m.venue_id = v.venue_id
GROUP BY t.team_id, t.team_name;''',


"Partnerships":'''
SELECT p1.full_name AS striker,
       p2.full_name AS non_striker,
       part.runs_scored,
       part.innings_no
FROM partnerships part
JOIN players p1 ON part.striker_id = p1.player_id
JOIN players p2 ON part.non_striker_id = p2.player_id
WHERE part.runs_scored >= 100;''',

"Bowling Performance at different venues":'''
SELECT p.full_name,
       v.name AS venue,
       COUNT(DISTINCT m.match_id) AS matches_played,
       SUM(bw.wickets) AS total_wickets,
       AVG(bw.economy) AS avg_economy
FROM bowling_stats bw
JOIN players p ON bw.player_id = p.player_id
JOIN matches m ON bw.match_id = m.match_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE bw.overs >= 4
GROUP BY p.player_id, v.venue_id
HAVING matches_played >= 3;''',

"Players who perform exceptionally well in close matches":'''WITH parsed_matches AS (
    SELECT 
        m.match_id,
        m.Status,
        -- victory_type detect karo (runs/wickets)
        CASE 
            WHEN m.Status LIKE '%run%' THEN 'runs'
            WHEN m.Status LIKE '%wkt%' THEN 'wickets'
            ELSE NULL
        END AS victory_type,

        -- victory_margin number extract karo
        CAST(
            TRIM(
                REPLACE(
                    REPLACE(
                        REPLACE(m.Status, 'won by', ''), 
                        'wkts', ''
                    ), 
                    'runs', ''
                )
            ) AS INT
        ) AS victory_margin
    FROM matches m
    WHERE m.Status LIKE '%won by%'
),

close_matches AS (
    SELECT *
    FROM parsed_matches
    WHERE 
        (victory_type = 'runs' AND victory_margin < 50)
        OR (victory_type = 'wickets' AND victory_margin < 5)
)

SELECT 
    p.full_name,
    AVG(bs.runs) AS avg_runs_in_close,
    COUNT(DISTINCT cm.match_id) AS close_matches_played,
    SUM(CASE WHEN cm.victory_type IS NOT NULL AND m.winner_id = bs.player_id THEN 1 ELSE 0 END) AS team_wins_with_player
FROM close_matches cm
JOIN batting_stats bs ON cm.match_id = bs.match_id
JOIN players p ON bs.player_id = p.player_id
JOIN matches m ON cm.match_id = m.match_id
GROUP BY p.full_name
HAVING COUNT(DISTINCT cm.match_id) > 0
ORDER BY avg_runs_in_close DESC;
''',


"Players' Batting performance changes over different years":'''
SELECT p.full_name,
       strftime('%Y', m.match_date) AS year,
       AVG(b.runs * 1.0) AS avg_runs,
       AVG(b.strike_rate) AS avg_strike_rate,
       COUNT(DISTINCT m.match_id) AS matches_played
FROM batting_stats b
JOIN players p ON b.player_id = p.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE year >= '2020'
GROUP BY p.player_id, year
HAVING matches_played >= 5;''',


"Toss Decision":'''
WITH match_outcomes AS (
    SELECT
        match_id,
        toss_winner_id,
        toss_decision,
        winner_id,
        CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END AS toss_helped
    FROM matches
    WHERE status LIKE '%won by%'
)
SELECT 
    toss_decision,
    COUNT(*) AS total_matches,
    SUM(toss_helped) AS matches_won_by_toss_winner,
    ROUND(SUM(toss_helped) * 100.0 / COUNT(*), 2) AS win_percentage
FROM match_outcomes
GROUP BY toss_decision;
''',

"Most Economical bowlers":'''
SELECT p.full_name,
       ROUND(SUM(b.runs_conceded) * 1.0 / SUM(NULLIF(b.overs,0)), 2) AS avg_economy,
       SUM(b.wickets) AS total_wickets,
       COUNT(DISTINCT b.match_id) AS matches_played
FROM bowling_stats b
JOIN players p ON p.player_id = b.player_id
JOIN matches m ON m.match_id = b.match_id
JOIN seriesmatches s ON m.series_id = s.series_id
WHERE s.match_type IN ('ODI', 'T20I')
GROUP BY p.full_name
HAVING COUNT(DISTINCT b.match_id) >= 10   -- कम से कम 10 matches खेले हों
   AND SUM(b.overs) / COUNT(DISTINCT b.match_id) >= 2   -- avg ≥ 2 overs per match
ORDER BY avg_economy ASC, total_wickets DESC;''',


"Consistent Batsman":'''
SELECT p.full_name,
       AVG(b.runs * 1.0) AS avg_runs,
       (AVG((b.runs * 1.0)*(b.runs * 1.0)) - (AVG(b.runs * 1.0) * AVG(b.runs * 1.0))) AS run_variance,
       COUNT(b.match_id) AS innings_played
FROM batting_stats b
JOIN players p ON p.player_id = b.player_id
WHERE b.balls >= 10
  AND b.match_id IN (
        SELECT match_id 
        FROM matches 
        WHERE match_date >= '2022-01-01'
      )
GROUP BY p.full_name
HAVING COUNT(b.match_id) >= 5
ORDER BY run_variance ASC, avg_runs DESC;
''',


"How many matches each player has played in different cricket formats":'''
SELECT 
    p.full_name,
    sm.match_type,
    COUNT(DISTINCT m.match_id) AS matches_played,
    AVG(b.runs * 1.0) AS batting_average
FROM players p
JOIN batting_stats b ON p.player_id = b.player_id
JOIN matches m ON m.match_id = b.match_id
JOIN seriesmatches sm ON sm.series_id = m.series_id
GROUP BY p.full_name, sm.match_type
HAVING COUNT(DISTINCT m.match_id) > 0
ORDER BY p.full_name, sm.match_type;
''',


"Performance Ranking":'''
WITH batting AS (
    SELECT 
        player_id,
        SUM(runs) AS total_runs,
        AVG(CAST(runs AS FLOAT)/NULLIF(balls,0)) AS batting_average,
        AVG(strike_rate) AS strike_rate
    FROM batting_stats
    GROUP BY player_id
),
bowling AS (
    SELECT 
        player_id,
        SUM(wickets) AS wickets_taken,
        AVG(runs_conceded*1.0/NULLIF(overs,0)) AS bowling_average,
        AVG(economy) AS economy_rate
    FROM bowling_stats
    GROUP BY player_id
)
SELECT 
    p.full_name,
    (b.total_runs*0.01 + b.batting_average*0.5 + b.strike_rate*0.3) +
    (bo.wickets_taken*2 + (50 - bo.bowling_average)*0.5 + ((6 - bo.economy_rate)*2)) AS performance_score
FROM players p
LEFT JOIN batting b ON b.player_id = p.player_id
LEFT JOIN bowling bo ON bo.player_id = p.player_id
ORDER BY performance_score DESC
LIMIT 20;
''',

"Prediction Analysis between teams":'''
SELECT 
    t1.team_name AS team1,
    t2.team_name AS team2,
    COUNT(m.match_id) AS total_matches,
    SUM(CASE WHEN m.winner_id = t1.team_id THEN 1 ELSE 0 END) AS team1_wins,
    SUM(CASE WHEN m.winner_id = t2.team_id THEN 1 ELSE 0 END) AS team2_wins,
    AVG(
        CASE WHEN m.winner_id = t1.team_id 
             THEN CAST(m.victory_margin AS FLOAT) 
        END
    ) AS avg_margin_team1,
    AVG(
        CASE WHEN m.winner_id = t2.team_id 
             THEN CAST(m.victory_margin AS FLOAT) 
        END
    ) AS avg_margin_team2,
    SUM(CASE WHEN m.toss_winner_id = t1.team_id THEN 1 ELSE 0 END) AS toss_wins_team1,
    SUM(CASE WHEN m.toss_winner_id = t2.team_id THEN 1 ELSE 0 END) AS toss_wins_team2
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
WHERE m.match_date >= date('now', '-3 years')
GROUP BY t1.team_name, t2.team_name
HAVING COUNT(m.match_id) >= 5
ORDER BY total_matches DESC;
''',

"Recent player form and momentum":'''
WITH recent_perf AS (
    SELECT 
        b.player_id,
        b.runs,
        b.strike_rate,
        ROW_NUMBER() OVER (PARTITION BY b.player_id ORDER BY m.match_date DESC) AS rn
    FROM batting_stats b
    JOIN matches m ON m.match_id = b.match_id
)
SELECT 
    p.full_name,
    AVG(CASE WHEN rn <= 5 THEN runs END) AS avg_last5,
    AVG(runs) AS avg_last10,
    AVG(strike_rate) AS recent_strike_rate,
    SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) AS fifties
FROM recent_perf r
JOIN players p ON p.player_id = r.player_id
WHERE rn <= 10
GROUP BY p.full_name;
''',

"Successful batting partnerships":'''WITH batting_order AS (
    SELECT 
        match_id,
        innings_no,
        start_pos AS batsman,   -- ye tumne already batsman1 id dala hai
        ROW_NUMBER() OVER(
            PARTITION BY match_id, innings_no 
            ORDER BY start_pos
        ) AS batting_pos
    FROM partnerships
    GROUP BY match_id, innings_no, start_pos
),
pairs AS (
    SELECT 
        b1.match_id,
        b1.innings_no,
        b1.batsman AS batsman1,
        b2.batsman AS batsman2
    FROM batting_order b1
    JOIN batting_order b2 
      ON b1.match_id = b2.match_id
     AND b1.innings_no = b2.innings_no
     AND b2.batting_pos = b1.batting_pos + 1   -- consecutive players
),
partnership_runs AS (
    SELECT 
        pr.match_id,
        pr.innings_no,
        pr.batsman1,
        pr.batsman2,
        SUM(p.runs_scored) AS total_runs
    FROM pairs pr
    JOIN partnerships p 
      ON p.match_id = pr.match_id 
     AND p.innings_no = pr.innings_no
     AND (p.striker_id = pr.batsman1 OR p.striker_id = pr.batsman2)
    GROUP BY pr.match_id, pr.innings_no, pr.batsman1, pr.batsman2
)
SELECT 
    p1.full_name AS batsman1,
    p2.full_name AS batsman2,
    total_runs
FROM partnership_runs pr
JOIN players p1 ON pr.batsman1 = p1.player_id
JOIN players p2 ON pr.batsman2 = p2.player_id
WHERE total_runs >= 100
ORDER BY total_runs DESC;
''',

"Time-series Analysis of player performance":'''WITH player_quarters AS (
    SELECT 
        b.player_id,
        STRFTIME('%Y-Q%q', m.match_date) AS quarter,
        AVG(b.runs) AS avg_runs,
        AVG(b.strike_rate) AS avg_sr,
        COUNT(*) AS matches_played
    FROM batting_stats b
    JOIN matches m ON m.match_id = b.match_id
    WHERE m.match_date >= '2020-01-01'
    GROUP BY b.player_id, quarter
    HAVING COUNT(*) >= 3
)
SELECT 
    p.full_name,
    quarter,
    avg_runs,
    avg_sr,
    matches_played
FROM player_quarters pq
JOIN players p ON p.player_id = pq.player_id
ORDER BY p.full_name, quarter;
'''}
# Sidebar navigation
st.sidebar.title("**📋Navigation**")
page = st.sidebar.radio("**📑Go to:**", ["**Live Matches**","**Play Stats**","**Questions Explorer**","**Players CRUD**","**Tools Summarization**"])


if page == '**Live Matches**':
    # SQLite connection
    conn = sqlite3.connect('cricbuzz.db')
    cursor = conn.cursor()

    # Show badge function
    def show_badge(text, color="#4CAF50"):
        st.markdown(
            f"<span style='background-color:{color}; color:white; padding:6px 12px; border-radius:12px; font-weight:bold;'>{text}</span>",
            unsafe_allow_html=True
        )

    # API headers
    HEADERS = {
        "x-rapidapi-key": "e722629e77mshcbcbf41f1daefe7p153ea5jsnceeee187e2a3",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
     
    # 🔄 1️⃣ Live Matches
    live_url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    response = requests.get(live_url, headers=HEADERS)

    live_data = {}
    if response.status_code == 200 and response.text.strip() != "":
        try:
            live_data = response.json()
        except:
            st.error("Error parsing live data")

    l1 = []
    for match in live_data.get('typeMatches', []):
        for seriesmatch in match.get('seriesMatches', []):
            if "seriesAdWrapper" in seriesmatch:
                for matches in seriesmatch['seriesAdWrapper'].get('matches', []):
                    matchinfo = matches.get('matchInfo', {})
                    l1.append([
                        matchinfo.get('matchId', ""),
                        matchinfo.get('matchFormat', ""),
                        matchinfo.get('seriesName', ""),
                        matchinfo.get('team1', {}).get('teamId', ""),
                        matchinfo.get('team1', {}).get('teamName', ""),
                        matchinfo.get('team2', {}).get('teamId', ""),
                        matchinfo.get('team2', {}).get('teamName', ""),
                        matchinfo.get('venueInfo', {}).get('ground', ""),
                        matchinfo.get('venueInfo', {}).get('city', "")
                    ])

    if len(l1) == 0:
        st.warning("No live matches available!")
        # st.stop()

    df1 = pd.DataFrame(l1, columns=['matchid', 'matchformat', 'seriesname', 'team1id', 'team1name', 'team2id', 'team2name', 'venue_name', 'venue_city'])
    matchid_list = df1['matchid'].tolist()

    # 2️⃣ Scorecards - Parallel fetch
    def fetch_scard(matchid):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{matchid}/scard"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 200 and res.text.strip():
                return matchid, res.json()
        except:
            return matchid, None
        return matchid, None

    scard_data_dict = {}
    l2 = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_scard, matchid_list))

    for matchid, scard_data in results:
        if not scard_data:
            continue
        scard_data_dict[matchid] = scard_data
        state = "complete" if scard_data.get("ismatchcomplete", False) else "incomplete"
        status = scard_data.get('status', 'Not Available')
        status_margin = status.split('by')[1].strip() if 'by' in status else 'N/A'
        winner = status.split('won')[0].strip() if 'won' in status else 'N/A'

        for scores in scard_data.get('scorecard', []):
            l2.append([
                matchid,
                scores.get('inningsid'),
                scores.get('batteamname'),
                scores.get('score'),
                scores.get('wickets'),
                scores.get('overs'),
                scores.get('runrate'),
                state,
                status,
                status_margin,
                winner,
                str(scores.get('extras', {}))
            ])

    df2 = pd.DataFrame(l2, columns=['matchid', 'inning_no', 'batteam_name', 'score', 'wicket', 'overs', 'runrate', 'state', 'status', 'status_margin', 'winner', 'extras'])

    # 3️⃣ Toss Info - Parallel fetch
    def fetch_overs(matchid):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{matchid}/overs"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 200 and res.text.strip():
                overs_data = res.json()
                toss = overs_data.get('matchheaders', {}).get('tossresults', {})
                return matchid, toss.get('tosswinnername', 'N/A'), toss.get('decision', 'N/A')
        except:
            return matchid, 'N/A', 'N/A'
        return matchid, 'N/A', 'N/A'

    l3 = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        toss_results = list(executor.map(fetch_overs, matchid_list))

    for matchid, winnername, decision in toss_results:
        l3.append([matchid, winnername, decision])

    df3 = pd.DataFrame(l3, columns=['matchid', 'tosswinnername', 'decision'])

    # 4️⃣ Merge DataFrames
    df1['matchid'] = df1['matchid'].astype(int)
    df2['matchid'] = df2['matchid'].astype(int)
    df3['matchid'] = df3['matchid'].astype(int)

    merged_df = pd.merge(df1, df2, on='matchid', how='left')
    final_df = pd.merge(merged_df, df3, on='matchid', how='left')

    df_final = final_df.copy()
    df_final['match_name'] = df_final['team1name'] + " vs " + df_final['team2name']

    # 🖥️ Streamlit UI
    st.title('🧾 Select a match')
    unique_matches = df_final[['matchid', 'match_name']].drop_duplicates(subset=['matchid'])
    match_name = st.selectbox('Choose a match', ['Select'] + unique_matches['match_name'].tolist())

    if match_name != 'Select':
        match_data = df_final[df_final['match_name'] == match_name]
        matchid = int(match_data['matchid'].iloc[0])

        # Show info
        col1, col2 = st.columns(2)
        with col1:
            st.write('**Match Name**')
            show_badge(match_name, "#1f77b4")
        with col2:
            st.write('**Series Name**')
            show_badge(match_data['seriesname'].iloc[0], "#ff7f0e")

        st.write("**Match date:**", datetime.now().strftime("%Y-%m-%d"))
        st.write("**Match Format:**", match_data['matchformat'].iloc[0])
        st.write("**Match Venue:**", match_data['venue_name'].iloc[0])
        st.write("**Match City:**", match_data['venue_city'].iloc[0])
        st.write("**Match Status:**", match_data['status'].iloc[0])
        st.write("**Match State:**", match_data['state'].iloc[0])

        # Score
        st.title("Current Score")
        inning1 = match_data[match_data['inning_no'] == 1]
        inning2 = match_data[match_data['inning_no'] == 2]

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Team1 Name**")
            st.write(inning1['batteam_name'].iloc[0] if not inning1.empty else "N/A")
            st.write("**Innings1 Score**")
            st.write(inning1['score'].iloc[0] if not inning1.empty else "N/A")
        with col2:
            st.write("**Team2 Name**")
            st.write(inning2['batteam_name'].iloc[0] if not inning2.empty else "N/A")
            st.write("**Innings2 Score**")
            st.write(inning2['score'].iloc[0] if not inning2.empty else "N/A")

        # 🧾 Full Scorecard
        if st.button("Load Full Scorecard"):
            scard_data = scard_data_dict.get(matchid, {})
            scorecards = scard_data.get('scorecard', [])

            for i, inning in enumerate(scorecards, start=1):
                st.subheader(f"Innings {i} - {inning.get('batteamname', '')}")

                # Batting
                batting_list = []
                for bat in inning.get('batsman', []):
                    batting_list.append([
                        bat.get('name', ''),
                        bat.get('runs', 0),
                        bat.get('balls', 0),
                        bat.get('fours', 0),
                        bat.get('sixes', 0),
                        bat.get('strkrate', 0.0),
                        bat.get('outdec', 'Not Out')
                    ])
                if batting_list:
                    batting_df = pd.DataFrame(batting_list, columns=['Name', 'Runs', 'Balls', '4s', '6s', 'SR', 'Status'])
                    st.write("**Batting**")
                    st.dataframe(batting_df)

                # Bowling
                bowling_list = []
                for bowl in inning.get('bowler', []):
                    bowling_list.append([
                        bowl.get('name', ''),
                        bowl.get('overs', 0),
                        bowl.get('maidens', 0),
                        bowl.get('runs', 0),
                        bowl.get('wickets', 0),
                        bowl.get('economy', 0.0)
                    ])
                if bowling_list:
                    bowling_df = pd.DataFrame(bowling_list, columns=['Name', 'Overs', 'Maidens', 'Runs', 'Wickets', 'Econ'])
                    st.write("**Bowling**")
                    st.dataframe(bowling_df)

    conn.close()
    st.markdown("### 📱 About This Dashboard")
    st.info("""
**Live Scores Page:**
- Real-time cricket match updates  
- Ball-by-ball commentary  
- Scorecards with team & player stats  
- Quick access to ongoing matches  

Perfect for learning Python + API integration + real-time data handling! 🚀
""")
elif page == "**Play Stats**":
    # ================== API Config ==================
    API_KEY = "e722629e77mshcbcbf41f1daefe7p153ea5jsnceeee187e2a3"
    API_HOST = "cricbuzz-cricket.p.rapidapi.com"
    HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

    # ================== API Calls ==================
    def search_player(name):
        url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
        query = {"plrN": name}
        res = requests.get(url, headers=HEADERS, params=query)
        if res.status_code == 200:
            return res.json().get("player", [])
        return []

    def get_player_profile(player_id):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
        return {}

    def get_batting_stats(player_id):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
        return {}

    def get_bowling_stats(player_id):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
        return {}

    # ================== Streamlit UI ==================
    st.set_page_config(layout="wide")
    # st.sidebar.title("🏏 Cricket Dashboard")
    st.title("📊 Cricket Player Statistics")

    # --- Search box
    player_name = st.text_input("Enter player name:")

    if player_name:
        players = search_player(player_name)
        if players:
            options = {f"{p['name']} ({p['teamName']})": p["id"] for p in players}
            selected = st.selectbox("Select a Player:", list(options.keys()))

            if selected:
                pid = options[selected]

                profile = get_player_profile(pid)
                batting = get_batting_stats(pid)
                bowling = get_bowling_stats(pid)

                # Layout: Left Profile | Right Stats
                left, right = st.columns([2, 1])

                # --- LEFT SIDE (Profile + Career)
                with left:
                    st.header(f"{profile.get('name')} - Profile")
                    if profile.get("image"):
                        st.image(profile.get("image"), width=150)
                    st.write("**Nickname:**", profile.get("nickName"))
                    st.write("**Role:**", profile.get("role"))
                    st.write("**Batting:**", profile.get("bat"))
                    st.write("**Bowling:**", profile.get("bowl"))
                    st.write("**DOB:**", profile.get("DoB"))
                    st.write("**Birth Place:**", profile.get("birthPlace"))
                    st.write("**Team:**", profile.get("intlTeam"))

                    if "appIndex" in batting:
                        st.markdown(f"[🔗 View Full Profile]({batting['appIndex']['webURL']})")

                    st.markdown("---")

                    if batting:
                        st.subheader("🏏 Batting Career Stats")
                        df_bat = pd.DataFrame(
                            [row["values"] for row in batting.get("values", [])],
                            columns=batting.get("headers", []),
                        )
                        st.dataframe(df_bat)

                    if bowling:
                        st.subheader("🎯 Bowling Career Stats")
                        df_bowl = pd.DataFrame(
                            [row["values"] for row in bowling.get("values", [])],
                            columns=bowling.get("headers", []),
                        )
                        st.dataframe(df_bowl)

                # --- RIGHT SIDE (Summary + Graphs)
                with right:
                    st.subheader("📌 Career Summary")

                    if batting:
                        df_bat = pd.DataFrame(
                            [row["values"] for row in batting.get("values", [])],
                            columns=batting.get("headers", []),
                        )
                        if not df_bat.empty and "ROWHEADER" in df_bat.columns:
                            df_bat.set_index("ROWHEADER", inplace=True)

                            try:
                                # Handle Runs
                                runs = pd.to_numeric(df_bat.loc["Runs"], errors="coerce").dropna()
                                avg = pd.to_numeric(df_bat.loc["Average"], errors="coerce").dropna()

                                if not runs.empty:
                                    max_runs = runs.max()
                                    st.metric("🏆 Max Runs", max_runs)

                                    # --- Top 5 Runs
                                    top5_runs = runs.sort_values(ascending=False).head(5)
                                    st.write("🔝 Top 5 Runs:")
                                    st.dataframe(top5_runs)

                                    fig1, ax1 = plt.subplots()
                                    top5_runs.plot(kind="bar", ax=ax1)
                                    ax1.set_title("Top 5 Runs")
                                    ax1.set_ylabel("Runs")
                                    st.pyplot(fig1)

                                # --- Top 5 Averages
                                if not avg.empty:
                                    top5_avg = avg.sort_values(ascending=False).head(5)
                                    st.write("🔝 Top 5 Averages:")
                                    st.dataframe(top5_avg)

                                    fig2, ax2 = plt.subplots()
                                    top5_avg.plot(kind="bar", ax=ax2, color="orange")
                                    ax2.set_title("Top 5 Batting Averages")
                                    ax2.set_ylabel("Average")
                                    st.pyplot(fig2)

                            except Exception as e:
                                st.warning("⚠️ Batting stats incomplete or invalid format.")

                    if bowling:
                        df_bowl = pd.DataFrame(
                            [row["values"] for row in bowling.get("values", [])],
                            columns=bowling.get("headers", []),
                        )
                        if not df_bowl.empty and "ROWHEADER" in df_bowl.columns:
                            df_bowl.set_index("ROWHEADER", inplace=True)

                            try:
                                wickets = pd.to_numeric(df_bowl.loc["Wickets"], errors="coerce").dropna()
                                if not wickets.empty:
                                    top5_wkts = wickets.sort_values(ascending=False).head(5)

                                    st.write("🔝 Top 5 Wicket Takers:")
                                    st.dataframe(top5_wkts)

                                    fig3, ax3 = plt.subplots()
                                    top5_wkts.plot(kind="bar", ax=ax3, color="green")
                                    ax3.set_title("Top 5 Wickets")
                                    ax3.set_ylabel("Wickets")
                                    st.pyplot(fig3)

                            except Exception as e:
                                st.warning("⚠️ Bowling stats incomplete or invalid format.")

        else:
            st.warning("⚠️ No players found. Try again.")
        
    st.markdown("### 📱 About This Dashboard")
    st.info("""
    **Player Stats Page:**
    - Search any cricket player  
    - Career statistics across formats  
    - Comprehensive player profiles  
    - No biography section (to save API calls)  

    Perfect for learning Python + API integration + Database operations! 🚀
    """) 

elif page == "**Questions Explorer**":
    st.header("📃SQL Questions Explorer")

    question = st.selectbox("**Select a Question**", list(questions.keys()))
    st.code(questions[question], language="sql")

    if st.button("**Run Query**",):
        df = pd.read_sql_query(questions[question], conn)
        st.dataframe(df)

    st.markdown("### 📱 About This Dashboard")
    st.info("""
**Question Explorer Page (SQL Questions):**
- Browse and search SQL questions from the dataset  
- Filter by topic, difficulty, or keywords  
- View question details and sample queries  
- Interactive DataFrame to explore questions and answers  

Perfect for learning Python + Pandas + SQL + DataFrame operations! 🚀
""")



# ----------------------------
# CRUD on Players
# ----------------------------
elif page == "**Players CRUD**":
    st.header("**🖋Manage Players Table**")

    crud_action = st.radio("**Choose Action:**", ["**Add Player**", "**View Players**", "**Update Player**", "**Delete Player**"])

    if crud_action == "**Add Player**":
       
        with st.form("add_form"):
            cursor.execute("SELECT COALESCE(MAX(player_id), 0) + 1 FROM players")
            new_id = cursor.fetchone()[0]
            full_name = st.text_input("**Full Name**")
            country = st.text_input("**Country**")
            playing_role = st.text_input("**Playing Role**")
            batting_style = st.text_input("**Batting Style**")
            bowling_style = st.text_input("**Bowling Style**")
            submitted = st.form_submit_button("**Add Player**")

            if submitted:
                
                cursor.execute(
                    "INSERT INTO players (player_id,full_name, country, playing_role, batting_style, bowling_style) VALUES (?, ?, ?, ?, ?,?)",
                    (new_id,full_name, country, playing_role, batting_style, bowling_style)
                )
                conn.commit()
                st.success("✅ Player added successfully")

    elif crud_action == "**View Players**":
        df = pd.read_sql_query("SELECT * FROM players", conn)
        st.dataframe(df)

    elif crud_action == "**Update Player**":
        df = pd.read_sql_query("SELECT * FROM players", conn)
        player_id = st.selectbox("Select Player ID to Update", df["player_id"])
        new_name = st.text_input("New Name")
        new_role = st.text_input("New Role")
        if st.button("**Update**"):
            cursor.execute("UPDATE players SET full_name=?, playing_role=? WHERE player_id=?", (new_name, new_role, player_id))
            conn.commit()
            st.success(" Player updated")

    elif crud_action == "**Delete Player**":
        df = pd.read_sql_query("SELECT * FROM players", conn)
        full_name = st.selectbox("Select Name to Delete", df["full_name"])
        if st.button("**Delete**"):
            cursor.execute("DELETE FROM players WHERE full_name=?", (full_name,))
            conn.commit()
            st.success(" Player deleted")
    st.markdown("### 📱 About This Dashboard")
    st.info("""
**CRUD Operations Page:**
- Create, Read, Update, Delete records  
- Manage database entries seamlessly  
- Interactive forms & tables for data handling  
- Ideal for learning database operations in Python  

Perfect for learning Python + Database integration + Streamlit forms! 🚀
""")

elif page=="**Tools Summarization**":

# Page Title
         st.title("📚 About This Project")
         st.write("This project is built using modern tools and technologies to provide a seamless cricket dashboard experience.")
         
         # Section: Tools & Libraries
         st.subheader("🛠 Tools & Libraries Used")
         st.markdown("""
         - **[Streamlit](https://streamlit.io/)** – For building the interactive web app
         - **[Python](https://www.python.org/)** – Core programming language
         - **[Requests](https://docs.python-requests.org/en/master/)** – For making API calls
         - **[Pandas](https://pandas.pydata.org/)** – Data manipulation and analysis
         - **[Matplotlib](https://matplotlib.org/)** – For visualizations and charts
         - **[Cricbuzz API (via RapidAPI)](https://rapidapi.com/)** – Source of real-time cricket data
         - **[GitHub](https://github.com/)** – Version control and repository hosting
         """)
         
         # Section: Features
         st.subheader("✨ Features Implemented")
         st.markdown("""
         - ✅ **Live Scores** – Get real-time match updates
         - ✅ **Player Stats** – Search any player and view complete career stats
         - ✅ **Question Explorer** – Get Insights of each and every page using sql queries
         - ✅ **CRUD Page** – Create,Write,Update,Delete players
         """)
         
         # Section: Tech Stack Diagram
         st.subheader("📐 Architecture Overview")
         st.info("""
         **Frontend:** Streamlit  
         **Backend:** Python (API integration using Requests)  
         **Data Source:** Cricbuzz API (RapidAPI)  
         **Data Handling:** Pandas  
         **Visualization:** Matplotlib  
         """)
         
         # Footer
         st.markdown("---")
         st.markdown("Made with ❤️ by **Vishal Singla**")
