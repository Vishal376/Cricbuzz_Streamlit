🏏 **Cricbuzz Streamlit App**

A Streamlit-based interactive cricket dashboard that fetches real-time cricket data using the Cricbuzz API. Perfect for exploring live scores, player stats, and match details in an intuitive UI.

🚀 **Features**

✅ Live Scores Page – View real-time match updates with scorecards
✅ Player Stats Page – Search any cricket player and view career stats across formats
✅ Question Explorer Page – Get Insights using sql queries
✅ Crud Operation Page - Create,Write,Update,Delete Player's Info
✅ Simple & Lightweight – Built with Streamlit, Pandas, and Matplotlib
✅ Fast API Integration – Uses Cricbuzz API via RapidAPI

**📂 Project Structure**
CRICBUZZ_STREAMLIT_APP/
├── main.py                # Main Streamlit application
├── cricbuzz.db            # Sqlite database
├── schemas/               # API fetched data code to DB.
└── README.md              # Project documentation

**⚙️ Tech Stack**

Python 3.9+

Streamlit (UI Framework)

Requests (API calls)

Pandas (Data manipulation)

Matplotlib (Charts & graphs)

**🔑 API Configuration**

This app uses Cricbuzz API via RapidAPI. To run the project:

Create a RapidAPI account.

Subscribe to the Cricbuzz API.

Get your API Key.

Add the key in app.py under:

**API_KEY =** "your_api_key_here"
**API_HOST =** "cricbuzz-cricket.p.rapidapi.com"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

**▶️ How to Run**

**Clone the repository:**

git clone https://github.com/Vishal376/Cricbuzz_Streamlit.git
cd cricbuzz-dashboard


**Install dependencies:**

pip install -r requirements.txt


**Run the Streamlit app:**

streamlit run main.py


**Open the local URL in your browser.**
**Live Scores Page**
**Player Stats Page**
**Question Explorer Page**
**Crud Operation Page**

**📌 Future Enhancements**

✅ Add Team Rankings Page

✅ Add Player Comparison Tool

✅ Add Match Prediction using ML

**🤝 Contributing**

Contributions are welcome! Please fork the repo and submit a pull request.

**📜 License**

This project is licensed under the MIT License.

