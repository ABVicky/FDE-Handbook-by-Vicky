"""The course assistant: retrieval + answering + follow-up drafting (added in Module 08).

A *workflow*, not an autonomous agent: the steps are fixed in code (retrieve → answer or draft →
validate), and the model never chooses actions with side effects. See docs/adr/005-course-assistant.md.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from .llm import Answer, Answerer, Drafter, build_engines
from .models import Draft
from .rag import Hit, Retriever, load_corpus


@dataclass
class CourseAssistant:
    retriever: Retriever
    answerer: Answerer
    drafter: Drafter
    k: int = 3

    def ask(self, question: str, as_of: Optional[date] = None) -> tuple:
        hits = self.retriever.search(question, k=self.k, as_of=as_of)
        return self.answerer.answer(question, hits), hits

    def draft_followup(self, lead, notes, requested_by: str) -> Draft:
        query = f"{lead.course or ''} fees timings campus visit"
        hits: List[Hit] = self.retriever.search(query, k=self.k)
        text = self.drafter.draft(lead, notes, hits)
        return Draft(
            draft_id=uuid.uuid4().hex[:12],
            lead_id=lead.lead_id,
            channel=text.channel,
            subject=text.subject,
            body=text.body,
            requested_by=requested_by,
            created_at=datetime.now().replace(microsecond=0),
            engine=text.engine,
        )


def build_assistant(docs: Optional[str] = None, kind: Optional[str] = None) -> Optional[CourseAssistant]:
    """From configuration: ADMITFLOW_DOCS (folder of course documents), ADMITFLOW_LLM ("offline" or "claude")."""
    folder = Path(docs or os.environ.get("ADMITFLOW_DOCS", "data/course_docs"))
    if not folder.is_dir():
        return None
    chunks = load_corpus(folder)
    if not chunks:
        return None
    answerer, drafter = build_engines(kind or os.environ.get("ADMITFLOW_LLM", "offline"))
    return CourseAssistant(Retriever(chunks), answerer, drafter)


__all__ = ["Answer", "CourseAssistant", "build_assistant"]
