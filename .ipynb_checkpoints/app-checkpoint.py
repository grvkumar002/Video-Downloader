from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Ensure 'downloads' folder exists
os.makedirs("downloads", exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_formats", methods=["POST"])
def get_formats():
    video_url = request.json.get("video_url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = [
                {
                    "format_id": f["format_id"],
                    "resolution": f.get("height", "Unknown"),
                    "extension": f["ext"],
                }
                for f in info.get("formats", [])
                if f.get("height")
            ]
        return jsonify({"formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    video_url = data.get("video_url")
    format_id = data.get("format_id")

    if not video_url or not format_id:
        return jsonify({"error": "Missing parameters"}), 400

    # Merge video and audio if needed
    if format_id in ["299", "303"]:  # 1080p60 formats
        format_id += "+140"  # Merge with best audio

    ydl_opts = {
        "format": format_id,
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return jsonify({"message": "✅ Download complete!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
