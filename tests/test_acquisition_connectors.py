import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from axion.acquisition.types import DocumentType, AccessStatus
from axion.acquisition.connectors.arxiv import ArxivConnector
from axion.acquisition.connectors.crossref import CrossrefConnector
from axion.acquisition.connectors.pubmed import PubMedConnector
from axion.acquisition.connectors.openalex import OpenAlexConnector
from axion.acquisition.connectors.huggingface import HuggingFaceConnector
from axion.acquisition.connectors.kaggle import KaggleConnector
from axion.acquisition.connectors.web_search import WebSearchConnector
from axion.acquisition.connectors.local_upload import LocalUploadConnector

# Sample Mock Atom XML for arXiv
MOCK_ARXIV_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2104.00001v1</id>
    <title>Quantum Hall Effect in Topological Insulators</title>
    <summary>We investigate anomalous quantum Hall conductance in Bi2Se3 crystals.</summary>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <published>2021-04-01T12:00:00Z</published>
    <arxiv:doi>10.1103/PhysRevB.100.014401</arxiv:doi>
    <link title="pdf" href="http://arxiv.org/pdf/2104.00001v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category term="cond-mat.mes-hall"/>
  </entry>
</feed>
"""

# Sample Mock Crossref JSON
MOCK_CROSSREF_JSON = {
    "status": "ok",
    "message": {
        "items": [
            {
                "title": ["Thermal Conduction in Silicon Nanowires"],
                "abstract": "<jats:p>Experimental measurement of phonon mean free paths.</jats:p>",
                "author": [{"given": "Charlie", "family": "Brown"}],
                "DOI": "10.1063/1.5000000",
                "URL": "https://doi.org/10.1063/1.5000000",
                "published": {"date-parts": [[2020, 5, 15]]},
                "license": [{"URL": "http://creativecommons.org/licenses/by/4.0/"}],
                "container-title": ["Applied Physics Letters"],
                "type": "journal-article"
            }
        ]
    }
}

# Sample Mock PubMed JSON
MOCK_PUBMED_ESEARCH_JSON = {
    "esearchresult": {"idlist": ["31234567"]}
}

MOCK_PUBMED_ESUMMARY_JSON = {
    "result": {
        "31234567": {
            "title": "Structure and Mechanism of Photosystem II",
            "authors": [{"name": "Diana Prince"}],
            "pubdate": "2019 Jun",
            "source": "Nature Plants",
            "articleids": [
                {"idtype": "doi", "value": "10.1038/s41477-019-0001"},
                {"idtype": "pmc", "value": "PMC6789000"}
            ]
        }
    }
}

# Sample Mock OpenAlex JSON
MOCK_OPENALEX_JSON = {
    "results": [
        {
            "id": "https://openalex.org/W2741809807",
            "display_name": "Attention Is All You Need",
            "doi": "https://doi.org/10.48550/arxiv.1706.03762",
            "publication_date": "2017-06-12",
            "authorships": [{"author": {"display_name": "Ashish Vaswani"}}],
            "abstract_inverted_index": {
                "The": [0],
                "dominant": [1],
                "sequence": [2],
                "transduction": [3],
                "models": [4]
            },
            "open_access": {"is_oa": True, "oa_status": "gold"},
            "primary_location": {"landing_page_url": "https://arxiv.org/abs/1706.03762", "license": "cc-by"}
        }
    ]
}

# Sample Mock Hugging Face JSON
MOCK_HF_JSON = [
    {
        "id": "scientific_papers",
        "description": "Corpus of scientific papers extracted from ArXiv and PubMed.",
        "author": "armancohan",
        "cardData": {"license": "apache-2.0"},
        "downloads": 54200,
        "tags": ["summarization", "arxiv", "pubmed"],
        "private": False
    }
]

@pytest.mark.asyncio
async def test_arxiv_connector():
    connector = ArxivConnector()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = MOCK_ARXIV_ATOM
        mock_get.return_value = mock_resp

        results = await connector.search("topological insulators", limit=5)
        assert len(results) == 1
        doc = results[0]
        assert doc.source_name == "arxiv"
        assert "Quantum Hall Effect" in doc.title
        assert "Bi2Se3" in doc.content
        assert "Alice Smith" in doc.authors
        assert doc.doi == "10.1103/PhysRevB.100.014401"
        assert doc.access_status == AccessStatus.OPEN_ACCESS

@pytest.mark.asyncio
async def test_crossref_connector():
    connector = CrossrefConnector()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_CROSSREF_JSON
        mock_get.return_value = mock_resp

        results = await connector.search("silicon nanowires", limit=5)
        assert len(results) == 1
        doc = results[0]
        assert doc.source_name == "crossref"
        assert "Silicon Nanowires" in doc.title
        assert "phonon mean free paths" in doc.content
        assert "Charlie Brown" in doc.authors
        assert doc.doi == "10.1063/1.5000000"
        assert doc.access_status == AccessStatus.OPEN_ACCESS

@pytest.mark.asyncio
async def test_pubmed_connector():
    connector = PubMedConnector()
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock first call (esearch) and second call (esummary)
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = MOCK_PUBMED_ESEARCH_JSON

        resp2 = MagicMock()
        resp2.status_code = 200
        resp2.json.return_value = MOCK_PUBMED_ESUMMARY_JSON

        mock_get.side_effect = [resp1, resp2]

        results = await connector.search("photosystem II", limit=5)
        assert len(results) == 1
        doc = results[0]
        assert doc.source_name == "pubmed"
        assert "Photosystem II" in doc.title
        assert "Diana Prince" in doc.authors
        assert doc.doi == "10.1038/s41477-019-0001"
        assert doc.access_status == AccessStatus.OPEN_ACCESS

@pytest.mark.asyncio
async def test_openalex_connector():
    connector = OpenAlexConnector()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_OPENALEX_JSON
        mock_get.return_value = mock_resp

        results = await connector.search("attention is all you need", limit=5)
        assert len(results) == 1
        doc = results[0]
        assert doc.source_name == "openalex"
        assert "Attention Is All You Need" in doc.title
        assert doc.content == "The dominant sequence transduction models"
        assert "Ashish Vaswani" in doc.authors
        assert doc.access_status == AccessStatus.OPEN_ACCESS

@pytest.mark.asyncio
async def test_huggingface_connector():
    connector = HuggingFaceConnector()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_HF_JSON
        mock_get.return_value = mock_resp

        results = await connector.search("scientific_papers", limit=5)
        assert len(results) == 1
        doc = results[0]
        assert doc.source_name == "huggingface"
        assert doc.document_type == DocumentType.DATASET
        assert "scientific_papers" in doc.title
        assert "apache-2.0" in doc.license

@pytest.mark.asyncio
async def test_kaggle_connector_public_mode():
    connector = KaggleConnector(username="", api_key="")
    assert not connector.is_authenticated
    results = await connector.search("higgs boson physics", limit=3)
    assert len(results) >= 1
    doc = results[0]
    assert doc.source_name == "kaggle"
    assert doc.document_type == DocumentType.DATASET

@pytest.mark.asyncio
async def test_web_search_connector():
    connector = WebSearchConnector()
    with patch.object(connector, "_search_duckduckgo_api") as mock_api:
        from axion.acquisition.types import SourceDocument
        mock_api.return_value = [
            SourceDocument(
                title="Hydraulic Machinery Principles",
                content="Hydraulic systems transmit power using pressurized fluids.",
                source_name="web_search",
                source_url="https://example.org/hydraulics",
                document_type=DocumentType.WEB_PAGE
            )
        ]
        results = await connector.search("hydraulic principles", limit=2)
        assert len(results) == 1
        assert results[0].source_name == "web_search"
        assert "Hydraulic Machinery" in results[0].title

@pytest.mark.asyncio
async def test_local_upload_connector(test_db_session):
    from axion.ingestion.source_manager import SourceManager
    manager = SourceManager(test_db_session)
    await manager.ingest_text(
        text_content="Lorenz force drives charged particle acceleration in magnetic fields.",
        title="Electrodynamics Notes",
        source_uri="local://physics/lorentz.txt"
    )

    connector = LocalUploadConnector(session=test_db_session)
    results = await connector.search("Electrodynamics", limit=5)
    assert len(results) >= 1
    doc = results[0]
    assert doc.source_name == "local_upload"
    assert "Electrodynamics" in doc.title
    assert "Lorenz force" in doc.content

@pytest.mark.asyncio
async def test_connector_health_checks():
    c_arxiv = ArxivConnector()
    health = await c_arxiv.check_health()
    assert health.source_name == "arxiv"
    assert health.source_type == "papers"

    c_kaggle = KaggleConnector()
    health_k = await c_kaggle.check_health()
    assert health_k.source_name == "kaggle"
    assert health_k.requires_auth is True
