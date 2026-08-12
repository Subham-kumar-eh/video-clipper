// ---------- timecode helpers ----------

// Accepts "ss", "mm:ss", or "hh:mm:ss" and returns whole seconds.
function parseTimecode(value) {
  const parts = value.trim().split(":").map((p) => p.trim());
  if (parts.some((p) => p === "" || isNaN(Number(p)))) return null;
  const nums = parts.map(Number);
  let seconds = 0;
  if (nums.length === 1) seconds = nums[0];
  else if (nums.length === 2) seconds = nums[0] * 60 + nums[1];
  else if (nums.length === 3) seconds = nums[0] * 3600 + nums[1] * 60 + nums[2];
  else return null;
  return seconds >= 0 ? seconds : null;
}

function formatTimecode(totalSeconds) {
  const s = Math.max(0, Math.round(totalSeconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(h)}:${pad(m)}:${pad(sec)}`;
}

// ---------- element refs ----------

const loadCard = document.getElementById("load-card");
const clipCard = document.getElementById("clip-card");
const progressCard = document.getElementById("progress-card");

const urlInput = document.getElementById("url-input");
const loadBtn = document.getElementById("load-btn");
const loadError = document.getElementById("load-error");

const thumb = document.getElementById("thumb");
const videoTitle = document.getElementById("video-title");
const videoSub = document.getElementById("video-sub");

const startInput = document.getElementById("start-input");
const endInput = document.getElementById("end-input");
const qualitySelect = document.getElementById("quality-select");
const clipBtn = document.getElementById("clip-btn");
const clipError = document.getElementById("clip-error");

const progressMessage = document.getElementById("progress-message");
const progressFill = document.getElementById("progress-fill");
const downloadLink = document.getElementById("download-link");
const resetBtn = document.getElementById("reset-btn");

let currentUrl = "";
let currentDuration = null;
let pollTimer = null;

// ---------- load metadata ----------

loadBtn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  loadError.hidden = true;
  if (!url) {
    loadError.textContent = "Paste a video URL first.";
    loadError.hidden = false;
    return;
  }

  loadBtn.disabled = true;
  loadBtn.textContent = "Loading...";

  try {
    const res = await fetch("/api/info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not load that video.");

    currentUrl = url;
    currentDuration = data.duration;

    videoTitle.textContent = data.title;
    videoSub.textContent = currentDuration
      ? `Duration: ${formatTimecode(currentDuration)}${data.uploader ? " · " + data.uploader : ""}`
      : data.uploader || "";
    thumb.src = data.thumbnail || "";
    thumb.style.visibility = data.thumbnail ? "visible" : "hidden";

    startInput.value = "00:00:00";
    endInput.value = formatTimecode(Math.min(10, currentDuration || 10));

    clipCard.hidden = false;
    clipCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    loadError.textContent = err.message;
    loadError.hidden = false;
  } finally {
    loadBtn.disabled = false;
    loadBtn.textContent = "Load";
  }
});

urlInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadBtn.click();
});

// ---------- start clip job ----------

clipBtn.addEventListener("click", async () => {
  clipError.hidden = true;

  const start = parseTimecode(startInput.value);
  const end = parseTimecode(endInput.value);

  if (start === null || end === null) {
    clipError.textContent = "Use hh:mm:ss (or mm:ss, or just seconds).";
    clipError.hidden = false;
    return;
  }
  if (end <= start) {
    clipError.textContent = "Out point must be after the in point.";
    clipError.hidden = false;
    return;
  }
  if (currentDuration && end > currentDuration) {
    clipError.textContent = `Out point is past the video's length (${formatTimecode(currentDuration)}).`;
    clipError.hidden = false;
    return;
  }

  clipBtn.disabled = true;

  try {
    const res = await fetch("/api/clip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: currentUrl, start, end, quality: qualitySelect.value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not start the job.");

    clipCard.hidden = true;
    progressCard.hidden = false;
    progressFill.style.width = "0%";
    downloadLink.hidden = true;
    resetBtn.hidden = true;
    progressMessage.textContent = "Queued...";

    pollProgress(data.job_id);
  } catch (err) {
    clipError.textContent = err.message;
    clipError.hidden = false;
  } finally {
    clipBtn.disabled = false;
  }
});

// ---------- poll progress ----------

function pollProgress(jobId) {
  if (pollTimer) clearInterval(pollTimer);

  pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/progress/${jobId}`);
      const job = await res.json();
      if (!res.ok) throw new Error(job.error || "Lost track of that job.");

      progressFill.style.width = `${job.percent || 0}%`;
      progressMessage.textContent = job.message || "Working...";

      if (job.status === "done") {
        clearInterval(pollTimer);
        downloadLink.href = `/api/download/${jobId}`;
        downloadLink.hidden = false;
        resetBtn.hidden = false;
      } else if (job.status === "error") {
        clearInterval(pollTimer);
        progressMessage.textContent = `Failed: ${job.error || "unknown error"}`;
        resetBtn.hidden = false;
      }
    } catch (err) {
      clearInterval(pollTimer);
      progressMessage.textContent = `Failed: ${err.message}`;
      resetBtn.hidden = false;
    }
  }, 800);
}

// ---------- reset ----------

resetBtn.addEventListener("click", () => {
  progressCard.hidden = true;
  clipCard.hidden = false;
});
