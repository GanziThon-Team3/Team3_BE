import requests
from langchain.tools import tool

BASE_URL = "http://localhost:3000"


# 1) search-drugs
@tool
def search_drugs(query: str, limit: int = 10):
    """Search drug info using FDA open database"""
    res = requests.get(f"{BASE_URL}/search-drugs", params={"query": query, "limit": limit})
    res.raise_for_status()
    return res.json()

# 10) search-medical-databases
@tool
def search_medical_databases(query: str):
    """Search multiple medical databases: PubMed, Scholar, Cochrane, ClinicalTrials."""
    res = requests.get(f"{BASE_URL}/search-medical-databases", params={"query": query})
    res.raise_for_status()
    return res.json()
