import logging
import os

import psycopg2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Top Users Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="dashboard"), name="static")
templates = Jinja2Templates(directory="dashboard")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

def get_top_users(limit=20):
    """Get top users from database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            SELECT user_id, posts_cnt, calculated_at 
            FROM top_users_by_posts 
            ORDER BY posts_cnt DESC 
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        cur.close()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
@app.get("/top", response_class=HTMLResponse)
async def read_top(request: Request):
    """Main dashboard endpoint"""
    users = get_top_users(20)

    # Format data for template
    user_data = []
    for user_id, posts_cnt, calculated_at in users:
        user_data.append({
            'user_id': user_id,
            'posts_cnt': posts_cnt,
            'calculated_at': calculated_at.strftime('%Y-%m-%d %H:%M:%S') if calculated_at else 'N/A'
        })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "users": user_data,
            "total_users": len(user_data)
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dashboard"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
