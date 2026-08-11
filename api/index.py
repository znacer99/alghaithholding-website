import sys
import os

# Add root directory to path for Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export app instance for Vercel serverless handler
app = app
