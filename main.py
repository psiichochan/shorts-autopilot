"""Cosmic Scale: faceless Shorts pipeline. Command line over pipeline/orchestrator.py.

Daily operation
  python main.py daily                  # what the scheduler runs: sync → uploads → make videos for free slots
                                        #   → uploads → comments → analytics + dashboard (reports/daily-*.md)
  python main.py status                 # queue, slots, alerts, readiness at a glance
  python main.py approve output/<folder> | --all     # approve videos (uploads into their slot)
  python main.py reject output/<folder> --note "..."  # turn one down; the slot gets a replacement
  python main.py withdraw output/<folder> --note "..." # pull a SCHEDULED upload: kept private, no publish time
  python main.py reschedule output/<folder> | --over-cap   # move a scheduled private upload to the next free slot;
                                        #   --over-cap moves every one beyond schedule.videos_per_day on its day
  touch STOP                            # kill switch: no new work or publishing until you delete STOP
  python main.py daily --dry-run        # everything except uploads, deletes and comments

Production
  python main.py ideas                  # brainstorm + score topics into data/topics.json
  python main.py calendar [--fill]      # 30-day plan → reports/[<id>/]CONTENT_CALENDAR.md (--fill brainstorms enough topics)
  python main.py make [--topic "..."] [--count N]   # make videos (gated), not uploaded
  python main.py rerender output/<folder>           # re-render an edited script.json
  python main.py add-music output/<folder> | --all [--replace]
                                        # mix background music under videos made without it (same picture);
                                        #   --replace also swaps already-scheduled private uploads on YouTube
  python main.py veo-prompts            # Veo hook-clip prompts for the next topics

Publishing
  python main.py publish output/<folder> [--force]  # upload one ready video into its slot
  python main.py crosspost              # post Shorts that went public on YouTube as Instagram Reels (if enabled)
  python main.py upload-pending         # upload every ready video (bounded by limits/quota)
  python main.py sync                   # confirm scheduled → published with YouTube

Measurement
  python main.py report | weekly        # dashboards in reports/
  python main.py quality [--count DAYS] # content gates, failure classes, claim/visual rates, model usage (default 7)
  python main.py inspect output/<folder>  # one video's claim ledger, citations, visual grounding, verification state
  python main.py comments               # read viewer comments now + what the comments agent learned from them

Setup
  python main.py auth-youtube | auth-analytics | channel-setup | refresh-instagram

Channels (docs/MULTI_CHANNEL.md)
  python main.py channels                         # list profiles and check they share no identity/credentials
  python main.py --channel clips <command>        # any command above, on another channel (default: config.yaml's)
  Clip channel only:
  python main.py --channel clips discover         # find sources (NASA library, inbox, optional YouTube leads)
  python main.py --channel clips sources          # registry with rights status; the manual review queue
  python main.py --channel clips rights-approve '<source id>' --reviewer NAME [--note "..."]
  python main.py --channel clips rights-reject '<source id>' --reviewer NAME --note "why"
  python main.py --channel clips revoke '<source id>' --note "permission withdrawn ..."
  python main.py --channel clips add-source path/to/video.mp4 --rights rights.yaml [--srt captions.srt]
"""
import argparse
import contextlib
import sys
from pathlib import Path

from pipeline import channels, control
from pipeline.util import load_env, slugify

COMMANDS = ["daily", "status", "approve", "reject", "ideas", "calendar", "make", "rerender", "veo-prompts", "publish",
            "upload-pending",
            "sync", "report", "weekly", "auth-youtube", "auth-analytics", "channel-setup",
            "refresh-instagram", "auto", "channels", "discover", "sources", "rights-approve", "rights-reject",
            "revoke", "add-source", "comments", "crosspost", "add-music", "withdraw", "reschedule", "quality", "inspect"]
# commands that change the queue/registry take the channel's lock (a second concurrent run exits)
MUTATING = {"daily", "auto", "approve", "reject", "make", "rerender", "publish", "upload-pending", "sync", "discover",
            "rights-approve", "rights-reject", "revoke", "add-source", "comments", "crosspost", "add-music",
            "withdraw", "reschedule"}
GENERATED_ONLY = {"ideas", "calendar", "rerender", "veo-prompts", "refresh-instagram", "add-music"}
CLIPS_ONLY = {"discover", "sources", "rights-approve", "rights-reject", "revoke", "add-source"}


