import os
import sys
from app.main import create_app

app = create_app()

if __name__ == '__main__':
    is_frozen = getattr(sys, 'frozen', False)
    debug_mode = not is_frozen
    
    port = int(os.environ.get("PORT", 5000))
    # In production/frozen mode, only bind to 127.0.0.1 for security
    host = "127.0.0.1" if is_frozen else "0.0.0.0"
    
    app.run(host=host, port=port, debug=debug_mode, use_reloader=debug_mode)
