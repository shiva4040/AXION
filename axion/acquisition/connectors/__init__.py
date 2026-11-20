from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.connectors.arxiv import ArxivConnector
from axion.acquisition.connectors.crossref import CrossrefConnector
from axion.acquisition.connectors.pubmed import PubMedConnector
from axion.acquisition.connectors.openalex import OpenAlexConnector
from axion.acquisition.connectors.huggingface import HuggingFaceConnector
from axion.acquisition.connectors.kaggle import KaggleConnector
from axion.acquisition.connectors.web_search import WebSearchConnector
from axion.acquisition.connectors.local_upload import LocalUploadConnector
from axion.acquisition.connectors.google_scholar import GoogleScholarConnector
from axion.acquisition.connectors.nasa_ads import NASAADSConnector
from axion.acquisition.connectors.inspire_hep import InspireHEPConnector
from axion.acquisition.connectors.web_of_science import WebOfScienceConnector
from axion.acquisition.connectors.inspec import InspecConnector
from axion.acquisition.connectors.ajp import AmericanJournalOfPhysicsConnector
from axion.acquisition.connectors.proquest import ProQuestConnector
from axion.acquisition.connectors.smithsonian import SmithsonianConnector

__all__ = [
    "BaseSourceConnector",
    "ArxivConnector",
    "CrossrefConnector",
    "PubMedConnector",
    "OpenAlexConnector",
    "HuggingFaceConnector",
    "KaggleConnector",
    "WebSearchConnector",
    "LocalUploadConnector",
    "GoogleScholarConnector",
    "NASAADSConnector",
    "InspireHEPConnector",
    "WebOfScienceConnector",
    "InspecConnector",
    "AmericanJournalOfPhysicsConnector",
    "ProQuestConnector",
    "SmithsonianConnector",
]
