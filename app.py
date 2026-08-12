"""
Clipper - a tiny local web UI that pulls an exact time range out of a long
video at full quality, without downloading the whole thing.

Run it with:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import threading
import uuid
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory, abort

from clipper import get_video_info, run_clip_job, JOBS, JOBS_LOCK

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info", methods=["POST"])
def api_info():
    data = request.get_json(force=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "Paste a video URL first."}), 400
    try:
        info = get_video_info(url)
        return jsonify(info)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 400


@app.route("/api/clip", methods=["POST"])
def api_clip():
    data = request.get_json(force=True) or {}
    url = (data.get("url") or "").strip()
    start = data.get("start")
    end = data.get("end")
    quality = data.get("quality", "best")

    if not url or start is None or end is None:
        return jsonify({"error": "URL, start and end are required."}), 400
    try:
        start, end = float(start), float(end)
    except (TypeError, ValueError):
        return jsonify({"error": "Start and end must be numbers of seconds."}), 400
    if end <= start:
        return jsonify({"error": "Out point must be after the in point."}), 400

    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {"status": "queued", "percent": 0, "message": "Queued...",
                         "file": None, "error": None}

    thread = threading.Thread(
        target=run_clip_job,
        args=(job_id, url, start, end, quality, str(DOWNLOAD_DIR)),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/progress/<job_id>")
def api_progress(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job"}), 404
    return jsonify(job)


@app.route("/api/download/<job_id>")
def api_download(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or job.get("status") != "done" or not job.get("file"):
        abort(404)
    return send_from_directory(DOWNLOAD_DIR, job["file"], as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
