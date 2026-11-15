# START HERE: set up your own automatic YouTube Shorts channel with Claude

This guide is for **non-technical people**. If you can use a browser, copy and paste, and follow steps, you can do this.
**Claude does the technical work.** You tell it what to do (we give you the exact words), you click "Allow" when it asks, and you paste your own keys where it tells you.

⏱️ **Time:** about 2–3 hours the first time, spread over a day or two (Google needs time for some steps).
💰 **Cost:** free (only your Claude plan).

---

## 0. The 6 golden rules (read these first)

1. **Never paste a key, password or token into the chat with Claude**, or into any file Claude will upload. Paste keys yourself into the `.env` file or into GitHub Secrets. Claude will tell you where.
2. **Never upload `.env`, `client_secret.json` or any `*_token.json` file to GitHub.** The project already blocks this; don't override it.
3. **Never turn off the fact-checking** to get more videos. A day with zero videos is fine; a wrong fact damages your channel.
4. **Don't post other people's videos.** This project makes original videos from free sources only.
5. **Run it in only ONE place:** either on GitHub (recommended) or on your computer, never both. Two places would upload the same videos twice.
6. **When Claude asks permission** to run something, read its one-line description. Read-only things (list, show, check) are safe. For upload, delete, publish or push, make sure it's what you asked for.

---

## 1. Create the free accounts you need

| Account | Link | Why |
|---|---|---|
| Google account + **YouTube channel** | youtube.com → your picture → *Create a channel* | where videos go |
| GitHub | github.com → Sign up | stores your copy of the project and runs it daily |
| Claude | claude.ai, then download the **desktop app** from claude.ai/download | your assistant |
| GitHub Desktop | desktop.github.com | downloads the project to your computer (no commands) |

Tip: on YouTube, verify your channel with your phone (YouTube Studio → Settings → Channel → Feature eligibility). This unlocks custom thumbnails and longer videos.

---

## 2. Make your own copy of this project

1. Sign in to GitHub. Open this repository's page.
2. Click **Fork** (top right) → **Create fork**. You now have your own copy at `github.com/<your-name>/<repo>`.
   - Keep it **Public**: GitHub Actions is free and unlimited for public repositories. Your keys stay private either way (they go in Secrets, which are never shown).
3. Open **GitHub Desktop** → *File → Clone repository* → pick your fork → **Clone**. Note the folder it shows (e.g. `Documents/GitHub/shorts-autopilot`).

---

## 3. Open the project in Claude

1. Open the **Claude desktop app** → **Code** tab.
2. Choose **Open folder** and select the folder from step 2.3.
3. Paste this message:

> I'm not technical. Read START_HERE.md, README.md and CLAUDE.md. Explain in simple words what this project does. Then set it up on my computer: install everything it needs (Python virtual environment, FFmpeg, the Python packages), one step at a time, telling me before each step what it does. Don't ask me to paste any keys into this chat.

Claude installs everything. Click **Allow** when asked (installing is safe). On a Mac it may ask you to install **Homebrew** first and type your Mac password in the Terminal. That's normal; type it yourself.

When it's done, ask: `Run the test suite and tell me if everything passed.` About 420 tests should pass.

---

## 4. Get your free keys and put them in `.env`

Ask Claude:

> Create my .env file from .env.example and open it in a text editor for me. Then list, one by one, which free keys I need, the exact website for each, and what to click. I'll paste the keys into the file myself.

Get these (all free):
1. **Gemini key (required):** aistudio.google.com/apikey → *Create API key* → copy → paste after `GEMINI_API_KEY=`.
2. **Second Gemini key (recommended, for channel 2):** the same site, signed in with a **different** Google account → paste after `GEMINI_API_KEY_CLIPS=`.
3. **Pixabay (recommended, stock footage):** pixabay.com/api/docs/ → sign in → your key is shown on the page → `PIXABAY_API_KEY=`.
4. **Optional backups** (used when Gemini is busy): Groq, OpenRouter, NVIDIA. The links are in the file.

Save the file. Tell Claude: `I saved the keys in .env. Check they work without showing them to me or printing them.`

---

## 5. Make it YOUR channel, then make a test video

Ask Claude (change the words in brackets):

> Set up the main channel for my niche: [example: "space facts for curious teenagers in the US" / "unbelievable true crime stories" / "motivational stories of athletes"]. My channel name is [name]. Update config.yaml (channel name, niche, signature angle, audience, description, keywords, playlist) so it fits. Keep all the fact-checking and quality settings. Show me the changes in simple words before saving.

If you only want **one** channel, say: `I only want one channel. Turn the second channel (clips) off safely.`

Then make a practice video (nothing is uploaded):

> Make one test video for the main channel as a dry run (no uploads). When it's done, tell me where the video file is and show me its script, sources and fact-check result.

Watch the video. If something's off (the voice, captions, music or pacing), describe it to Claude in plain words and ask it to change the settings.

