# Clipper

Pull an exact time range out of a long video, at full quality, without downloading the whole thing.

Paste a link, mark an in point and an out point, and get back just those seconds. Under the hood it uses [yt-dlp](https://github.com/yt-dlp/yt-dlp), which can fetch only the fragments that fall inside your time range on most sites, then uses `ffmpeg` to cut precisely on your marks — no full download, no re-encoding the whole file.

## Features

- **Video clip** — trims to your in/out points, full original quality
- **Audio only** — trims to your in/out points, extracts the audio as a 192kbps mp3
- **Whole video** — downloads the entire source with no trimming
- Works with any site [yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) (1000+, including YouTube)
- Live progress bar while it downloads and processes
- Runs entirely locally — nothing leaves your machine except the request to the video's own host

## Requirements

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your `PATH`
  - Mac: `brew install ffmpeg`
  - Windows: `winget install ffmpeg` (or download from ffmpeg.org and add it to PATH)
  - Linux: `sudo apt install ffmpeg`

## Setup

```bash
git clone https://github.com/Subham-kumar-eh/video-clipper.git
cd video-clipper

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Usage

1. **Paste a video URL** into the Source URL field and click **Load**. The title, thumbnail, and duration will appear.
2. **Pick an output mode**: Video Clip, Audio Only, or Whole Video.
3. **For Video Clip or Audio Only** — set the In point and Out point as timecodes (`hh:mm:ss`, `mm:ss`, or just seconds all work), and pick a quality cap if you want one.
4. **For Whole Video** — the in/out fields are skipped entirely; it downloads the full source at the quality you pick.
5. Click the action button. A progress bar tracks the download and the ffmpeg processing step.
6. When it finishes, click **Download** to save the file.

## How it works

- `clipper.py` — talks to yt-dlp. `get_video_info` fetches title/duration without downloading anything. `run_clip_job` downloads just the requested time window (`download_ranges`) and re-encodes the cut edges so the clip starts/ends exactly on the mark (`force_keyframes_at_cuts`), while everything in between stays original quality. For audio mode it adds an `FFmpegExtractAudio` postprocessing step; for whole-video mode it skips the range entirely.
- `app.py` — a small Flask app with four routes: fetch metadata, start a job in a background thread, poll its progress, and download the finished file.
- `static/app.js` — timecode parsing, the load flow, mode switching, and progress polling.

## Notes / limitations

- Clip precision depends on the source. Most sites yt-dlp supports (YouTube included) allow fragment-level range downloads; a few fall back to fetching more than the exact window before cutting. Either way, the output file is trimmed to the exact in/out points.
- This is a local, single-user tool — job state lives in memory, so it resets if the server restarts.
- Only use it on videos you have the right to download (your own uploads, content licensed for reuse, sites' own terms permitting it, etc.) — same rule that applies to yt-dlp itself.

## Roadmap

- [ ] Drag-to-select in/out points on a scrubber instead of typing timecodes
- [ ] Batch mode: clip several ranges from one video in one pass
- [ ] Dockerfile for one-command setup

## License

[MIT](LICENSE)

Disclaimer

Clipper is provided as-is, without guarantees of availability, accuracy, or fitness for any particular purpose. The developers are not responsible for data loss, failed downloads, corrupted files, service restrictions, or any other issues resulting from the use of this software.

Clipper itself does not provide or host video content. Users are responsible for ensuring that their use of downloaded material complies with applicable laws, licenses, and the terms of the websites they use.
