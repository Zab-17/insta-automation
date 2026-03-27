# api/webhook.py — Vercel Python serverless function
# Cloudinary uploads trigger this webhook → posts to Instagram automatically
from http.server import BaseHTTPRequestHandler
import json
import os
import time
import requests as http_requests

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)
        body = json.loads(raw_body)

        # Cloudinary sends a notification_type field
        if body.get("notification_type", "") != "upload":
            return self._respond(200, {"skipped": "not an upload notification"})

        # Only process videos
        if body.get("resource_type", "") != "video":
            return self._respond(200, {"skipped": "not a video"})

        # Extract video URL
        video_url = body.get("secure_url", "")
        if not video_url:
            return self._respond(400, {"error": "no secure_url in payload"})

        # Extract caption from context metadata
        context = body.get("context", {})
        custom = context.get("custom", {}) if isinstance(context, dict) else {}
        caption = custom.get("caption", "")

        if not caption:
            # Fallback: join tags as hashtags
            tags = body.get("tags", [])
            caption = " ".join(f"#{t}" for t in tags) if tags else ""

        if not caption:
            return self._respond(400, {"error": "no caption — set context.caption when uploading"})

        # Load credentials from env
        account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
        access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")

        if not account_id or not access_token:
            return self._respond(500, {"error": "missing Instagram credentials in env"})

        # Step 1: Create media container
        create_resp = http_requests.post(
            f"{GRAPH_API_BASE}/{account_id}/media",
            params={
                "video_url": video_url,
                "caption": caption,
                "media_type": "REELS",
                "access_token": access_token,
            },
        )

        if create_resp.status_code != 200:
            return self._respond(500, {"error": "container creation failed", "details": create_resp.json()})

        container_id = create_resp.json()["id"]

        # Step 2: Poll for processing (every 5s, max 10 attempts = 50s)
        for attempt in range(10):
            time.sleep(5)
            status_resp = http_requests.get(
                f"{GRAPH_API_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": access_token},
            )
            status = status_resp.json().get("status_code", "")

            if status == "FINISHED":
                break
            if status == "ERROR":
                return self._respond(500, {"error": "Instagram processing failed", "container_id": container_id})
        else:
            return self._respond(504, {"error": "processing timed out", "container_id": container_id})

        # Step 3: Publish
        publish_resp = http_requests.post(
            f"{GRAPH_API_BASE}/{account_id}/media_publish",
            params={
                "creation_id": container_id,
                "access_token": access_token,
            },
        )

        if publish_resp.status_code != 200:
            return self._respond(500, {"error": "publish failed", "details": publish_resp.json()})

        media_id = publish_resp.json()["id"]
        return self._respond(200, {"ok": True, "media_id": media_id, "video_url": video_url})

    def do_GET(self):
        """Health check."""
        return self._respond(200, {"status": "alive"})

    def _respond(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
