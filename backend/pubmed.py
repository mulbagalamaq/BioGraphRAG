"""Async PubMed / NCBI Gene client for real-time biomedical data fetching."""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

import httpx

from backend.config import AppConfig

LOGGER = logging.getLogger(__name__)

# NCBI E-utilities endpoints
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
GENE_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
GENE_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# Common disease patterns for literature mining
DISEASE_PATTERNS: Dict[str, str] = {
    "lung cancer": "DISEASE_LUNG_CANCER",
    "breast cancer": "DISEASE_BREAST_CANCER",
    "colon cancer": "DISEASE_COLON_CANCER",
    "colorectal cancer": "DISEASE_COLORECTAL_CANCER",
    "pancreatic cancer": "DISEASE_PANCREATIC_CANCER",
    "prostate cancer": "DISEASE_PROSTATE_CANCER",
    "ovarian cancer": "DISEASE_OVARIAN_CANCER",
    "leukemia": "DISEASE_LEUKEMIA",
    "lymphoma": "DISEASE_LYMPHOMA",
    "melanoma": "DISEASE_MELANOMA",
    "glioblastoma": "DISEASE_GLIOBLASTOMA",
    "cancer": "DISEASE_CANCER",
    "diabetes": "DISEASE_DIABETES",
    "alzheimer": "DISEASE_ALZHEIMERS",
    "parkinson": "DISEASE_PARKINSONS",
    "hypertension": "DISEASE_HYPERTENSION",
    "asthma": "DISEASE_ASTHMA",
    "obesity": "DISEASE_OBESITY",
    "arthritis": "DISEASE_ARTHRITIS",
}

# Regex to find gene-like symbols in text (2-6 uppercase letters/digits)
_GENE_SYMBOL_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,5})\b")