def status(cfg):
    from pipeline import jobs, analytics
    all_jobs = jobs.load()
    print(f"\nKill switch: {'ON' if control.STOP_FILE.exists() or cfg.get('control', {}).get('kill_switch') else 'off'}")
    print("\nQueue:")
    for j in sorted(all_jobs, key=lambda j: (jobs.when(j) or jobs.now()).isoformat()):
        if j["status"] == "deleted":
            continue
        w = jobs.when(j)
        print(f"  {j['status']:<12} {w.strftime('%a %d %b %H:%M') if w else '-':<16} {j.get('role') or '-':<10} "
              f"{j['topic'][:44]:<44} {j.get('youtube_id') or ''} {('⚠ ' + j['alert']) if j.get('alert') else ''}")
    free = jobs.free_slots(cfg, all_jobs, cfg["schedule"].get("buffer_days", 2))
    print(f"\nFree slots in the next {cfg['schedule'].get('buffer_days', 2)} days: "
          + (", ".join(f"{s:%a %H:%M}" for s in free) or "none"))
    from pipeline import orchestrator as orch
    waiting = orch.awaiting(all_jobs)
    if waiting:
        print(f"\n{len(waiting)} video(s) AWAITING YOUR APPROVAL — watch video.mp4 and read post.txt, then:")
        for j in waiting:
            w = jobs.when(j)  # a rerendered video awaiting approval may have no slot yet (approve picks one)
            print(f"  {w.strftime('%a %d %b %H:%M') if w else 'next free slot':<16}  "
                  f"python main.py approve output/{j['folder']}")
        print('  (or: python main.py approve --all    |   python main.py reject output/<folder> --note "why")')
    r = analytics.readiness(cfg)
    print(f"\nSubscribers (last snapshot): {r['subscribers']} / {r['thresholds'].get('subscribers', '?')}")


def sources_table(cfg):
    from pipeline.clips import registry
    srcs = sorted(registry.sources(cfg).values(), key=lambda s: (s["status"], -s.get("score", 0)))
    for s in srcs:
        rv = s.get("review") or {}
        print(f"  {s['status']:<14} {s.get('score', 0):<5} {s['id'][:60]:<60} {s.get('title', '')[:40]}")
        for reason in rv.get("hard", []):
            print(f"      ✗ {reason}")
        for reason in rv.get("soft", []) if s["status"] == "manual_review" else []:
            print(f"      ? {reason}")
    print(f"\n{len(srcs)} source(s). Approve after checking: python main.py --channel {cfg['channel']['id']} "
          f"rights-approve '<id>' --reviewer <you>")


def main():
    load_env()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=COMMANDS)
    ap.add_argument("--channel", help="channel profile id (default: config.yaml's channel; see `channels`)")
    ap.add_argument("--reviewer", help="rights decisions: who decided")
    ap.add_argument("--rights", help="add-source: YAML file with the source's rights record")
    ap.add_argument("--srt", help="add-source: captions file (.srt/.vtt)")
    ap.add_argument("--title")
    ap.add_argument("--creator")
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--topic")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--force", action="store_true", help="publish even if the job didn't pass the gates")
    ap.add_argument("--dry-run", action="store_true", help="no uploads, deletes or comments")
    ap.add_argument("--fill", action="store_true", help="calendar: brainstorm topics until 30 days are covered")
    ap.add_argument("--all", action="store_true", help="approve: every video awaiting approval; add-music: every "
                                                       "queued video without music")
    ap.add_argument("--over-cap", action="store_true", help="reschedule: every scheduled upload beyond the daily target")
    ap.add_argument("--replace", action="store_true", help="add-music: also replace scheduled (still private) uploads")
    ap.add_argument("--note")
    a = ap.parse_args()
    control.DRY_RUN = a.dry_run
    if a.cmd == "channels":
        channels.validate_all()
        for cid in channels.available():
            c = channels.load(cid)
            print(f"  {cid:<10} {c['channel'].get('type', 'generated'):<10} {c['channel']['name']:<32} "
                  f"yt={c['channel'].get('youtube_channel_id') or '(not linked)':<26} "
                  f"{c['schedule']['videos_per_day']}/day uploads={'on' if c['youtube'].get('enabled') else 'off'}")
        print("OK: no two channels share a YouTube channel id, token file, token variable or data folder.")
        return
    cfg = channels.activate(channels.load(a.channel))
    kind = cfg["channel"].get("type", "generated")
    if kind == "clips" and a.cmd in GENERATED_ONLY or kind != "clips" and a.cmd in CLIPS_ONLY:
        sys.exit(f"'{a.cmd}' isn't available for {kind} channel '{cfg['channel']['id']}'")

    from pipeline import orchestrator as orch
    from pipeline.clips import orchestrator as clips
    if a.cmd in ("daily", "auto"):
        # Run watchdog: a stalled network read once held the channel lock for 13 h and blocked every later run.
        # On expiry it dumps every thread's stack to the log and exits; the OS releases the flock, writes are
        # atomic, and an interrupted upload is reconciled by the next run.
        watchdog(cfg.get("control", {}).get("max_run_minutes", 180) * 60)
    with channels.lock(cfg) if a.cmd in MUTATING else contextlib.nullcontext():
        try:
            run(a, cfg, kind, orch, clips)
        finally:
            control.write_usage(a.cmd)


