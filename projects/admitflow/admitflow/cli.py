"""Command-line interface: `admitflow import|list|search|stats|export`."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional

from . import store
from .dedupe import dedupe
from .importers import FORMATS, import_file
from .models import Lead


def _print_leads(leads: List[Lead]) -> None:
    for lead in leads:
        contact = lead.email or lead.phone or "(no contact)"
        print(
            f"{lead.lead_id:<12} {lead.received_at:%Y-%m-%d}  {lead.name:<28} "
            f"{(lead.course or '-'):<24} {'+'.join(lead.sources):<16} {contact}"
        )
    print(f"\n{len(leads)} lead(s)")


def cmd_import(args: argparse.Namespace) -> int:
    path = store.store_path()
    existing = store.load(path)
    incoming: List[Lead] = []
    for fmt in FORMATS:
        for file in getattr(args, fmt) or []:
            result = import_file(Path(file), fmt)
            print(f"{file}: {len(result.leads)} imported, {len(result.rejected)} rejected")
            for line_num, reason in result.rejected:
                print(f"  line {line_num}: {reason}", file=sys.stderr)
            incoming.extend(result.leads)
    if not incoming:
        print("nothing to import: pass --website, --ads or --walkins", file=sys.stderr)
        return 2
    unique, merged = dedupe(existing + incoming)
    store.save(path, unique)
    added = len(unique) - len(existing)
    print(f"{merged} duplicate(s) merged; {added} new; {len(unique)} unique lead(s) saved to {path}")
    return 0


def _filtered(args: argparse.Namespace) -> List[Lead]:
    leads = store.load(store.store_path())
    if getattr(args, "source", None):
        leads = [lead for lead in leads if args.source.lower() in lead.sources]
    if getattr(args, "course", None):
        leads = [lead for lead in leads if lead.course and args.course.casefold() in lead.course.casefold()]
    return leads


def cmd_list(args: argparse.Namespace) -> int:
    _print_leads(_filtered(args))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    _print_leads([lead for lead in store.load(store.store_path()) if lead.matches(args.text)])
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    leads = store.load(store.store_path())
    print(f"Unique leads: {len(leads)}")
    print(f"Enquired through more than one channel: {sum(1 for lead in leads if len(lead.sources) > 1)}")
    print(f"No usable contact details: {sum(1 for lead in leads if not (lead.email or lead.phone))}")
    print("\nBy channel (a lead counts once per channel it used):")
    for source, count in Counter(s for lead in leads for s in lead.sources).most_common():
        print(f"  {source:<10} {count}")
    print("\nBy course:")
    for course, count in Counter(lead.course or "(unknown)" for lead in leads).most_common():
        print(f"  {course:<26} {count}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    leads = _filtered(args)
    store.export_csv(Path(args.output), leads)
    print(f"Exported {len(leads)} lead(s) to {args.output}")
    return 0


def cmd_create_user(args: argparse.Namespace) -> int:
    import getpass

    from .auth import hash_password
    from .models import User

    password = args.password or getpass.getpass(f"Password for {args.username}: ")
    if len(password) < 12:
        print("error: use a password of at least 12 characters", file=sys.stderr)
        return 2
    from .repository import default_repository

    default_repository().save_user(User(args.username, args.full_name, args.role, hash_password(password)))
    print(f"Saved {args.role} {args.username}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:  # pragma: no cover - starts a long-running server
    import uvicorn

    from .api import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


def _sql_repo():
    import os

    from .db import SqlRepository

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("error: set DATABASE_URL (e.g. sqlite:///admitflow.db) and run `alembic upgrade head` first")
    return SqlRepository(url)


def cmd_ingest(args: argparse.Namespace) -> int:
    from .pipeline import ingest

    repo = _sql_repo()
    ran = False
    for fmt in FORMATS:
        for file in getattr(args, fmt) or []:
            print(ingest(repo, Path(file), fmt, force=args.force))
            ran = True
    if not ran:
        print("nothing to ingest: pass --website, --ads or --walkins", file=sys.stderr)
        return 2
    return 0


def cmd_match_admissions(args: argparse.Namespace) -> int:
    from .pipeline import match_admissions

    report = match_admissions(_sql_repo(), Path(args.file))
    print(f"matched {report.matched}, already matched {report.already_matched}, unmatched {len(report.unmatched)}")
    for student_no, reason in report.unmatched:
        print(f"  {student_no}: {reason}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from .pipeline import conversion_by_channel

    print(f"{'channel':<10} {'leads':>6} {'enrolled':>9} {'conversion':>11}")
    for row in conversion_by_channel(_sql_repo()):
        print(f"{row['channel']:<10} {row['leads']:>6} {row['enrolled']:>9} {row['conversion']:>10.1%}")
    return 0


def cmd_train_model(args: argparse.Namespace) -> int:
    import warnings

    from .scoring import conversion_by_response_time, save, train

    warnings.filterwarnings("ignore", category=RuntimeWarning)  # harmless BLAS warnings on some Macs
    result = train(Path(args.history))
    print(f"trained on {result.train_rows} leads (2024 intake), tested on {result.test_rows} (2025 intake)\n")
    print(f"{'':<10} {'ROC AUC':>8} {'prec@20%':>9} {'Brier':>7}")
    for name, m in result.metrics.items():
        print(f"{name:<10} {m['roc_auc']:>8} {m['precision_at_20pct']:>9} {m['brier']:>7}")
    print(f"\nbase rate (test): {result.metrics['model']['base_rate']}")
    print("\nenrolment rate by time to first contact (descriptive, all history):")
    for row in conversion_by_response_time(Path(args.history)):
        print(f"  {row['bucket']:<14} {row['leads']:>5} leads  {row['rate']:.1%}")
    save(result, Path(args.out))
    print(f"\nsaved {args.out} (+ .json metadata)")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    from .assistant import build_assistant

    assistant = build_assistant(args.docs, args.llm)
    if assistant is None:
        print(f"error: no course documents found in {args.docs}", file=sys.stderr)
        return 1
    answer, hits = assistant.ask(args.question)
    print(answer.text)
    print("\nretrieved: " + ", ".join(f"{h.chunk.chunk_id} ({h.score})" for h in hits))
    return 0


def cmd_eval_assistant(args: argparse.Namespace) -> int:
    import json

    from .assistant import build_assistant
    from .evals import evaluate, load_cases

    assistant = build_assistant(args.docs, args.llm)
    if assistant is None:
        print(f"error: no course documents found in {args.docs}", file=sys.stderr)
        return 1
    report = evaluate(load_cases(Path(args.cases)), assistant.retriever, assistant.answerer)
    failures = report.pop("failures")
    print(json.dumps(report, indent=2))
    for failure in failures:
        print(f"FAIL {failure['id']} {failure['question']!r}: {'; '.join(failure['reasons'])}")
    if args.min_correct is not None and report["correct"] < args.min_correct:
        print(f"\ncorrect {report['correct']} is below the required {args.min_correct}", file=sys.stderr)
        return 1
    return 0


def _senders_from_env(dry_run: bool):
    from .integrations.messaging import RecordingSender, SmtpEmailSender, WhatsAppCloudSender

    if dry_run:
        recorder = RecordingSender()
        return {"email": recorder, "whatsapp": recorder}, recorder
    senders = {}
    if os.environ.get("SMTP_HOST"):
        senders["email"] = SmtpEmailSender(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587")),
                                           os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"],
                                           os.environ["SMTP_FROM"])
    if os.environ.get("WHATSAPP_TOKEN"):
        senders["whatsapp"] = WhatsAppCloudSender(os.environ["WHATSAPP_API_URL"], os.environ["WHATSAPP_TOKEN"],
                                                  os.environ["WHATSAPP_PHONE_NUMBER_ID"])
    return senders, None


def cmd_send_approved(args: argparse.Namespace) -> int:
    from .integrations.messaging import send_approved
    from .repository import default_repository

    senders, recorder = _senders_from_env(args.dry_run)
    report = send_approved(default_repository(), senders)
    print(f"sent {len(report.sent)}, failed {len(report.failed)}, skipped {len(report.skipped)}")
    for draft_id, reason in report.failed + report.skipped:
        print(f"  {draft_id}: {reason}")
    if recorder:
        for message in recorder.sent:
            print(f"\n[dry run] to {message['to']}: {message['subject']}\n{message['body']}")
    return 1 if report.failed else 0


def cmd_crm_sync(args: argparse.Namespace) -> int:
    from .integrations.crm import CrmClient, sync_leads
    from .repository import default_repository

    if not (os.environ.get("CRM_BASE_URL") and os.environ.get("CRM_TOKEN")):
        print("error: set CRM_BASE_URL and CRM_TOKEN", file=sys.stderr)
        return 2
    report = sync_leads(default_repository(), CrmClient(os.environ["CRM_BASE_URL"], os.environ["CRM_TOKEN"]))
    print(f"created {len(report.created)}, linked {len(report.linked)}, updated {len(report.updated)}, "
          f"skipped {len(report.skipped)}, failed {len(report.failed)}")
    for lead_id, reason in report.failed:
        print(f"  FAILED {lead_id}: {reason}")
    return 1 if report.failed else 0


def cmd_mcp(args: argparse.Namespace) -> int:  # pragma: no cover - runs until the client disconnects
    from .mcp_server import build_server

    build_server(user=args.user).run("stdio")
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    """Consistent online backup of a SQLite database. For PostgreSQL use pg_dump (see the runbook)."""
    import sqlite3

    url = os.environ.get("DATABASE_URL", "")
    if not url.startswith("sqlite:///"):
        print("For PostgreSQL run:  pg_dump --format=custom --file=admitflow.dump \"$DATABASE_URL\"  (runbook: BACKUP)",
              file=sys.stderr)
        return 2
    source = sqlite3.connect(url[len("sqlite:///"):])
    target = sqlite3.connect(args.to)
    with target:
        source.backup(target)        # safe while the app is running, unlike copying the file
    source.close()
    target.close()
    print(f"backed up to {args.to}")
    return cmd_verify_backup(argparse.Namespace(path=args.to))


def cmd_verify_backup(args: argparse.Namespace) -> int:
    """A backup you haven't restored is a hope, not a backup: open it and check it."""
    import sqlite3

    db = sqlite3.connect(args.path)
    ok = db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    counts = {t: db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables if t != "alembic_version"}
    print(f"integrity: {'ok' if ok else 'FAILED'}")
    for table, count in counts.items():
        print(f"  {table:<16} {count}")
    return 0 if ok and "leads" in counts else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="admitflow", description="AdmitFlow lead manager")
    parser.add_argument("-v", "--verbose", action="store_true", help="show warnings while importing")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("import", help="import and deduplicate leads from channel exports")
    for fmt in FORMATS:
        p.add_argument(f"--{fmt}", action="append", metavar="FILE", help=f"{fmt} export (CSV)")
    p.set_defaults(func=cmd_import)

    for name, func, helptext in (("list", cmd_list, "list leads"), ("export", cmd_export, "export leads to CSV")):
        p = sub.add_parser(name, help=helptext)
        if name == "export":
            p.add_argument("output", help="CSV file to write")
        p.add_argument("--source", help="only leads from this channel, e.g. whatsapp")
        p.add_argument("--course", help="only leads for courses containing this text")
        p.set_defaults(func=func)

    p = sub.add_parser("search", help="search by name, email, phone, course or ID")
    p.add_argument("text")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("stats", help="summary counts")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("create-user", help="add or update a counsellor/admin login (Module 04)")
    p.add_argument("username")
    p.add_argument("--full-name", required=True)
    p.add_argument("--role", choices=["counsellor", "admin"], default="counsellor")
    p.add_argument("--password", help="omit to be prompted (recommended: keeps it out of shell history)")
    p.set_defaults(func=cmd_create_user)

    p = sub.add_parser("ingest", help="load exports into the SQL database, with an audit trail (Module 05)")
    for fmt in FORMATS:
        p.add_argument(f"--{fmt}", action="append", metavar="FILE")
    p.add_argument("--force", action="store_true", help="reload files that were already loaded")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("match-admissions", help="mark leads as enrolled from the SIS export (Module 05)")
    p.add_argument("file")
    p.set_defaults(func=cmd_match_admissions)

    p = sub.add_parser("report", help="leads and enrolments by channel (Module 05)")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("train-model", help="train the lead-scoring model on past intakes (Module 07)")
    p.add_argument("history", help="e.g. data/historical_leads.csv")
    p.add_argument("--out", default="models/lead_score.joblib")
    p.set_defaults(func=cmd_train_model)

    for name, func, helptext in (("ask", cmd_ask, "ask the course assistant a question (Module 08)"),
                                 ("eval-assistant", cmd_eval_assistant, "run the assistant evaluation set (Module 08)")):
        p = sub.add_parser(name, help=helptext)
        if name == "ask":
            p.add_argument("question")
        else:
            p.add_argument("--cases", default="data/eval/assistant_eval.jsonl")
            p.add_argument("--min-correct", type=float, help="exit 1 if the correct rate is below this (for CI)")
        p.add_argument("--docs", default="data/course_docs")
        p.add_argument("--llm", default=os.environ.get("ADMITFLOW_LLM", "offline"), choices=["offline", "claude"])
        p.set_defaults(func=func)

    p = sub.add_parser("send-approved", help="send approved follow-up drafts (Module 09)")
    p.add_argument("--dry-run", action="store_true", help="print instead of sending")
    p.set_defaults(func=cmd_send_approved)

    p = sub.add_parser("crm-sync", help="sync leads to the CRM, idempotently (Module 09)")
    p.set_defaults(func=cmd_crm_sync)

    p = sub.add_parser("mcp", help="run the AdmitFlow MCP server over stdio (Module 09; Python 3.10+)")
    p.add_argument("--user", default=os.environ.get("ADMITFLOW_MCP_USER"), required=False,
                   help="counsellor the tools act as (default from $ADMITFLOW_MCP_USER)")
    p.set_defaults(func=cmd_mcp)

    p = sub.add_parser("backup", help="back up the SQLite database and verify the copy (Module 10)")
    p.add_argument("--to", required=True)
    p.set_defaults(func=cmd_backup)

    p = sub.add_parser("verify-backup", help="open a backup and check its integrity and row counts (Module 10)")
    p.add_argument("path")
    p.set_defaults(func=cmd_verify_backup)

    p = sub.add_parser("serve", help="run the HTTP API (Module 04)")
    p.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"),
                   help="use 0.0.0.0 inside a container (default from $HOST)")
    p.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")),
                   help="default from $PORT (cloud platforms set it)")
    p.set_defaults(func=cmd_serve)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.WARNING if args.verbose else logging.ERROR, format="%(levelname)s %(message)s")
    from .privacy import RedactingFilter

    for handler in logging.getLogger().handlers:
        handler.addFilter(RedactingFilter())
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
