from flask import Flask, jsonify

from database import get_all_requests


# ============================================================
# Flask Application
# ============================================================

app = Flask(
    __name__
)


# ============================================================
# Home Page
# ============================================================

@app.route("/")
def home():

    return """
    <!DOCTYPE html>
    <html>
    <head>

        <title>Campus Help Server</title>

        <style>

            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background: #F5F7FB;
                color: #111827;
            }

            .container {
                max-width: 800px;
                margin: 70px auto;
                background: white;
                padding: 40px;
                border-radius: 18px;
                box-shadow: 0 10px 35px rgba(0,0,0,0.08);
            }

            h1 {
                color: #4F46E5;
                margin-bottom: 10px;
            }

            p {
                color: #6B7280;
                line-height: 1.6;
            }

            .service {
                padding: 15px;
                margin: 12px 0;
                background: #F9FAFB;
                border-radius: 10px;
            }

            .active {
                color: #059669;
                font-weight: bold;
            }

            a {
                color: #4F46E5;
                text-decoration: none;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>Campus Help Server</h1>

            <p>
                Campus LAN Student Help Request System
                server is running successfully.
            </p>

            <div class="service">
                TCP Server:
                <span class="active">Running</span>
                — Port 5000
            </div>

            <div class="service">
                UDP Discovery:
                <span class="active">Running</span>
                — Port 5001
            </div>

            <div class="service">
                FTP Server:
                <span class="active">Running</span>
                — Port 2121
            </div>

            <div class="service">
                HTTP Server:
                <span class="active">Running</span>
                — Port 8000
            </div>

            <p>
                <a href="/health">
                    View Server Health
                </a>
            </p>

            <p>
                <a href="/stats">
                    View Request Statistics
                </a>
            </p>

        </div>

    </body>
    </html>
    """


# ============================================================
# Health Endpoint
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "service": "Campus Help Server",
        "tcp_port": 5000,
        "udp_port": 5001,
        "ftp_port": 2121,
        "http_port": 8000
    })


# ============================================================
# Statistics Endpoint
# ============================================================

@app.route("/stats")
def statistics():

    result = get_all_requests()

    if not result.get(
        "success"
    ):

        return jsonify({
            "success": False,
            "message": "Unable to load statistics."
        }), 500

    requests = result.get(
        "requests",
        []
    )

    pending = 0
    progress = 0
    resolved = 0

    for request in requests:

        status = request.get(
            "status"
        )

        if status == "Pending":

            pending += 1

        elif status == "In Progress":

            progress += 1

        elif status == "Resolved":

            resolved += 1

    return jsonify({
        "success": True,
        "total_requests": len(requests),
        "pending": pending,
        "in_progress": progress,
        "resolved": resolved
    })


# ============================================================
# Start HTTP Server
# ============================================================

def start_http_server():

    print("=" * 50)

    print(
        "Campus Help HTTP Server Started"
    )

    print(
        "HTTP Port: 8000"
    )

    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False,
        threaded=True
    )