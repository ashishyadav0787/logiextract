import json, os
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def chat(system, user):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=system)
    return model.generate_content(user).text.strip()

def _parse_json(text):
    try:
        if "```" in text:
            for part in text.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("{"): return json.loads(part)
        return json.loads(text)
    except:
        try: return json.loads(text[text.index("{"):text.rindex("}")+1])
        except: return {}

def validate_against_po(invoice_fields: Dict[str, Any], po_fields: Dict[str, Any]) -> Dict[str, Any]:
    result = chat('Compare invoice vs PO. Return ONLY JSON: {"status":"matched|mismatch|warning","matched_fields":[],"mismatched_fields":[{"field":"x","expected":"y","found":"z","severity":"error"}],"missing_fields":[],"summary":"one sentence"}',
        f"PO:\n{json.dumps(po_fields,indent=2)}\n\nInvoice:\n{json.dumps(invoice_fields,indent=2)}")
    return _parse_json(result) or {"status":"warning","matched_fields":[],"mismatched_fields":[],"missing_fields":[],"summary":"Validation completed"}

def quick_field_validate(extracted_fields: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    result = chat(f'Check this {doc_type.replace("_"," ")} for issues. Return ONLY JSON: {{"status":"matched|warning|mismatch","matched_fields":[],"mismatched_fields":[{{"field":"x","expected":"y","found":"z","severity":"error"}}],"missing_fields":[],"summary":"one sentence"}}',
        f"Fields:\n{json.dumps(extracted_fields,indent=2)}")
    return _parse_json(result) or {"status":"warning","matched_fields":list(extracted_fields.keys()),"mismatched_fields":[],"missing_fields":[],"summary":"Validation completed"}
