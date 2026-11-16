# Shorts Autopilot

**A free robot that makes and uploads faceless YouTube Shorts every day, with every fact checked.**
You set it up once by chatting with **Claude** (an AI assistant). You don't need to know how to code.

> 👋 **Not technical? This page is all you need.** Follow the steps in order. Each step tells you exactly what to click or what to copy and paste into Claude.

---

## What it does

Every day, without you:

1. **Picks a topic** that fits your channel (and never repeats one)
2. **Reads real sources** (Wikipedia, NASA)
3. **Writes a 40–55 second script** with free AI
4. **Fact-checks every sentence** using a *different* AI. Scripts with a wrong fact are thrown away
5. **Records a natural voice** (free Microsoft voices)
6. **Adds pictures and video** (free NASA / Wikimedia / stock footage)
7. **Builds the video**: vertical 1080×1920, word-by-word captions, music
8. **Checks quality** (length, sound, black frames)
9. **Uploads to YouTube**, scheduled for your best times
10. **Learns** from your YouTube numbers which topics and times work

It runs on **GitHub** (free), so your computer can be **off**.

Two example channels are included: **space facts** and **unbelievable true stories**. You can change them to any niche.

**Cost: $0.** Every service used has a free plan. You only need a Claude plan to do the setup.

---

## ⏱️ Before you start

- **Time:** about 2–3 hours the first time. You can spread it over two days.
- **Computer:** a Mac or Windows PC with internet.
- **Phone:** to verify your Google/YouTube account.

---

## 🛑 6 golden rules (read these first)

1. **Never paste a key, password or token into the chat with Claude.** You paste keys yourself into a file called `.env`, or into GitHub's "Secrets" page. Claude tells you where.
2. **Never upload `.env`, `client_secret.json` or any `*_token.json` file to GitHub.** The project already blocks this. Don't change that.
3. **Never turn off the fact-checking** to get more videos. A day with zero videos is fine; a wrong fact hurts your channel.
4. **Never post other people's videos.** This project only makes original videos from free sources.
5. **Run it in only ONE place:** on GitHub (recommended) *or* on your computer, never both. Two places would upload the same videos twice.
6. **When Claude asks "Allow?"**, read its one-line description first. Reading, listing and checking are safe. For upload, delete, publish or push, make sure it's what you asked for.

---

## Step 1: Install these 3 free things

