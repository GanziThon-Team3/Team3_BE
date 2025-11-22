import requests
from langchain.tools import tool

from langchain_upstage import ChatUpstage
from decouple import config
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

llm = ChatUpstage(api_key=config("upstage_key"), model="solar-pro2")

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

def ai_answer(question):
    tools = [
    search_drugs,
    search_medical_databases,
    ]
    llm_with_tools = llm.bind_tools(tools)

    messages = [{"role": "system", "content": "질병 혹은 약에 관해서는 최대한 tool을 사용하고, 질병 혹은 약에 해당하는 한 단어만 영어로 번역해서 query로 전달해줘. 대신 답변은 한국어로"},
        {"role": "user", "content": question}]
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # 이름 → 실제 tool 객체 매핑
        tool_map = {t.name: t for t in tools}
        tool_fn = tool_map[tool_name]

        # tool 실행
        tool_result = tool_fn.invoke(tool_args)

        summary = llm.invoke([
            {"role": "system", "content": "질문에 맞게 5줄 이내로 한국어로 정리해줘. 검색결과가 없거나 부족하면 추가자료를 찾아줘"},
            {"role": "user", "content": "question: " + question + "tool_result: " + str(tool_result)}
        ])

        return {
            "mode": "tool_call",
            "tool": tool_name,
            "args": tool_args,
            "tool_resut" : tool_result,
            "result": summary.content,
        }
    return {
        "mode": "llm_response",
        "result": response.content,
    }