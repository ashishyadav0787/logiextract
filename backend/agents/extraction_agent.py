import json, os
from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def chat(system: str, user: str) -> str:
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=system)
    return model.generate_content(user).text.strip()

class AgentState(TypedDict):
    raw_text: str
    filename: str
    doc_type: Optional[str]
    schema: Optional[Dict]
    extracted_fields: Optional[Dict]
    confidence_score: Optional[float]
    evidence: Optional[list]
    error: Optional[str]

SCHEMAS = {
    "bill_of_lading": {"shipper_name":"Name of shipper","shipper_address":"Address of shipper","consignee_name":"Name of consignee","consignee_address":"Address of consignee","notify_party":"Notify party","vessel_name":"Vessel name","voyage_number":"Voyage number","port_of_loading":"Port of loading","port_of_discharge":"Port of discharge","place_of_delivery":"Place of delivery","cargo_description":"Cargo description","hs_code":"HS code","gross_weight":"Gross weight","measurement":"CBM measurement","number_of_packages":"Number of packages","bl_number":"B/L number","date_of_issue":"Date of issue","freight_terms":"Freight terms","incoterms":"Incoterms"},
    "invoice": {"invoice_number":"Invoice number","invoice_date":"Invoice date","seller_name":"Seller name","seller_address":"Seller address","buyer_name":"Buyer name","buyer_address":"Buyer address","po_reference":"PO reference","currency":"Currency","total_amount":"Total amount","line_items":"Line items array","payment_terms":"Payment terms","bank_details":"Bank details","hs_code":"HS code","country_of_origin":"Country of origin"},
    "purchase_order": {"po_number":"PO number","po_date":"PO date","buyer_name":"Buyer name","supplier_name":"Supplier name","delivery_date":"Delivery date","line_items":"Line items array","total_amount":"Total amount","currency":"Currency","delivery_address":"Delivery address","payment_terms":"Payment terms"}
}

def _parse_json(text):
    try:
        if "```" in text:
            for part in text.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("{"):
                    return json.loads(part)
        return json.loads(text)
    except:
        try:
            return json.loads(text[text.index("{"):text.rindex("}")+1])
        except:
            return {}

def scope_resolution(state):
    result = chat("You are a logistics document classifier. Reply ONLY with: bill_of_lading, invoice, purchase_order, or unknown. No explanation.", f"Document:\n{state['raw_text'][:1500]}")
    doc_type = result.strip().lower().split()[0]
    if doc_type not in ["bill_of_lading","invoice","purchase_order"]: doc_type = "unknown"
    return {**state, "doc_type": doc_type}

def context_compilation(state):
    return {**state, "schema": SCHEMAS.get(state.get("doc_type","unknown"), {})}

def schema_routing(state) -> Literal["extract","error"]:
    return "error" if state.get("doc_type") == "unknown" else "extract"

def plan_and_execute(state):
    schema_str = "\n".join([f"- {k}: {v}" for k,v in state["schema"].items()])
    result = chat(
        f"You are an expert logistics document parser. Extract these fields:\n{schema_str}\n\nReturn ONLY valid JSON no markdown:\n{{\"fields\":{{...}},\"confidence_score\":0.9,\"evidence\":[{{\"field\":\"x\",\"snippet\":\"y\"}}]}}",
        f"Document:\n{state['raw_text']}"
    )
    parsed = _parse_json(result)
    if parsed:
        return {**state, "extracted_fields": parsed.get("fields", parsed), "confidence_score": float(parsed.get("confidence_score", 0.80)), "evidence": parsed.get("evidence", [])}
    return {**state, "extracted_fields": {}, "confidence_score": 0.0, "evidence": [], "error": "Parse failed"}

def handle_error(state):
    return {**state, "extracted_fields": {}, "confidence_score": 0.0, "evidence": [], "error": "Could not identify document type"}

def evidence_delivery(state):
    return state

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("scope_resolution", scope_resolution)
    g.add_node("context_compilation", context_compilation)
    g.add_node("plan_and_execute", plan_and_execute)
    g.add_node("evidence_delivery", evidence_delivery)
    g.add_node("handle_error", handle_error)
    g.set_entry_point("scope_resolution")
    g.add_edge("scope_resolution", "context_compilation")
    g.add_conditional_edges("context_compilation", schema_routing, {"extract":"plan_and_execute","error":"handle_error"})
    g.add_edge("plan_and_execute", "evidence_delivery")
    g.add_edge("evidence_delivery", END)
    g.add_edge("handle_error", END)
    return g.compile()

extraction_agent = build_graph()

def run_extraction(raw_text: str, filename: str) -> Dict[str, Any]:
    return extraction_agent.invoke({"raw_text": raw_text, "filename": filename, "doc_type": None, "schema": None, "extracted_fields": None, "confidence_score": None, "evidence": None, "error": None})