| # | What | Where | How |
|---|---|---|---|
| 1 | **Claude desktop app** | [claude.ai/download](https://claude.ai/download) | Download, install, sign in. You need a Claude plan (Pro or higher) to use the **Code** tab |
| 2 | **GitHub Desktop** | [desktop.github.com](https://desktop.github.com) | Download, install, sign in with your GitHub account (create one at [github.com/signup](https://github.com/signup) if you don't have one) |
| 3 | **A text editor** | Mac: TextEdit is already installed. Windows: Notepad is already installed | Nothing to do. Used to paste your keys into a file |

You **don't** need to install Python, FFmpeg or anything else yourself. Claude installs those for you in Step 4.

---

## Step 2: Create your free accounts

| Account | Where | Why |
|---|---|---|
| **Google account + YouTube channel** | [youtube.com](https://youtube.com) → your picture → **Create a channel** | where your videos go |
| **GitHub** | [github.com/signup](https://github.com/signup) | stores your copy of the project and runs it every day |

💡 **Tip:** Verify your YouTube channel with your phone: [YouTube Studio](https://studio.youtube.com) → **Settings** → **Channel** → **Feature eligibility** → **Verify phone number**. This unlocks custom thumbnails.

---

## Step 3: Make your own copy of this project

1. On this page (on GitHub), click **Fork** at the top right → **Create fork**.
   You now have your own copy at `github.com/YOUR-NAME/shorts-autopilot`.
   - Keep it **Public**. GitHub runs public projects for free with no limit. Your keys stay private either way (they go in "Secrets", which nobody can see).
2. Open **GitHub Desktop** → **File** → **Clone repository** → choose `YOUR-NAME/shorts-autopilot` → **Clone**.
3. Write down the folder it shows (for example `Documents/GitHub/shorts-autopilot`). You need it next.

---

## Step 4: Open the project in Claude and install everything

1. Open the **Claude desktop app** → click the **Code** tab.
2. Click **Open folder** (or "Select folder") and choose the folder from Step 3.
3. Copy this whole message, paste it into Claude and press Enter:

```
I'm not technical. Read README.md and CLAUDE.md. Explain in simple words what this project does.
Then set it up on my computer: install everything it needs (Homebrew if I'm on a Mac,
Python, FFmpeg, a Python virtual environment and the Python packages), one step at a time.
Before each step, tell me in one sentence what it does. Don't ask me to paste any keys into this chat.
When everything is installed, run the test suite and tell me if it passed.
```

**What to expect:**
- Claude asks **"Allow?"** before running commands. Click **Allow** (installing is safe).
- On a Mac it may ask you to install **Homebrew** and type **your Mac password** in a Terminal window. That's normal. Type it yourself (you won't see the letters as you type).
- At the end, about **420 tests** should pass. If something fails, just say: `Something failed. Fix it and explain in simple words.`

---

## Step 5: Get your free keys (about 15 minutes)

Paste this into Claude:

```
Create my .env file from .env.example and open it in a text editor for me.
Then tell me, one at a time, which free keys I need, the exact website for each,
and what to click. I'll paste the keys into the file myself. Wait for me to say "done" after each one.
```

The keys you'll get (all free, no credit card):

| Key | Where | Needed? |
|---|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → **Create API key** | ✅ **Required** |
| `GEMINI_API_KEY_CLIPS` | Same site, but signed in with a **different** Google account | Recommended if you run 2 channels |
| `PIXABAY_API_KEY` | [pixabay.com/api/docs](https://pixabay.com/api/docs/) → sign in → the key is shown on the page | Recommended (stock video) |
| `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `NVIDIA_API_KEY` | Links are inside the `.env` file | Optional backups when Gemini is busy |

How to paste a key: in the `.env` file, find the line (for example `GEMINI_API_KEY=`) and paste the key **right after the `=`**, with no spaces. Save the file.

Then tell Claude:

```
I saved my keys in .env. Check that they work, without printing them or showing them to me.
```

---

## Step 6: Make it YOUR channel and make a test video

Change the words in [brackets], then paste into Claude:

```
Set up the main channel for my niche: [for example: "space facts for curious teenagers in the US"].
My channel name is [your channel name]. Update config.yaml (channel name, niche, signature angle,
audience, description, keywords, playlist) so it fits. Keep all the fact-checking and quality settings.
Show me the changes in simple words before saving.
```

Only want **one** channel? Paste: `I only want one channel. Turn the second channel (clips) off safely.`

Then make a **practice video** (nothing gets uploaded):

```
Make one test video for the main channel as a dry run (no uploads). When it's done,
open the video for me and show me its script, its sources and the fact-check result.
```

Watch it. Don't like something? Just describe it, for example:
`The voice is too fast and the captions are too small. Fix it and make another test video.`

---

## Step 7: Connect your YouTube channel (one time, about 30 minutes)

Paste into Claude:

```
Walk me through connecting my YouTube channel for automatic uploads, one click at a time:
create a Google Cloud project, enable the YouTube Data API v3 and the YouTube Analytics API,
set up the OAuth consent screen (External, then publish the app "In production" so the login
doesn't expire every 7 days), create a Desktop OAuth client and save it as client_secret.json
in this folder. Wait for me to say "done" after each step.
```

Then:

```
Run the YouTube login (auth-youtube, then auth-analytics) for the main channel.
I'll click Allow in the browser and choose MY channel.
```

```
Find my channel's ID from the login, put it in config.yaml as youtube_channel_id,
and set youtube enabled to true. Show me the change.
```

**Good to know:**
- If Google says **"This app isn't verified"**, click **Advanced** → **Go to (app name)**. It's your own app, so it's safe.
- If your uploaded videos stay **Private** even after their publish time, Google wants a free check of new projects. Ask Claude: `Help me fill in the YouTube API audit form honestly.`
- Using a second channel? Repeat this step and add `for the clips channel` to each message.

---

## Step 8: Put it on autopilot (runs every day, even with your computer off)

Paste into Claude:

```
Explain step by step how to add my secrets to GitHub Actions for my fork of this project.
Tell me the exact secret names the workflow needs (ENV_FILE, YT_TOKEN_COSMIC, YT_ANALYTICS_COSMIC,
and YT_TOKEN_CLIPS, YT_ANALYTICS_CLIPS if I use a second channel) and which local file goes into each one.
Open each file for me so I can copy it myself, but never print the contents in this chat.
```

On GitHub: **your fork** → **Settings** → **Secrets and variables** → **Actions**:

1. **Secrets** tab → **New repository secret** → type the name → paste the file's **entire** contents → **Add secret**. Repeat for each one.
2. **Variables** tab → **New repository variable** → name: `SCHEDULER` → value: `github` → **Add variable**. This switches on the daily timer.

Then test it:

1. Click the **Actions** tab → **I understand my workflows, go ahead and enable them**.
2. Click **Daily video** on the left → **Run workflow** → choose your channel → keep **Dry run** ticked → **Run workflow**.
3. Wait about 10 minutes, then ask Claude: `Read the latest GitHub Actions run of my fork and tell me if it worked.`
4. If it worked, run it once more with **Dry run unticked**. Then check [YouTube Studio](https://studio.youtube.com) → **Content**: a new video should show as **Scheduled**. 🎉

From now on it runs **by itself, 4 times a day** (2 per channel) and fills your schedule days ahead.
⚠️ After this, **don't** also run the daily command on your computer (golden rule 5).

**Want different posting times?** Ask Claude: `I want my videos to post at the best times for viewers in [country]. Suggest times and change the schedule after I approve.`

---

## Step 9: Your 10-minute daily routine

1. Open **GitHub Desktop** → **Fetch origin** → **Pull origin**.
2. In Claude, paste:

```
Pull the latest changes and give me today's report for my channels in simple words:
videos made, uploaded and scheduled, anything rejected and why, how many days are queued ahead,
and any problems I need to fix.
```

3. Watch the newest scheduled video in YouTube Studio. Do the pictures match the words? Any obviously wrong fact?
   If something is wrong:
   `The video "[title]" has this problem: [describe]. Take it off the schedule safely (make it private, don't delete it) and explain what you did.`

**Once a week:**

```
Summarize this week: best and worst videos with their views, which posting times work best,
recurring problems, and 3 concrete ideas to grow. Show me exactly what you'd change before changing anything.
```

---

## When something goes wrong

| You see | What it means | What to do |
|---|---|---|
| "503", "overloaded", "Deferred" | Google's free AI was busy | Nothing. The next run tries again |
| Run finished but 0 videos | The fact-check rejected scripts (that's good), or the AI was busy | Normal on some days. 3+ days in a row: ask Claude why |
| "quota" | YouTube's daily upload limit | Nothing. It resets every day |
| "invalid_grant", "token expired", "auth" | Your YouTube login expired | Ask Claude to redo the login (Step 7), then update the GitHub secret (Step 8) |
| Run started late | GitHub's timer is often late | Fine. Videos are scheduled days ahead |

**Emergency stop:** GitHub → **Actions** → **Daily video** → **"..."** (top right) → **Disable workflow**. Turn it back on the same way.
Videos already scheduled on YouTube still go out. To stop one, set it to **Private** in YouTube Studio.

**Any error you don't understand:** copy the red text (make sure it has no keys in it) and paste:
`Explain this error in simple words and tell me if I need to do anything: [paste error]`

---

## Handy prompts to copy

| You want to… | Paste this into Claude |
|---|---|
| Understand the project | `Explain how this project decides what video to make next, like I'm 12.` |
| Change the voice | `Change the voice to a calm female British voice and make a test video.` |
| Change the captions | `Make the captions bigger and yellow. Show me a test frame.` |
| Switch language | `Switch the main channel to Hindi and make a dry-run video.` |
| Get topic ideas | `Suggest 10 topic ideas for my channel. Don't add them until I approve.` |
| Add approved topics | `Add these approved topics to the queue: [list].` |
| Grow views | `My views are low. Read my YouTube analytics and suggest what to change, with reasons.` |
| Save changes to GitHub | `Does this change contain any key, token, password or personal data?` (It must say **no**.) Then: `Commit and push my changes.` |

---

## For developers

- [`CLAUDE.md`](CLAUDE.md): the technical manual (architecture, commands, invariants). Claude reads it automatically.
- `main.py`: the command reference (`python main.py --help`).
- [`docs/`](docs/): architecture, quality checklist, multi-channel design, analytics, policy notes.
- Tests: `.venv/bin/pytest` (about 420 tests, all offline).

## Safety built in

- Scripts that say anything the sources don't support are **rejected**, never published.
- Every upload checks that it's going to **your** channel (channel ID check).
- AI-generated media is disclosed to YouTube automatically.
- Secrets live only in `.env` on your computer and in **GitHub Secrets**, never in the code.

## Responsibility

Use it only on channels you own. You're responsible for what your channels publish and for following YouTube's rules (see [`docs/research/YOUTUBE_POLICY_NOTES.md`](docs/research/YOUTUBE_POLICY_NOTES.md)).
