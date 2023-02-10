import os
import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        '__init__:app',
        host='0.0.0.0',
        port=8081,
        reload=os.environ.get('DEBUG', 'false') == 'true',
        workers=None if os.environ.get('DEBUG', 'false') == 'true' else 1)
