"""pyglocal CLI — unified Pythonic toolchain for the glocal constellation.

Probe-verified: offline-first, offline.backend, HTML/CSS/Rust/WASM primary,
remote APIs optional, local files default.

Usage:
    pyglocal kænbæn create "intent" --assignee imperial|vice|reviewer
    pyglocal kænbæn status
    pyglocal kænbæn dispatch --max 1
    pyglocal kænbæn done k001 --evidence "..."
    pyglocal kænbæn stats

    pyglocal fleet offer           # all-in-one QR
    pyglocal fleet probe           # probe nodes
    pyglocal fleet qr              # print QR payload

    pyglocal ollama probe          # ping :11434
    pyglocal ollama bake           # pull+bake llama3.2:3b

    pyglocal mp4 build             # build local_agent.mp4
    pyglocal mp4 render            # render local HTML fallback

    pyglocal png gen "payload"     # PNG receipt
    pyglocal png penguin           # PNG penguin glyph

    pyglocal html pacelet "title"  # pacelet writer
    pyglocal html render           # local HTML fallback

    pyglocal sticky write          # write to Sticky Notes LocalState
    pyglocal sticky open           # open glocal window in Sticky Notes
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python pyglocal/cli.py` to import pyglocal from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pyglocal.kabban as k
import pyglocal.crypto as c
import pyglocal.fleet as f
import pyglocal.ollama_cpu as o
import pyglocal.mp4_gen as m
import pyglocal.png_gen as p
import pyglocal.html_gen as h
import pyglocal.winsticky as w


def cmd_kabban(args):
    if args.sub == "create":
        t = k.new_task(args.intent, args.assignee)
        print("created {} (assignee: {})".format(t["id"], t["assignee"]))
    elif args.sub == "list":
        for t in k.list_tasks():
            print("{} [{}] {} -> {}".format(t["id"], t["status"], t["assignee"], t["intent"]))
    elif args.sub == "start":
        t = k.start(args.tid)
        print("started" if t else "not found", t["id"] if t else "")
    elif args.sub == "done":
        t = k.done(args.tid, args.evidence)
        print("done" if t else "not found", t["id"] if t else "")
    elif args.sub == "block":
        t = k.block(args.tid, args.reason)
        print("blocked" if t else "not found", t["id"] if t else "")
    elif args.sub == "unblock":
        t = k.unblock(args.tid)
        print("unblocked" if t else "not found", t["id"] if t else "")
    elif args.sub == "dormant":
        t = k.dormant(args.tid)
        print("dormant" if t else "not found", t["id"] if t else "")
    elif args.sub == "reroute":
        t = k.reroute(args.tid, args.new)
        print("reroute" if t else "not found", t["id"] if t else "")
    elif args.sub == "dep":
        if args.op == "add":
            k.dep_add(args.child, args.parent)
            print("dep added")
        else:
            k.dep_remove(args.child, args.parent)
            print("dep removed")
    elif args.sub == "dispatch":
        max_tasks = args.max_tasks if args.max_tasks else args.max_tasks_opt or 1
        ready = k.dispatch(max_tasks)
        print("dispatched:", [t["id"] for t in ready] if ready else "none")
    elif args.sub == "stats":
        s = k.stats()
        print(json_dumps(s))
    elif args.sub == "status":
        print(json_dumps({"node": k.SYSTEM["node"], "offline": k.SYSTEM["offline"], "qr": k.SYSTEM["qr"]}))


def cmd_fleet(args):
    if args.sub == "offer":
        print(f.all_in_one_qr())
    elif args.sub == "probe":
        for n in f.probe_nodes():
            print(json_dumps(n))
    elif args.sub == "qr":
        print(f.all_in_one_qr())
    elif args.sub == "nodes":
        for n in f.fleet_nodes():
            print(json_dumps(n))


def cmd_ollama(args):
    if args.sub == "probe":
        print(json_dumps(o.ping()))
    elif args.sub == "bake":
        print(json_dumps(o.generation()))
    elif args.sub == "chat":
        print(json_dumps(o.chat(args.prompt)))


def cmd_mp4(args):
    if args.sub == "build":
        r = m.build()
        print(json_dumps(r))
    elif args.sub == "render":
        print(json_dumps(m.render()))


def cmd_png(args):
    if args.sub == "gen":
        path = args.path or (Path("receipts") / ("{}.png".format(args.id)))
        im = p.receipt({"id": args.id, "verdict": args.verdict})
        im.save(str(path))
        print("wrote", path)
    elif args.sub == "penguin":
        im = p.penguin(args.payload)
        im.save("penguin.png")
        print("wrote penguin.png")


def cmd_html(args):
    if args.sub == "pacelet":
        p = h.pacelet(args.title, args.body)
        print("wrote", p)
    elif args.sub == "render":
        print(json_dumps(h.render()))


def cmd_sticky(args):
    if args.sub == "write":
        print(json_dumps(w.write()))
    elif args.sub == "open":
        print(json_dumps(w.open_sn()))
    elif args.sub == "probe":
        print(json_dumps(w.probe()))


def json_dumps(obj: dict | list) -> str:
    import json as _json
    return _json.dumps(obj, indent=2, ensure_ascii=False)


def main(argv=None):
    # Allow `python pyglocal/cli.py` to import pyglocal from repo root
    import sys as _sys
    from pathlib import Path as _P
    REPO_ROOT = _P(__file__).resolve().parent.parent
    if str(REPO_ROOT) not in _sys.path:
        _sys.path.insert(0, str(REPO_ROOT))

    ap = argparse.ArgumentParser(prog="pyglocal", description="pythonic toolchains for the glocal constellation")
    sub = ap.add_subparsers(dest="command", required=True)

    # kabban
    kb = sub.add_parser("kabban", help="kænbæn task board")
    kb.add_argument("sub", choices=["create", "list", "show", "start", "done", "block", "unblock", "dormant", "reroute", "dep", "dispatch", "stats", "status"])
    kb.add_argument("intent", nargs="?", default="")
    kb.add_argument("assignee", nargs="?", default="self")
    kb.add_argument("tid", nargs="?", default="")
    kb.add_argument("evidence", nargs="?", default="")
    kb.add_argument("reason", nargs="?", default="")
    kb.add_argument("child", nargs="?", default="")
    kb.add_argument("parent", nargs="?", default="")
    kb.add_argument("new", nargs="?", default="self")
    kb.add_argument("max_tasks", type=int, nargs="?", default=None)
    kb.add_argument("--max-tasks", type=int, dest="max_tasks_opt", default=None)
    kb.set_defaults(func=cmd_kabban)

    # fleet
    fl = sub.add_parser("fleet", help="FleetWave all-in-one QR")
    fl.add_argument("sub", choices=["offer", "probe", "qr", "nodes"])
    fl.set_defaults(func=cmd_fleet)

    # ollama
    ol = sub.add_parser("ollama", help="Ollama CPU brain")
    ol.add_argument("sub", choices=["probe", "bake", "chat"])
    ol.add_argument("prompt", nargs="?", default="probe")
    ol.set_defaults(func=cmd_ollama)

    # mp4
    mp = sub.add_parser("mp4", help="constellation MP4")
    mp.add_argument("sub", choices=["build", "render"])
    mp.set_defaults(func=cmd_mp4)

    # png
    pn = sub.add_parser("png", help="PNG receipts")
    pn.add_argument("sub", choices=["gen", "penguin"])
    pn.add_argument("payload", nargs="?", default="probe")
    pn.add_argument("id", nargs="?", default="receipt")
    pn.add_argument("path", nargs="?", default="")
    pn.set_defaults(func=cmd_png)

    # html
    ht = sub.add_parser("html", help="HTML/CSS pacelets")
    ht.add_argument("sub", choices=["pacelet", "render"])
    ht.add_argument("title", nargs="?", default="pacelet")
    ht.add_argument("body", nargs="?", default="")
    ht.set_defaults(func=cmd_html)

    # sticky
    st = sub.add_parser("sticky", help="Sticky Notes integration")
    st.add_argument("sub", choices=["write", "open", "probe"])
    st.set_defaults(func=cmd_sticky)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
