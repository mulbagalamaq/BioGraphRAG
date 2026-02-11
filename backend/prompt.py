"""Prompt builder — formats KG context for the LLM."""

from __future__ import annotations

from typing import Any, Dict, List

MAX_CONTEXT_CHARS = 6000


def build_prompt(
    question: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
) -> str:
    """Build the LLM prompt from question + retrieved KG subgraph."""
    lines = [
        "You are an expert biomedical research assistant. "
        "Use the knowledge graph context below to answer the question. "
        "Be concise, accurate, and cite PMIDs when available.",
        f"\nQuestion: {question}",
        "\n--- Knowledge Graph Context ---",
    ]

    # Genes / diseases / drugs
    for node in nodes:
        ntype = node.get("type", "Entity")
        name = node.get("name") or node.get("id", "?")
        desc = node.get("description", "")
        if ntype == "Publication":
            continue  # handled below
        entry = f"[{ntype}] {name}"
        if desc:
            entry += f": {desc[:200]}"
        lines.append(entry)

    # Publications
    pub_lines: List[str] = []
    for node in nodes:
        if node.get("type") != "Publication":
            continue
        pmid = node.get("pmid", "")
        title = node.get("title") or node.get("name", "")
        abstract = node.get("abstract") or node.get("description", "")
        url = (node.get("properties") or {}).get("url", "")
        entry = f"[Publication] PMID:{pmid} — {title}"
        if abstract:
            entry += f"\n  Abstract: {abstract[:300]}"
        if url:
            entry += f"\n  URL: {url}"
        pub_lines.append(entry)
    if pub_lines:
        lines.append("\nRelevant Publications:")
        lines.extend(pub_lines)

    # Relationships
    if edges:
        lines.append("\nRelationships:")
        for edge in edges:
            src = edge.get("source", "?")
            tgt = edge.get("target", "?")
            rel = edge.get("relation", "RELATED")
            desc = edge.get("description", "")
            entry = f"  {src} —[{rel}]→ {tgt}"
            if desc:
                entry += f"  ({desc})"
            lines.append(entry)

    lines.append("\n--- End Context ---")
    lines.append("\nAnswer (include citations and brief rationale):")

    prompt = "\n".join(lines)

    # Truncate to fit context window
    if len(prompt) > MAX_CONTEXT_CHARS:
        prompt = prompt[:MAX_CONTEXT_CHARS] + "\n...[truncated]\n\nAnswer:"

    return prompt
