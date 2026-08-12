# Clipper

Pull an exact time range out of a long video, at full quality, without
downloading the whole thing.

Paste a link, mark an in point and an out point, hit **Clip it**. Under the
hood it uses [yt-dlp](https://github.com/yt-dlp/yt-dlp), which can fetch only
the fragments that fall inside your time range on most sites, then uses
`ffmpeg` to cut precisely on your marks.

## Requirements

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your `PATH`
  - Mac: `brew install ffmpeg`
  - Windows: `winget install ffmpeg` (or download from ffmpeg.org and add it to PATH)
  - Linux: `sudo apt install ffmpeg`

## Setup

```bash
git clone https://github.com/YOUR-USERNAME/video-clipper.git
cd video-clipper

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## How it works

- `clipper.py` — talks to yt-dlp. `get_video_info` fetches title/duration
  without downloading anything. `run_clip_job` downloads just the requested
  time window (`download_ranges`) and re-encodes the cut edges so the clip
  starts/ends exactly where you asked (`force_keyframes_at_cuts`), while
  everything in between stays original quality.
- `app.py` — a small Flask app with four routes: load metadata, start a clip
  job in a background thread, poll its progress, and download the finished
  file.
- `static/app.js` — the UI logic: timecode parsing, the load flow, and
  polling the progress bar.

## Notes / limitations

- Clip precision depends on the source. Most sites yt-dlp supports (YouTube
  included) allow fragment-level range downloads; a few will fall back to
  fetching more than the exact window before cutting. Either way, the output
  file is trimmed to your exact in/out points.
- This is a local, single-user tool — job state lives in memory, so it
  resets if you restart the server.
- Only use it on videos you have the right to download (your own uploads,
  content licensed for reuse, sites' own terms permitting it, etc.) — same
  rule that applies to yt-dlp itself.

## Roadmap ideas

- [ ] Drag-to-select in/out points on a scrubber instead of typing timecodes
- [ ] Batch mode: clip several ranges from one video in one pass
- [ ] Optional audio-only output
- [ ] Dockerfile for one-command setup

Contributions welcome — see below if you're new to git and want to get this
running on GitHub.

---

## Putting this on GitHub (beginner walkthrough)

You said you don't know how to do this yet, so here's the whole path, start
to finish.

### 1. Install git

- Mac: it's usually already installed — check with `git --version` in
  Terminal. If not, `brew install git`.
- Windows: download [Git for Windows](https://git-scm.com/download/win),
  install with defaults.
- Linux: `sudo apt install git`.

### 2. Create a GitHub account

Go to [github.com](https://github.com) and sign up if you haven't already.

### 3. Tell git who you are (one-time setup)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Create the repository on GitHub

- Click the **+** in the top-right of GitHub → **New repository**.
- Name it `video-clipper` (or whatever you like).
- Leave it empty — don't add a README, .gitignore, or license from GitHub's
  UI, since this project already has them.
- Click **Create repository**. GitHub will show you a page with some commands
  — you don't need them, the steps below cover it.

### 5. Turn your local folder into a git repository

From inside the `video-clipper` folder on your machine:

```bash
git init
git add .
git commit -m "Initial commit: working clipper app"
```

`git init` starts tracking the folder. `git add .` stages every file (the
`.gitignore` already excludes junk like `venv/` and downloaded clips).
`git commit` saves that snapshot with a message describing it.

### 6. Connect your local repo to GitHub and push

GitHub will have shown you a URL like
`https://github.com/YOUR-USERNAME/video-clipper.git`. Use it here:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/video-clipper.git
git push -u origin main
```

- `git branch -M main` names your default branch `main`.
- `git remote add origin ...` tells git where "GitHub" is for this project.
- `git push -u origin main` uploads your commit. First time, it'll ask you to
  log in — GitHub now requires a
  [personal access token](https://github.com/settings/tokens) instead of your
  password, or you can authenticate via the
  [GitHub CLI](https://cli.github.com/) (`gh auth login`) which handles this
  for you.

Refresh the GitHub page — your code is there.

### 7. Making changes later

Every time you want to save and publish new changes:

```bash
git add .
git commit -m "Describe what you changed"
git push
```

### 8. Making it easy for other editors to use

Since this is open source, a few things help people trust and adopt it:

- The `LICENSE` file (already included, MIT) tells people what they're
  allowed to do with the code.
- Fill in your name in `LICENSE` where it says `[Your Name]`.
- On the GitHub repo page, click the gear icon next to "About" and add a
  short description + topics like `video`, `ffmpeg`, `yt-dlp`, `flask` so
  people can find it.
- If people start opening issues or pull requests, GitHub will email you —
  that's the whole workflow, no extra tooling needed to start.
