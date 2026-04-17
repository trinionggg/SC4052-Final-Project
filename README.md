# SC4052 Project2

# AI Coaching for League of Legends

CoachBot is a web-based AI coaching tool for League of Legends players. It fetches match data from the Riot Games API, grades player performance using a role-weighted scoring system, and generates personalised coaching reports using OpenAI's GPT-4o-mini model.


## Setup

### Prerequisites
- Python 3.10+
- A [Riot Games API key](https://developer.riotgames.com) (free, regenerates every 24 hours)
- An [OpenAI API key]

### 1. Clone the repository

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Create a `.env` file in the `backend/` folder
```
RIOT_API_KEY=your_riot_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 4. Run the backend
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 5. Open the frontend
```bash
cd frontend
python -m http.server 3000
```