---

## 6. Connect YouTube (one time, about 30 minutes)

Ask Claude:

> Walk me through connecting my YouTube channel for automatic uploads, one click at a time: creating a Google Cloud project, enabling the YouTube Data API v3 and the YouTube Analytics API, the OAuth consent screen (External, then publish the app "In production" so the login doesn't expire every 7 days), creating a Desktop OAuth client and saving it as client_secret.json in this folder. Wait for me to say "done" after each step.

Then:

> Run the YouTube login (auth-youtube, then auth-analytics) for the main channel. I'll click Allow in the browser and pick MY channel.

> Find my channel's ID from the login and put it in config.yaml as youtube_channel_id, then set youtube enabled to true. Show me the change.

If Google says the app is "unverified", click **Advanced → Go to (app)**. It's your own app.
Note: if your uploaded videos stay **private** even after their publish time, Google wants a free review of new API projects. Ask Claude: `Help me fill in the YouTube API audit form honestly.`

Do the same for channel 2 if you use it (`for the clips channel`).

---

## 7. Put it on autopilot with GitHub (free, runs while your computer is off)

Ask Claude:

> Explain step by step how to add my secrets to GitHub Actions for this repository. Tell me the exact secret names this project's workflow needs (ENV_FILE, YT_TOKEN_COSMIC, YT_ANALYTICS_COSMIC, and the CLIPS ones if I use channel 2) and which local file's contents go into each one. Open each file for me so I can copy it myself, but never print the contents in the chat.

On GitHub: **your fork → Settings → Secrets and variables → Actions**:
- **Secrets** tab → *New repository secret*: create each name and paste the matching file's whole contents.
- **Variables** tab → *New repository variable*: name `SCHEDULER`, value `github`. This switches on the daily timer.

Then **Actions** tab → *I understand my workflows, enable them* → **Daily video** → **Run workflow** → choose the channel → keep **Dry run** ticked → **Run**. Ask Claude: `Read the latest Actions run and tell me if it worked.`

When the dry run works, run it once with Dry run **unticked**. Check YouTube Studio: a new video should be **scheduled**.

From now on it runs **4 times a day** by itself (2 per channel) and fills your schedule days ahead.

> ⚠️ After this, don't run the daily command on your computer too (golden rule 5).

---

## 8. Your routine (10 minutes a day)

**Daily:** open GitHub Desktop → *Fetch origin → Pull*. Then ask Claude:

> Pull the latest changes and give me today's report for my channels in simple words: videos made, uploaded and scheduled, anything rejected and why, how many days are queued ahead, and any problems I need to act on.

Then watch the newest scheduled video in YouTube Studio. Do the pictures match the words? Is any fact obviously wrong?
If something's wrong: `The video "<title>" has this problem: <describe>. Take it back from the schedule safely (withdraw, don't delete) and explain what you did.`

**Weekly:**

> Summarize this week: best and worst videos with views, which posting times work best, recurring problems, and 3 concrete suggestions to grow. Then show me exactly what you'd change before changing anything.

---

## 9. When something goes wrong

| You see | Meaning | What to do |
|---|---|---|
| "503", "overloaded", "Deferred" | Google's free AI was busy | Nothing. The next run retries |
| Run OK but 0 videos | Fact-check rejected the scripts (that's good), or the AI was busy | Normal on some days. 3+ days in a row: ask Claude why |
| "quota" | YouTube's daily limit | Nothing; it resets daily |
| "invalid_grant", "token expired", "auth" | Your YouTube login expired | Ask Claude to redo the login (step 6), then update the GitHub secret (step 7) |
| Run started late | GitHub's timer is often late | Fine; uploads are scheduled ahead |

**Emergency stop:** GitHub → **Actions → Daily video → "..." → Disable workflow**. Enable it again the same way. Videos already scheduled on YouTube still go out; set one to **Private** in YouTube Studio to stop it.

**Any error you don't understand:** copy the red text and ask: `Explain this error in simple words and tell me if I need to do anything: <paste error>`. Make sure it contains no keys.

---

## 10. Learn as you go: useful prompts

- `Explain how this project decides what topic to make next, like I'm 12.`
- `What happens to a script from the moment it's written until it's uploaded? Simple steps.`
- `Change the voice to a female British voice and make a test video.`
- `Make the captions bigger and yellow. Show me a test frame.`
- `Switch the main channel to Hindi and make a dry-run video.`
- `Post at the best times for viewers in the US. What times do you suggest and why?`
- `Suggest 10 topic ideas for my channel. Don't add them until I approve.`
- `Add these approved topics to the queue: <list>.`
- `My views are low. Read the analytics and suggest what to change, with reasons.`
- Before any push to GitHub: `Does this change contain any key, token, password or personal data?` It must say **no**.

You're set. Good luck with your channel! 🚀
