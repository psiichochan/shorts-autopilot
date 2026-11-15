# Shorts Autopilot: free, fact-checked faceless YouTube Shorts on autopilot

**New here and not technical? Go straight to [START_HERE.md](START_HERE.md).** You'll set everything up by chatting with Claude (an AI assistant). No coding needed.

---

## What this does

It runs one or two faceless YouTube Shorts channels **by itself, every day, for free**:

```
1. Topic      →  picks a topic that fits your channel (and avoids repeats)
2. Research   →  reads real sources first (Wikipedia, NASA)
3. Script     →  writes a 40–55 second hook-first script with free AI (Google Gemini + backups)
4. Fact-check →  a DIFFERENT AI checks every claim against the sources; failing scripts are thrown away
5. Voice      →  natural narration with exact word timings (Microsoft Edge voices, free)
6. Visuals    →  NASA / Wikimedia public-domain images, free stock video, animated scenes
7. Video      →  1080×1920 with word-by-word captions, original music, progress bar
8. QA         →  checks length, loudness, black frames, mismatched images; an AI reviewer watches it
9. Publish    →  uploads to YouTube, scheduled for your best time slots, with sources in the description
10. Learn     →  reads YouTube Analytics and tunes topics and posting times
```

It runs on **GitHub Actions** (free), so your computer can be off.

Two example channel styles are included and ready to use:
- **Space facts** (`config.yaml`): one mind-blowing space fact made real with an everyday comparison.
- **True stories** (`channels/clips.yaml`): surprising, fact-checked history stories.

You can change the niche, voice, look, schedule and language (English or Hindi) by asking Claude.

## What it costs

**$0.** Every service has a free tier: Gemini, Edge TTS voices, NASA/Wikimedia images, Pixabay footage, the YouTube API, GitHub Actions on a public repository. You need a computer to set it up, and Claude to guide you.

## Safety built in

- Scripts that state anything the sources don't support are **rejected**, never published.
- Every upload checks it's going to **your** channel (channel ID check).
- AI-generated media is disclosed to YouTube automatically.
- No downloading or re-uploading other creators' videos.
- Secrets (API keys, logins) live in `.env` locally and in **GitHub Secrets** on GitHub, never in the code.

## For developers

- `CLAUDE.md`: the technical manual (architecture, commands, invariants). Claude reads it automatically.
- `main.py`: the command reference (`python main.py --help`).
- `docs/`: architecture, quality checklist, multi-channel design, analytics, policy notes.
- Tests: `.venv/bin/pytest` (about 420 tests, all offline).

## Responsibility

Use it on channels you own. You're responsible for what your channels publish and for following YouTube's policies (see `docs/research/YOUTUBE_POLICY_NOTES.md`).