class BiomedicalDataFetcher:
    """Fetches real-time data from PubMed and NCBI Gene APIs."""

    def __init__(self, config: AppConfig) -> None:
        self.email = config.get("ncbi.email", "biographrag@example.com")
        self.api_key: Optional[str] = config.get("ncbi.api_key")
        self.max_publications = int(config.get("retrieval.max_publications", 10))
        self.max_genes = int(config.get("retrieval.max_genes", 5))
        self.max_nodes = int(config.get("retrieval.max_nodes", 30))
        self._last_request = 0.0
        self._interval = 0.11 if self.api_key else 0.34

    def _base_params(self) -> Dict[str, str]:
        params: Dict[str, str] = {"email": self.email}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    async def _rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self._interval:
            await asyncio.sleep(self._interval - elapsed)
        self._last_request = time.monotonic()

    # ------------------------------------------------------------------
    # Gene search
    # ------------------------------------------------------------------

    async def search_genes(
        self, client: httpx.AsyncClient, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search NCBI Gene for human genes matching *query*."""
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "gene",
            "term": f"{query}[Gene Name] AND Homo sapiens[Organism]",
            "retmax": str(max_results),
            "retmode": "json",
        }
        try:
            resp = await client.get(GENE_SEARCH, params=params, timeout=10)
            resp.raise_for_status()
            gene_ids = resp.json().get("esearchresult", {}).get("idlist", [])
            if not gene_ids:
                return []
            return await self._fetch_gene_details(client, gene_ids)
        except Exception as exc:
            LOGGER.error("Gene search failed for '%s': %s", query, exc)
            return []

    async def _fetch_gene_details(
        self, client: httpx.AsyncClient, gene_ids: List[str]
    ) -> List[Dict[str, Any]]:
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "gene",
            "id": ",".join(gene_ids),
            "retmode": "json",
        }
        try:
            resp = await client.get(GENE_SUMMARY, params=params, timeout=10)
            resp.raise_for_status()
            result = resp.json().get("result", {})
            genes: List[Dict[str, Any]] = []
            for gid, gdata in result.items():
                if gid == "uids":
                    continue
                symbol = gdata.get("name", gid)
                genes.append(
                    {
                        "id": f"GENE_{symbol}",
                        "type": "Gene",
                        "symbol": symbol,
                        "name": gdata.get("description", ""),
                        "description": gdata.get("summary", ""),
                        "properties": {
                            "source": "ncbi_gene",
                            "ncbi_id": gid,
                            "chromosome": gdata.get("chromosome", ""),
                            "organism": gdata.get("organism", {}).get(
                                "scientificname", "Homo sapiens"
                            ),
                        },
                    }
                )
            return genes
        except Exception as exc:
            LOGGER.error("Gene detail fetch failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Publication search
    # ------------------------------------------------------------------

    async def search_publications(
        self, client: httpx.AsyncClient, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search PubMed for publications matching *query*."""
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "pubmed",
            "term": query,
            "retmax": str(max_results),
            "retmode": "json",
            "sort": "relevance",
        }
        try:
            resp = await client.get(PUBMED_SEARCH, params=params, timeout=10)
            resp.raise_for_status()
            pmids = resp.json().get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []
            return await self._fetch_publication_details(client, pmids)
        except Exception as exc:
            LOGGER.error("PubMed search failed for '%s': %s", query, exc)
            return []

    async def _fetch_publication_details(
        self, client: httpx.AsyncClient, pmids: List[str]
    ) -> List[Dict[str, Any]]:
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        try:
            resp = await client.get(PUBMED_FETCH, params=params, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            pubs: List[Dict[str, Any]] = []
            for article in root.findall(".//PubmedArticle"):
                pmid_el = article.find(".//PMID")
                title_el = article.find(".//ArticleTitle")
                abstract_el = article.find(".//AbstractText")

                pmid = pmid_el.text if pmid_el is not None else "Unknown"
                title = title_el.text if title_el is not None else "No title"
                abstract = abstract_el.text if abstract_el is not None else ""

                authors: List[str] = []
                for author in article.findall(".//Author"):
                    last = author.find("LastName")
                    fore = author.find("ForeName")
                    if last is not None:
                        name = last.text
                        if fore is not None:
                            name = f"{fore.text} {name}"
                        authors.append(name)

                pubs.append(
                    {
                        "id": f"PMID_{pmid}",
                        "type": "Publication",
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "name": title,
                        "description": (abstract or "")[:500],
                        "properties": {
                            "source": "pubmed",
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        },
                    }
                )
            return pubs
        except Exception as exc:
            LOGGER.error("PubMed fetch failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Disease–gene associations (literature mining)
    # ------------------------------------------------------------------

    async def search_disease_associations(
        self, client: httpx.AsyncClient, gene_symbol: str
    ) -> List[Dict[str, Any]]:
        """Mine PubMed for disease associations for *gene_symbol*."""
        pubs = await self.search_publications(
            client, f"{gene_symbol} AND disease[MeSH]", max_results=10
        )
        edges: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for pub in pubs:
            text = f"{pub['title']} {pub.get('abstract', '')}".lower()
            for disease_name, disease_id in DISEASE_PATTERNS.items():
                if disease_name in text:
                    key = f"{gene_symbol}_{disease_id}"
                    if key in seen:
                        continue
                    seen.add(key)
                    edges.append(
                        {
                            "source": f"GENE_{gene_symbol}",
                            "target": disease_id,
                            "relation": "ASSOCIATED_WITH",
                            "description": f"{gene_symbol} associated with {disease_name}",
                            "properties": {
                                "pmid": pub["pmid"],
                                "source": "pubmed_literature",
                            },
                        }
                    )
        return edges

    # ------------------------------------------------------------------
    # Full knowledge-graph builder
    # ------------------------------------------------------------------

    def _extract_gene_symbols(self, text: str) -> List[str]:
        """Extract likely gene symbols from the query text."""
        return list(dict.fromkeys(_GENE_SYMBOL_RE.findall(text)))

    async def build_knowledge_graph(self, question: str) -> Dict[str, Any]:
        """Build a KG from live APIs for the given *question*.

        Returns ``{"nodes": [...], "edges": [...]}``.
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        mentioned = self._extract_gene_symbols(question)

        async with httpx.AsyncClient() as client:
            # Fetch genes — either specific or generic search
            if mentioned:
                gene_tasks = [
                    self.search_genes(client, sym, max_results=1)
                    for sym in mentioned[: self.max_genes]
                ]
                gene_results = await asyncio.gather(*gene_tasks)
                for batch in gene_results:
                    nodes.extend(batch)
                found_symbols = [g["symbol"] for g in nodes if g.get("symbol")]
            else:
                genes = await self.search_genes(
                    client, question, max_results=self.max_genes
                )
                nodes.extend(genes)
                found_symbols = [g["symbol"] for g in genes if g.get("symbol")]

            # Fetch publications concurrently with disease associations
            pub_task = self.search_publications(
                client,
                question,
                max_results=min(self.max_publications, self.max_nodes - len(nodes)),
            )
            assoc_tasks = [
                self.search_disease_associations(client, sym)
                for sym in found_symbols[:3]
            ]

            pub_result, *assoc_results = await asyncio.gather(
                pub_task, *assoc_tasks
            )

            nodes.extend(pub_result)

            # Add disease-gene edges and disease nodes
            for assocs in assoc_results:
                for edge in assocs[:5]:
                    edges.append(edge)
                    disease_id = edge["target"]
                    if not any(n["id"] == disease_id for n in nodes):
                        nodes.append(
                            {
                                "id": disease_id,
                                "type": "Disease",
                                "name": disease_id.replace("DISEASE_", "")
                                .replace("_", " ")
                                .title(),
                                "description": "Disease entity from literature mining",
                                "properties": {"source": "pubmed_inferred"},
                            }
                        )

            # Link publications → genes (MENTIONS edges)
            for pub in pub_result:
                text = f"{pub['title']} {pub.get('abstract', '')}".lower()
                for sym in found_symbols:
                    if sym.lower() in text:
                        edges.append(
                            {
                                "source": pub["id"],
                                "target": f"GENE_{sym}",
                                "relation": "MENTIONS",
                                "description": f"Publication mentions {sym}",
                                "properties": {"pmid": pub["pmid"]},
                            }
                        )

        LOGGER.info("Built KG: %d nodes, %d edges", len(nodes), len(edges))
        return {"nodes": nodes, "edges": edges}