def watchdog(seconds):
    """Wall-clock run limit. faulthandler's own timer uses a clock that stops while the Mac sleeps (a run passed
    7 h with the 3 h limit unfired), so this thread checks time.time() and, on expiry, dumps every thread's stack to
    the log and exits. The OS releases the flock, writes are atomic, and an interrupted upload is reconciled next run."""
    import faulthandler
    import os
    import threading
    import time
    deadline = time.time() + seconds

    def watch():
        while time.time() < deadline:
            time.sleep(30)
        print(f"watchdog: run exceeded {seconds // 60} min (wall clock); stopping", flush=True)
        faulthandler.dump_traceback(all_threads=True)
        os._exit(3)
    threading.Thread(target=watch, daemon=True, name="watchdog").start()


def run(a, cfg, kind, orch, clips):
    if a.cmd in ("daily", "auto"):
        clips.daily(cfg) if kind == "clips" else orch.daily(cfg, force=a.force)
    elif a.cmd == "quality":
        from pipeline import quality
        print("\n".join(quality.report_lines(cfg, a.count if a.count > 1 else 7)))
    elif a.cmd == "inspect":
        from pipeline import quality
        if not a.folder:
            sys.exit("usage: python main.py inspect output/<folder>")
        print(quality.inspect(Path(a.folder).name))
    elif a.cmd == "status":
        status(cfg)
    elif a.cmd == "approve":
        folders = [j["folder"] for j in orch.awaiting()] if a.all else [Path(a.folder).name] if a.folder else []
        if not folders:
            sys.exit("usage: python main.py approve output/<folder>   |   python main.py approve --all")
        orch.approve(cfg, folders)
    elif a.cmd == "reject":
        if not a.folder:
            sys.exit('usage: python main.py reject output/<folder> --note "why"')
        orch.reject(cfg, Path(a.folder).name, a.note or "")
    elif a.cmd == "withdraw":
        if not a.folder:
            sys.exit('usage: python main.py withdraw output/<folder> --note "why"')
        orch.withdraw(cfg, Path(a.folder).name, a.note or "")
    elif a.cmd == "reschedule":
        folders = [j["folder"] for j in orch.over_cap(cfg)] if a.over_cap else [Path(a.folder).name] if a.folder else []
        if not folders:
            sys.exit("nothing to move" if a.over_cap else
                     "usage: python main.py reschedule output/<folder>   |   python main.py reschedule --over-cap")
        for f in folders:
            orch.reschedule(cfg, f, a.note or "")
    elif a.cmd == "ideas":
        from pipeline import ideas
        for t in ideas.refill_backlog(cfg):
            print(f"- [{t.get('score', '?')}] ({t.get('role', '?')}) {t['topic']}")
    elif a.cmd == "calendar":
        from pipeline import calendar_plan
        calendar_plan.build(cfg, fill=a.fill)
    elif a.cmd == "make":
        if control.killed(cfg):
            return
        for _ in range(a.count):
            if kind == "clips":
                clips.prepare_candidates(cfg, a.count)
                if not clips.make_short(cfg, segment_id=a.topic):
                    print("no rights-cleared candidate segment (see: sources)")
                    break
            else:
                orch.make_video(cfg, topic=a.topic)
    elif a.cmd == "rerender":
        import json
        if not a.folder:
            sys.exit("usage: python main.py rerender output/<folder>   (after editing its script.json)")
        orch.make_video(cfg, script=json.loads((Path(a.folder) / "script.json").read_text(encoding="utf-8")))
    elif a.cmd == "veo-prompts":
        from pipeline import ideas
        lines = [f"SAVE AS:  assets/veo/{slugify(t['topic'])}.mp4\nTOPIC:    {t['topic']}\n"
                 f"PROMPT:   {t.get('veo_prompt', '(no prompt)')}\n" for t in ideas.peek(a.count if a.count > 1 else 7)]
        out = cfg["_paths"]["output"]
        out.mkdir(exist_ok=True)
        (out / "veo_prompts.txt").write_text("\n".join(lines), encoding="utf-8")
        print("\n".join(lines))
    elif a.cmd == "publish":
        if not a.folder:
            sys.exit("usage: python main.py publish output/<folder>")
        if not control.killed(cfg):
            orch.publish(cfg, Path(a.folder).name, a.force)
    elif a.cmd == "upload-pending":
        if not control.killed(cfg):
            orch.upload_pending(cfg)
    elif a.cmd == "sync":
        orch.sync_status(cfg)
    elif a.cmd == "report":
        from pipeline import analytics
        analytics.snapshot(cfg)
        print(analytics.write_daily_report(cfg).read_text())
    elif a.cmd == "comments":
        from pipeline import comments
        comments.analyse(cfg)
        print("\n".join(comments.report_lines(cfg)) or "no public Shorts with comments yet")
    elif a.cmd == "add-music":
        folders = ([j["folder"] for j in orch.jobs.load() if j["status"] in orch.MUSIC_FIXABLE
                    and (not j.get("music") or j.get("music_not_uploaded"))]
                   if a.all else [Path(a.folder).name] if a.folder else [])
        if not folders:
            sys.exit("usage: python main.py add-music output/<folder> | --all  [--replace]")
        if not control.killed(cfg):
            for f in folders:
                orch.add_music(cfg, f, replace=a.replace)
    elif a.cmd == "crosspost":
        if not control.killed(cfg):
            orch.crosspost(cfg)
    elif a.cmd == "weekly":
        from pipeline import analytics
        analytics.fetch_video_analytics(cfg)
        print(analytics.write_weekly_report(cfg).read_text())
    elif a.cmd == "auth-youtube":
        from pipeline import publish_youtube
        publish_youtube.authorize()
    elif a.cmd == "auth-analytics":
        from pipeline import analytics
        analytics.authorize()
    elif a.cmd == "channel-setup":
        from pipeline import channel
        channel.update_branding(cfg)
        if cfg.get("channel_profile", {}).get("banner"):
            channel.upload_banner(Path(cfg["channel_profile"]["banner"]))
        if cfg["youtube"].get("playlist"):
            channel.ensure_playlist(cfg["youtube"]["playlist"])
    elif a.cmd == "refresh-instagram":
        from pipeline import publish_instagram
        publish_instagram.refresh_token(cfg)
    elif a.cmd == "discover":
        from pipeline.clips import discovery
        discovery.run(cfg)
    elif a.cmd == "sources":
        sources_table(cfg)
    elif a.cmd in ("rights-approve", "rights-reject", "revoke"):
        from pipeline.clips import rights
        if not a.folder:
            sys.exit(f"usage: python main.py --channel {cfg['channel']['id']} {a.cmd} '<source id>' ...")
        if a.cmd == "rights-approve":
            rights.approve(cfg, a.folder, a.reviewer, a.note or "")
        elif a.cmd == "rights-reject":
            rights.reject(cfg, a.folder, a.reviewer, a.note or "")
        else:
            rights.revoke(cfg, a.folder, a.note or "revoked")
    elif a.cmd == "add-source":
        import yaml
        from pipeline.clips import ingest, registry
        if not (a.folder and a.rights):
            sys.exit("usage: python main.py --channel clips add-source video.mp4 --rights rights.yaml [--srt x.srt]")
        meta = yaml.safe_load(Path(a.rights).read_text(encoding="utf-8")) or {}
        sid = ingest.register_file(cfg, a.folder, meta.get("rights") or meta, a.title or meta.get("title") or
                                   Path(a.folder).stem, a.creator or meta.get("creator", "unknown"), a.srt,
                                   meta.get("url"))
        print(f"registered {sid}: {registry.get(cfg, sid)['status']}")


if __name__ == "__main__":
    main()
