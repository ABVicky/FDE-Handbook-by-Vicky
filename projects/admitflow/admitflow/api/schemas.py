"""Request and response shapes (Pydantic). These become the OpenAPI docs at /docs."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..normalize import normalize_email, normalize_name, normalize_phone

Status = Literal["new", "contacted", "visit_booked", "applied", "enrolled", "lost"]
Source = Literal["website", "ad", "phone", "walk-in", "whatsapp"]


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    role: str


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lead_id: str
    received_at: datetime
    name: str
    phone: Optional[str]
    email: Optional[str]
    course: Optional[str]
    sources: List[str]
    status: str
    assigned_to: Optional[str]
    notes: str = ""


class LeadPage(BaseModel):
    items: List[LeadOut]
    total: int
    page: int
    page_size: int


class LeadCreate(BaseModel):
    """A lead typed in by reception (phone call or walk-in)."""

    name: str = Field(min_length=1, max_length=200)
    phone: Optional[str] = None
    email: Optional[str] = None
    course: Optional[str] = Field(default=None, max_length=100)
    source: Source

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = normalize_name(value)
        if not any(ch.isalpha() for ch in cleaned):
            raise ValueError("name must contain at least one letter")
        return cleaned

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: Optional[str]) -> Optional[str]:
        if value in (None, ""):
            return None
        email = normalize_email(value)
        if email is None:
            raise ValueError("not a valid email address")
        return email

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: Optional[str]) -> Optional[str]:
        if value in (None, ""):
            return None
        phone = normalize_phone(value)
        if phone is None:
            raise ValueError("not a valid phone number")
        return phone


class LeadUpdate(BaseModel):
    status: Optional[Status] = None
    assigned_to: Optional[str] = None
    course: Optional[str] = Field(default=None, max_length=100)


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author: str
    text: str
    created_at: datetime


class LeadDetail(LeadOut):
    history: List[NoteOut]


class FollowUpIn(BaseModel):
    due: datetime


class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    followup_id: str
    lead_id: str
    counsellor: str
    due: datetime
    done: bool


class Stats(BaseModel):
    total: int
    by_status: dict
    by_source: dict
    unassigned: int


class ScoreOut(BaseModel):
    lead_id: str
    probability: float
    band: Literal["high", "medium", "low"]
    factors: List[str]
    model_version: str


class PriorityLead(BaseModel):
    lead_id: str
    name: str
    course: Optional[str]
    sources: List[str]
    hours_waiting: float
    score: float
    band: str
    factors: List[str]


class AskIn(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class Citation(BaseModel):
    chunk_id: str
    title: str
    section: str


class AskOut(BaseModel):
    answer: str
    answered: bool
    citations: List[Citation]


class DraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draft_id: str
    lead_id: str
    channel: str
    subject: str
    body: str
    requested_by: str
    created_at: datetime
    engine: str
    status: str
    decided_by: Optional[str]
    decided_at: Optional[datetime]
    reason: str
    sent_at: Optional[datetime] = None
    external_id: Optional[str] = None


class DraftDecision(BaseModel):
    reason: str = Field(default="", max_length=500)


class WebFormIn(BaseModel):
    """A website enquiry form submission (sent by the website's server, signed)."""

    name: str = Field(min_length=1, max_length=200)
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=40)
    course: Optional[str] = Field(default=None, max_length=100)
    message: str = Field(default="", max_length=2000)


class GoogleLoginIn(BaseModel):
    id_token: str = Field(min_length=10, max_length=4096)
