"""Start server with logging to file and test."""
import sys, os, logging
os.chdir(r'C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab')
sys.path.insert(0, '.')

# Configure logging to file
logging.basicConfig(
    filename='server_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)

import uvicorn
uvicorn.run('app:app', host='127.0.0.1', port=22400, log_level='debug')
