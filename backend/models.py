"""Pydantic request / response schemas for the BioGraphRAG API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class NodeSchema(BaseModel):
    id: str
    type: str
    name: str
    description: str = ""
    properties: Dict[str, Any] = {}


class EdgeSchema(BaseModel):
    source: str
    target: str
    relation: str
    description: str = ""


class EvidenceSchema(BaseModel):
    pmid: str = ""
    title: str = ""
    url: str = ""
    score: Optional[float] = None


class MetadataSchema(BaseModel):
    pipeline_ms: int = 0
    gnn_enabled: bool = False
    node_count: int = 0
    edge_count: int = 0


class QuestionResponse(BaseModel):
    question: str
    answer: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    metadata: MetadataSchema = MetadataSchema()
