import config
from config import create_app
from routes import individual, match
import storage

storage.init_db()  # creates research.db on first run

app = create_app()

app.include_router(individual.router, prefix="/analyze")
app.include_router(match.router,      prefix="/analyze")

@app.get("/")
def root():
    return {"service": "CoachBot-as-a-Service", "version": "2.0", "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}