import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from routes.landing_routes import landing

# Fallback route if Vercel forwards /api/index directly to Flask
@app.route('/api/index')
def vercel_api_index_handler():
    return landing()

# Export app instance for Vercel WSGI runner
app = app
