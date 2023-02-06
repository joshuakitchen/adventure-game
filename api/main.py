import uvicorn
from adventure_api.setup import setup_database

if __name__ == '__main__':
  setup_database()
  uvicorn.run('adventure_api:app', host='0.0.0.0', port=8081, reload=True, workers=3)
