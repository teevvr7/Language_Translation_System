"""
Technical Entity and Term Preservation Service
Extracts, protects (via placeholders), restores, and audits domain-specific identifiers.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from app.config import DEFAULT_PRODUCT_GLOSSARY, TECHNICAL_PATTERNS


class TermPreservationService:
    """Protects technical vocabulary, error codes, identifiers, and brand terms from mistranslation."""

    def __init__(
        self,
        glossary: Optional[List[str]] = None,
        patterns: Optional[List[Tuple[str, re.Pattern]]] = None,
    ):
        self.glossary: List[str] = list(glossary if glossary is not None else DEFAULT_PRODUCT_GLOSSARY)
        self.patterns = patterns or TECHNICAL_PATTERNS

    def get_glossary(self) -> List[str]:
        """Returns the current product glossary."""
        return list(self.glossary)

    def set_glossary(self, new_glossary: List[str]) -> None:
        """Updates the product glossary."""
        self.glossary = [term.strip() for term in new_glossary if term.strip()]

    def add_term_to_glossary(self, term: str) -> bool:
        """Adds a single term if not already in glossary."""
        cleaned = term.strip()
        if cleaned and cleaned not in self.glossary:
            self.glossary.append(cleaned)
            return True
        return False

    def extract_technical_terms(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts non-overlapping spans of technical terms, error codes, order IDs, URLs, and glossary products.
        """
        if not text:
            return []

        spans: List[Tuple[int, int, str, str]] = []
        occupied = [False] * len(text)

        # 1. Match glossary terms (longest string first, case-insensitive)
        for term in sorted(self.glossary, key=len, reverse=True):
            pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            for m in pattern.finditer(text):
                s, e = m.start(), m.end()
                if not any(occupied[s:e]):
                    for i in range(s, e):
                        occupied[i] = True
                    spans.append((s, e, "PRODUCT", m.group(0)))

        # 2. Match URLs, emails, error codes, tickets, and order IDs
        for label, pattern in self.patterns:
            for m in pattern.finditer(text):
                s, e = m.start(), m.end()
                if not any(occupied[s:e]):
                    for i in range(s, e):
                        occupied[i] = True
                    spans.append((s, e, label, m.group(0)))

        # Sort spans by starting index in original string
        spans.sort(key=lambda x: x[0])

        return [
            {
                "index": idx,
                "start": s,
                "end": e,
                "type": label,
                "value": val,
                "placeholder": f"ZXQTERM{idx}ZXQ",
            }
            for idx, (s, e, label, val) in enumerate(spans)
        ]

    def protect_terms(
        self, text: str, use_placeholders: bool = True
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Replaces technical terms with synthetic uppercase placeholders (e.g. ZXQTERM0ZXQ).
        """
        terms = self.extract_technical_terms(text)
        if not use_placeholders or not terms:
            return text, terms

        parts: List[str] = []
        last_idx = 0
        for item in terms:
            s, e = int(item["start"]), int(item["end"])
            parts.append(text[last_idx:s])
            parts.append(str(item["placeholder"]))
            last_idx = e
        parts.append(text[last_idx:])

        return "".join(parts), terms

    def restore_and_audit_terms(
        self,
        translated_text: str,
        extracted_terms: List[Dict[str, Any]],
        used_placeholders: bool = True,
    ) -> Dict[str, Any]:
        """
        Restores placeholders into the translated string and verifies verbatim term presence.
        """
        output = translated_text or ""
        restored_count = 0

        # Replace placeholders if placeholder masking was used
        if used_placeholders and extracted_terms:
            for item in extracted_terms:
                ph = str(item["placeholder"])
                val = str(item["value"])
                pattern = re.compile(re.escape(ph), re.IGNORECASE)
                if pattern.search(output):
                    output = pattern.sub(lambda _: val, output)
                    restored_count += 1

        # Check for any un-restored placeholder artifacts
        has_leftover_placeholder = bool(re.search(r"ZXQTERM\d*ZXQ", output, re.IGNORECASE))

        # Normalize redundant spaces while preserving newlines
        output = re.sub(r"[^\S\r\n]+", " ", output).strip()

        # Audit whether each extracted term appears in the final text (case-insensitive)
        missing_terms = [
            str(item["value"])
            for item in extracted_terms
            if str(item["value"]).lower() not in output.lower()
        ]

        return {
            "final_text": output,
            "extracted_terms": [
                {"type": t["type"], "value": t["value"]} for t in extracted_terms
            ],
            "restored_count": restored_count,
            "has_leftover_placeholder": has_leftover_placeholder,
            "missing_terms": missing_terms,
            "all_terms_preserved": (len(missing_terms) == 0 and not has_leftover_placeholder),
        }
