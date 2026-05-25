from fastapi import APIRouter
import json
import re
from models import DebateRequest
from services.ollama import client, MODEL
from services.scoring import score_argument
from services.ollama import generate_references

router = APIRouter()

@router.post("/score")
def score_debate(request: DebateRequest):
    # Step 1: Extract arguments using LLM
    prompt = f"""You are a debate analyst. Extract specific arguments from the transcript below.

IMPORTANT RULES:
- Extract ONLY arguments that appear in the transcript
- Do NOT repeat the topic as an argument
- Each argument must be a specific claim made by the speaker
- Include the reason/evidence they gave

Return ONLY a JSON array like this:
[
  {{"claim": "specific claim made", "premise": "reason or evidence given"}},
  {{"claim": "another specific claim", "premise": "reason or evidence given"}}
]

Topic: {request.topic}
Speaker: {request.speaker}
Transcript: {request.transcript}

Return ONLY the JSON array, nothing else."""

    response = client.generate(model=MODEL, prompt=prompt)
    raw = response["response"].strip()

    raw = re.sub(r"```json|```", "", raw).strip()
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        extracted_args = json.loads(raw)
        if not isinstance(extracted_args, list):
            extracted_args = []
    except:
        extracted_args = []

    # Use provided references or generate from topic
    references = request.reference_arguments if request.reference_arguments else generate_references(request.topic)

    # Step 2: Score each argument
    matched = 0
    total_quality = 0.0
    results = []

    for arg in extracted_args:
        best_match, best_score = score_argument(arg.get("claim", ""), references)

        if best_score >= 0.5:
            matched += 1

        total_quality += best_score
        results.append({
            "argument": arg.get("claim", ""),
            "best_match": best_match,
            "quality_score": round(best_score, 2)
        })

    # Step 3: Calculate final score
    total_args = len(extracted_args)
    coverage = round(matched / total_args, 2) if total_args > 0 else 0.0
    quality = round(total_quality / total_args, 2) if total_args > 0 else 0.0
    final_score = round(coverage * quality, 2)

    return {
        "speaker": request.speaker,
        "topic": request.topic,
        "extracted_arguments": results,
        "coverage": coverage,
        "quality": quality,
        "final_score": final_score
    }