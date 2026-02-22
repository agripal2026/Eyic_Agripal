from waitress import serve
from app import app, clear_sessions_on_startup, init_database
import logging
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    # Initialize
    clear_sessions_on_startup()
    init_database()
    
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🌱 AGRIPAL - PRODUCTION SERVER STARTING")
    print("=" * 60)
    print(f"   Local:   http://127.0.0.1:5000")
    print(f"   Network: http://{local_ip}:5000")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    serve(
        app,
        host='0.0.0.0',
        port=5000,
        threads=8
    )