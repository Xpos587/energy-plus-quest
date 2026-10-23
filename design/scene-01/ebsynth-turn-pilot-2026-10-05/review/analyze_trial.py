import json
import os
import re
import time
from pathlib import Path

from google import genai
from google.genai import types


ROOT = Path(__file__).parent
MAP_VIDEO = ROOT / "transfer-three-map.mp4"
COMPARISON_VIDEO = ROOT / "transfer-three-turn.mp4"
CRITIQUE = ROOT / "critique.md"
RECEIPT = ROOT / "analysis-receipt.json"

PROMPT = """You are a skeptical animation reviewer. Analyze both complete six-second videos.
The first file is the actual map render. The second is the source/comparison render.

Required target: bright, clean 2D illustration with soft colored edges; no black-heavy,
plastic, or low-poly look. Exactly one green modern tractor with one white trailer must
make a full articulated 90-degree turn. If people are visible, there should be exactly
two drivers, consistently located inside the cab. Reject roof-driving, duplicated people
or vehicles, teleporting parts, or temporally unstable/morphing details.

At 12 fps, inspect the whole timeline and give extra frame-level scrutiny to the key
switches 17->18 (about 00:01.417->00:01.500) and 53->54 (about
00:04.417->00:04.500). Compare those adjacent frames for identity, silhouette,
articulation, driver placement/count, color/style, and background continuity.

Return Markdown in English with:
1. A single PASS or FAIL verdict. FAIL if the details morph, if two drivers cannot be
   read when people are visible, if articulation/full 90-degree turn is not supported,
   or if the art is not aligned with the stated bright clean 2D target.
2. Timestamped observations covering the full 00:00.000-00:06.000 timeline.
3. Separate explicit observations for 17->18 and 53->54.
4. A criterion-by-criterion table: style; one tractor/one trailer; full 90-degree
   articulated turn; drivers; no roof-driving/duplicates; temporal stability.
5. Separate observed facts from interpretations, and mark unreadable or uncertain detail.
Do not infer compliance from the prompt. Do not invent visible details. This is review of
the actual files, not a description-writing task.
"""


def main() -> None:
    key = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ["GOOGLE_AI_API_KEY"]
    )
    client = genai.Client(api_key=key)
    uploads = []
    receipt = {
        "sources": [MAP_VIDEO.name, COMPARISON_VIDEO.name],
        "coverage": "both complete 6-second videos at 12 fps",
        "key_switches": ["17->18", "53->54"],
        "model": "gemini-2.5-flash",
        "official_guide": "https://ai.google.dev/gemini-api/docs/video-understanding",
        "cleanup": False,
    }
    try:
        for path in (MAP_VIDEO, COMPARISON_VIDEO):
            upload = client.files.upload(file=str(path))
            uploads.append(upload)

        active_uploads = []
        for upload in uploads:
            for _ in range(60):
                upload = client.files.get(name=upload.name)
                if upload.state.name == "ACTIVE":
                    active_uploads.append(upload)
                    break
                if upload.state.name == "FAILED":
                    raise RuntimeError(f"Video processing failed: {upload.name}")
                time.sleep(2)
            else:
                raise RuntimeError(f"Video processing timed out: {upload.name}")

        parts = [
            types.Part(
                file_data=types.FileData(
                    file_uri=upload.uri,
                    mime_type="video/mp4",
                ),
                video_metadata=types.VideoMetadata(fps=12),
            )
            for upload in active_uploads
        ]
        parts.append(types.Part(text=PROMPT))
        response = client.models.generate_content(
            model=receipt["model"],
            contents=[types.Content(parts=parts)],
            config=types.GenerateContentConfig(temperature=0.1),
        )
        critique = re.sub(r"[ \t]{2,}", " ", response.text).rstrip() + "\n"
        CRITIQUE.write_text(critique, encoding="utf-8")
        receipt["status"] = "completed"
        if response.usage_metadata:
            receipt["usage"] = response.usage_metadata.model_dump(mode="json")
    except Exception as error:
        receipt["status"] = "failed"
        receipt["error_type"] = type(error).__name__
        receipt["error"] = str(error)
        raise
    finally:
        cleanup_errors = []
        for upload in uploads:
            try:
                client.files.delete(name=upload.name)
            except Exception as error:
                cleanup_errors.append(f"{type(error).__name__}: {error}")
        receipt["cleanup"] = bool(uploads) and not cleanup_errors
        if cleanup_errors:
            receipt["cleanup_errors"] = cleanup_errors
        RECEIPT.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
