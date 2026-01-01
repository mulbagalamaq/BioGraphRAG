"""Real-time biomedical data fetching from free public APIs.

This module fetches live data from:
- PubMed E-utilities (literature, citations)
- NCBI Gene (gene information)
- MeSH (disease/drug terminology)
- Europe PMC (biomedical publications)
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

import requests

LOGGER = logging.getLogger(__name__)

# API endpoints
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
GENE_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
GENE_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


class BiomedicalDataFetcher:
    """Fetch real-time biomedical data from public APIs."""

    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize fetcher with optional NCBI credentials.

        Parameters
        ----------
        email : str, optional
            Email for NCBI E-utilities (recommended for higher rate limits)
        api_key : str, optional
            NCBI API key for higher rate limits (optional, free to obtain)
        """
        self.email = email or "biographrag@example.com"
        self.api_key = api_key
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.34  # NCBI rate limit: 3 requests/second (or 10/s with API key)

    def _rate_limit(self):
        """Enforce NCBI rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def search_genes(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for genes by name or symbol.

        Parameters
        ----------
        query : str
            Gene name or symbol (e.g., "EGFR", "TP53")
        max_results : int
            Maximum number of results to return

        Returns
        -------
        List[Dict]
            List of gene dictionaries with id, symbol, description, organism
        """
        self._rate_limit()

        params = {
            "db": "gene",
            "term": f"{query}[Gene Name] AND Homo sapiens[Organism]",
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(GENE_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            gene_ids = data.get("esearchresult", {}).get("idlist", [])
            if not gene_ids:
                return []

            return self.fetch_gene_details(gene_ids)

        except Exception as exc:
            LOGGER.error("Gene search failed for query '%s': %s", query, exc)
            return []

    def fetch_gene_details(self, gene_ids: List[str]) -> List[Dict]:
        """Fetch detailed gene information by ID.

        Parameters
        ----------
        gene_ids : List[str]
            List of NCBI Gene IDs

        Returns
        -------
        List[Dict]
            List of gene dictionaries with detailed information
        """
        self._rate_limit()

        params = {
            "db": "gene",
            "id": ",".join(gene_ids),
            "retmode": "json",
            "email": self.email,
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(GENE_SUMMARY_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            genes = []
            for gene_id, gene_data in data.get("result", {}).items():
                if gene_id == "uids":
                    continue

                genes.append({
                    "id": f"GENE_{gene_data.get('name', gene_id)}",
                    "type": "Gene",
                    "symbol": gene_data.get("name", ""),
                    "name": gene_data.get("description", ""),
                    "description": gene_data.get("summary", ""),
                    "organism": gene_data.get("organism", {}).get("scientificname", "Homo sapiens"),
                    "chromosome": gene_data.get("chromosome", ""),
                    "ncbi_id": gene_id,
                    "properties": {
                        "source": "ncbi_gene",
                        "gene_id": gene_id,
                    }
                })

            return genes

        except Exception as exc:
            LOGGER.error("Gene fetch failed for IDs %s: %s", gene_ids, exc)
            return []

    def search_publications(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search PubMed for publications.

        Parameters
        ----------
        query : str
            Search query (e.g., "EGFR lung cancer", "BRCA1 treatment")
        max_results : int
            Maximum number of results

        Returns
        -------
        List[Dict]
            List of publication dictionaries with PMID, title, abstract
        """
        self._rate_limit()

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
            "sort": "relevance",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(PUBMED_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            pmids = data.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            return self.fetch_publication_details(pmids)

        except Exception as exc:
            LOGGER.error("Publication search failed for query '%s': %s", query, exc)
            return []

    def fetch_publication_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch detailed publication information by PMID.

        Parameters
        ----------
        pmids : List[str]
            List of PubMed IDs

        Returns
        -------
        List[Dict]
            List of publication dictionaries
        """
        self._rate_limit()

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "email": self.email,
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(PUBMED_FETCH_URL, params=params, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            publications = []

            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                title_elem = article.find(".//ArticleTitle")
                abstract_elem = article.find(".//AbstractText")

                pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
                title = title_elem.text if title_elem is not None else "No title"
                abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"

                # Extract authors
                authors = []
                for author in article.findall(".//Author"):
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None:
                        name = last_name.text
                        if fore_name is not None:
                            name = f"{fore_name.text} {name}"
                        authors.append(name)

                publications.append({
                    "id": f"PMID_{pmid}",
                    "type": "Publication",
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "properties": {
                        "source": "pubmed",
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    }
                })

            return publications

        except Exception as exc:
            LOGGER.error("Publication fetch failed for PMIDs %s: %s", pmids, exc)
            return []

    def search_disease_gene_associations(self, gene_symbol: str) -> List[Dict]:
        """Search for disease associations for a gene via PubMed literature.

        Parameters
        ----------
        gene_symbol : str
            Gene symbol (e.g., "EGFR")

        Returns
        -------
        List[Dict]
            List of disease-gene association edges
        """
        # Search PubMed for gene + disease mentions
        publications = self.search_publications(f"{gene_symbol} AND disease[MeSH]", max_results=10)

        associations = []
        for pub in publications:
            # Extract disease mentions from title/abstract (simple keyword matching)
            text = f"{pub['title']} {pub['abstract']}".lower()

            # Common disease keywords
            diseases = {
                "cancer": "DISEASE_CANCER",
                "lung cancer": "DISEASE_LUNG_CANCER",
                "breast cancer": "DISEASE_BREAST_CANCER",
                "colon cancer": "DISEASE_COLON_CANCER",
                "diabetes": "DISEASE_DIABETES",
                "alzheimer": "DISEASE_ALZHEIMERS",
                "parkinson": "DISEASE_PARKINSONS",
            }

            for disease_name, disease_id in diseases.items():
                if disease_name in text:
                    associations.append({
                        "source": f"GENE_{gene_symbol}",
                        "target": disease_id,
                        "relation": "ASSOCIATED_WITH",
                        "description": f"{gene_symbol} associated with {disease_name}",
                        "properties": {
                            "pmids": [pub["pmid"]],
                            "source": "pubmed_literature",
                            "evidence": pub["title"],
                        }
                    })

        return associations

    def build_realtime_graph(self, query: str, max_nodes: int = 30) -> Dict:
        """Build a knowledge graph in real-time from biomedical APIs.

        Parameters
        ----------
        query : str
            User's biomedical question
        max_nodes : int
            Maximum number of nodes to retrieve

        Returns
        -------
        Dict
            Graph dictionary with nodes and edges
        """
        nodes = []
        edges = []

        # Extract gene mentions from query (simple keyword extraction)
        gene_keywords = ["EGFR", "TP53", "KRAS", "BRCA1", "BRCA2", "AKT1", "PIK3CA", "PTEN"]
        mentioned_genes = [g for g in gene_keywords if g.lower() in query.lower()]

        if not mentioned_genes:
            # Generic search for genes
            genes = self.search_genes(query, max_results=5)
            nodes.extend(genes)
            mentioned_genes = [g["symbol"] for g in genes]
        else:
            # Fetch specific genes
            for gene_symbol in mentioned_genes[:3]:
                genes = self.search_genes(gene_symbol, max_results=1)
                nodes.extend(genes)

        # Search for publications
        publications = self.search_publications(query, max_results=min(10, max_nodes - len(nodes)))
        nodes.extend(publications)

        # Build gene-disease associations
        for gene_symbol in mentioned_genes[:3]:
            associations = self.search_disease_gene_associations(gene_symbol)
            edges.extend(associations[:5])

            # Add disease nodes referenced in edges
            for edge in associations[:5]:
                disease_id = edge["target"]
                if not any(n["id"] == disease_id for n in nodes):
                    nodes.append({
                        "id": disease_id,
                        "type": "Disease",
                        "name": disease_id.replace("DISEASE_", "").replace("_", " ").title(),
                        "description": f"Disease entity from literature mining",
                        "properties": {"source": "pubmed_inferred"}
                    })

        # Link publications to genes (mentions)
        for pub in publications:
            text = f"{pub['title']} {pub['abstract']}".lower()
            for gene_symbol in mentioned_genes:
                if gene_symbol.lower() in text:
                    edges.append({
                        "source": pub["id"],
                        "target": f"GENE_{gene_symbol}",
                        "relation": "MENTIONS",
                        "description": f"Publication mentions {gene_symbol}",
                        "properties": {"pmid": pub["pmid"]}
                    })

        LOGGER.info("Built real-time graph: %d nodes, %d edges", len(nodes), len(edges))
        return {"nodes": nodes, "edges": edges}


def fetch_realtime_data(question: str) -> Dict:
    """Fetch real-time biomedical data based on user question.

    Parameters
    ----------
    question : str
        User's biomedical question

    Returns
    -------
    Dict
        Knowledge graph with real-time data
    """
    fetcher = BiomedicalDataFetcher()
    return fetcher.build_realtime_graph(question, max_nodes=30)
