"""Parse ANMS Test Specification docx into structured JSON."""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

NS_URI = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
DOCX_PATH = sys.argv[1] if len(sys.argv) > 1 else "../Downloads/ANMS_TestSpec_revC_em.docx"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "../output/anms_test_spec.json"

@dataclass
class Paragraph:
    index: int; text: str; is_bold: bool; has_numbering: bool
    is_hyperlink: bool; hyperlink_rel_id: str = ""

@dataclass
class TestCase:
    id: str = ""; title: str = ""; section_id: str = ""; section_path: str = ""
    purpose: str = ""; requirements_verified: str = ""; assumptions: str = ""
    test_data: str = ""; test_scripts: str = ""; preconditions: str = ""
    test_steps: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    test_artifacts: List[str] = field(default_factory=list)
    type: str = ""

SECTION_LABELS = frozenset([
    "Test Case Purpose", "Requirements Verified", "Assumptions",
    "Test Data", "Test Scripts", "Preconditions", "Test Steps",
    "Expected Outcome(s)", "Test Artifacts",
])

def _get_text(elem) -> str:
    parts = [elem.text or ""]
    for ch in elem:
        parts.append(_get_text(ch))
        parts.append(ch.tail or "")
    return "".join(parts)

def _is_bold(p) -> bool:
    for r in p.findall(f".//{{{NS_URI}}}r"):
        rpr = r.find(f"{{{NS_URI}}}rPr")
        if rpr is not None and (rpr.find(f"{{{NS_URI}}}b") is not None or rpr.find(f"{{{NS_URI}}}bCs") is not None):
            return True
    return False

def _has_numbering(p) -> bool:
    pPr = p.find(f"{{{NS_URI}}}pPr")
    if pPr is not None and pPr.find(f"{{{NS_URI}}}numPr") is not None: return True
    for hl in p.findall(f"{{{NS_URI}}}hyperlink"):
        for r in hl.findall(f"{{{NS_URI}}}r"):
            rpr = r.find(f"{{{NS_URI}}}rPr")
            if rpr is not None and rpr.find(f"{{{NS_URI}}}numPr") is not None: return True
    return False

def _get_hyperlink(p) -> tuple:
    hl = p.find(f"{{{NS_URI}}}hyperlink")
    if hl is None: return False, ""
    rid = hl.find(f"{{{REL_NS}}}id")
    return True, rid.get("val","") if rid is not None else ""

def parse_docx(path: str) -> tuple:
    with zipfile.ZipFile(path) as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(doc_xml)
    pars = root.findall(f".//{{{NS_URI}}}p")
    paragraphs: List[Paragraph] = []
    idx = 0
    for p in pars:
        text = _get_text(p).strip()
        if not text:
            idx += 1; continue
        paragraphs.append(Paragraph(
            index=idx, text=text, is_bold=_is_bold(p),
            has_numbering=_has_numbering(p),
            is_hyperlink=_get_hyperlink(p)[0],
            hyperlink_rel_id=_get_hyperlink(p)[1],
        ))
        idx += 1
    tables: List[List[List[str]]] = []
    for tbl in root.findall(f".//{{{NS_URI}}}tbl"):
        rows: List[List[str]] = []
        for tr in tbl.findall(f"{{{NS_URI}}}tr"):
            cells: List[str] = []
            for tc in tr.findall(f"{{{NS_URI}}}tc"):
                ct = _get_text(tc).strip()
                if ct: cells.append(ct)
            if cells: rows.append(cells)
        if rows: tables.append(rows)
    return paragraphs, tables

def extract_toc(paragraphs: List[Paragraph]) -> Dict[str, tuple]:
    toc: Dict[str, tuple] = {}
    for p in paragraphs:
        m = re.search(r"^(\d+(?:\.\d+)?)\s*(.+?)\s+PAGEREF", p.text)
        if m:
            title = re.sub(r"\s+", " ", m.group(2).strip())
            if 1 < len(title) < 80:
                toc[m.group(1)] = (title, p.index)
    return toc

def extract_toc_paragraphs(paragraphs: List[Paragraph]) -> List[tuple]:
    """Extract TOC paragraph text for matching against body paragraphs."""
    results = []
    for p in paragraphs:
        m = re.search(r"^(\d+(?:\.\d+)?)\s*(.+?)\s+PAGEREF", p.text)
        if m:
            title = re.sub(r"\s+", " ", m.group(2).strip())
            if 1 < len(title) < 80:
                results.append((m.group(1), title, p.index))
    return results

def is_test_case_header(text: str) -> bool:
    return bool(re.match(r"^ANMS_(FUN|EXP)_[A-Z_]+_\d+\s*\(.+", text))

def extract_test_id(text: str) -> Optional[str]:
    m = re.match(r"^(ANMS_(?:FUN|EXP)_[A-Z_]+_\d+)\s*\(.+", text)
    return m.group(1) if m else None

def extract_test_title(text: str) -> Optional[str]:
    m = re.match(r"^(?:ANMS_(?:FUN|EXP)_[A-Z_]+_\d+)\s*\((.+)\)", text)
    return m.group(1) if m else None

def test_case_type(test_id: str) -> str:
    return "exploratory" if "EXP" in test_id else "functional"

def assign_section(test_case_idx: int, paragraphs: List[Paragraph],
                   toc_paras: List[tuple]) -> tuple:
    """Match test case to TOC entry by comparing body paragraph text to TOC title."""
    # Build stripped TOC title -> (sec_id, title) mapping
    stripped: Dict[str, tuple] = {}
    for sid, title, _ in toc_paras:
        clean = re.sub(r"\s+", " ", title).strip()
        stripped[clean] = (sid, title)

    best: Optional[tuple] = None
    best_dist = float("inf")
    for i in range(max(0, test_case_idx - 300), test_case_idx):
        p = paragraphs[i]
        clean = re.sub(r"\s+", " ", p.text).strip()
        if clean in stripped:
            dist = test_case_idx - i
            if dist < best_dist:
                best_dist = dist
                best = stripped[clean]
                if best_dist <= 30:
                    break
    return (best[0], best[1]) if best else ("", "")

def parse_test_case(header_idx: int, paragraphs: List[Paragraph],
                    toc_paras: List[tuple]) -> TestCase:
    tc = TestCase()
    hdr = paragraphs[header_idx].text
    tc.id = extract_test_id(hdr) or ""
    tc.title = extract_test_title(hdr) or ""
    tc.type = test_case_type(tc.id)
    sec_id, sec_title = assign_section(header_idx, paragraphs, toc_paras)
    tc.section_id = sec_id
    tc.section_path = f"{sec_id} {sec_title}".strip() if sec_id else ""

    current_label: Optional[str] = None
    sub_group: Optional[str] = None

    for j in range(header_idx + 1, len(paragraphs)):
        p = paragraphs[j]
        ptext = p.text
        if is_test_case_header(ptext):
            break
        if ptext in SECTION_LABELS:
            current_label = ptext; sub_group = None; continue

        if current_label == "Test Case Purpose" and not tc.purpose:
            tc.purpose = ptext
        elif current_label == "Requirements Verified":
            tc.requirements_verified += (" " + ptext) if tc.requirements_verified else ptext
        elif current_label == "Assumptions":
            tc.assumptions += (" " + ptext) if tc.assumptions else ptext
        elif current_label == "Test Data":
            if p.is_bold:
                tc.test_data += f"\nDATA_ITEM: {ptext}"
            elif tc.test_data and not tc.test_data.endswith("DATA_ITEM:"):
                tc.test_data += " " + ptext
            elif not tc.test_data:
                tc.test_data = ptext
        elif current_label == "Test Scripts":
            tc.test_scripts += (" " + ptext) if tc.test_scripts else ptext
        elif current_label == "Preconditions":
            tc.preconditions += (" " + ptext) if tc.preconditions else ptext
        elif current_label == "Test Steps":
            if p.is_bold and ptext:
                sub_group = ptext
            else:
                tc.test_steps.append(f"{sub_group}: {ptext}" if sub_group else ptext)
        elif current_label == "Expected Outcome(s)":
            if "This test is considered" not in ptext:
                tc.expected_outcomes.append(ptext)
        elif current_label == "Test Artifacts":
            tc.test_artifacts.append(ptext)
        elif current_label is None and not tc.purpose:
            tc.purpose = ptext
    return tc

def classify_table(rows: List[List[str]]) -> str:
    if not rows: return "empty"
    hdr = " ".join(rows[0]).lower()
    if "revision" in hdr: return "change_log"
    if "property" in hdr and "value" in hdr: return "metadata"
    if any(w in hdr for w in ["acronym", "term", "definition", "source"]): return "glossary"
    if any(w in hdr for w in ["document number", "sdr", "controlling doc"]): return "reference_doc_1"
    if any(w in hdr for w in ["identifier", "description", "sr-", "doc-00"]): return "reference_doc_2"
    if "object type" in hdr or "obj_metadata" in hdr: return "schema_object_metadata"
    if "attribute" in hdr and "value" in hdr: return "schema_attribute"
    if "rule" in hdr and "enum" in hdr: return "test_data_rules"
    return "unknown"

def build_output(docx_path, paragraphs, test_cases, tables, toc_paras):
    sections = []
    for sid, title, _ in sorted(toc_paras):
        parts = sid.split(".")
        sections.append({"id": sid, "title": title, "depth": len(parts),
                        "parent_id": ".".join(parts[:-1]) if len(parts) > 1 else None})
    classified = []
    for i, rows in enumerate(tables):
        classified.append({"index": i+1, "type": classify_table(rows),
                          "header": rows[0], "total_rows": len(rows),
                          "sample_row": rows[1] if len(rows)>1 else None})
    return {
        "meta": {"title": "ANMS Test Specification (TS)", "version": "2.0",
                "revision": "C", "date": "August 2025",
                "source_file": os.path.abspath(docx_path),
                "total_paragraphs": len(paragraphs), "total_tables": len(tables),
                "total_test_cases": len(test_cases),
                "tables": {"count": len(classified), "entries": classified}},
        "sections": sections,
        "test_cases": [{
            "id": tc.id, "title": tc.title, "section_id": tc.section_id,
            "section_path": tc.section_path, "type": tc.type,
            "purpose": tc.purpose, "requirements_verified": tc.requirements_verified,
            "assumptions": tc.assumptions, "test_data": tc.test_data.strip(),
            "test_scripts": tc.test_scripts.strip(), "preconditions": tc.preconditions,
            "test_steps": tc.test_steps, "expected_outcomes": tc.expected_outcomes,
            "test_artifacts": tc.test_artifacts,
        } for tc in test_cases],
    }

def main():
    docx_path = os.path.normpath(DOCX_PATH)
    print(f"Parsing: {docx_path}")
    paragraphs, tables = parse_docx(docx_path)
    print(f"  Paragraphs: {len(paragraphs)}  |  Tables: {len(tables)}")

    toc_paras: List[tuple] = []
    for p in paragraphs:
        m = re.search(r"^(\d+(?:\.\d+)?)\s*(.+?)\s+PAGEREF", p.text)
        if m:
            title = re.sub(r"\s+", " ", m.group(2).strip())
            if 1 < len(title) < 80:
                toc_paras.append((m.group(1), title, p.index))
    print(f"  TOC sections: {len(toc_paras)}")

    anchors = [i for i, p in enumerate(paragraphs) if is_test_case_header(p.text)]
    print(f"  Test case headers found: {len(anchors)}")

    test_cases = []
    for a in anchors:
        tc = parse_test_case(a, paragraphs, toc_paras)
        if tc.id: test_cases.append(tc)
    print(f"  Parsed: {len(test_cases)}")

    out = build_output(docx_path, paragraphs, test_cases, tables, toc_paras)
    out_dir = os.path.dirname(os.path.abspath(OUT_PATH))
    if out_dir: os.makedirs(out_dir, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUT_PATH}")
    print(f"  Sections: {len(out['sections'])}  |  Test cases: {len(out['test_cases'])}")

    type_counts = {}
    for tc in test_cases:
        type_counts[tc.type] = type_counts.get(tc.type, 0) + 1
    print(f"  By type: {type_counts}")

    section_counts: Dict[str, int] = {}
    for tc in test_cases:
        s = tc.section_id or "uncategorized"
        section_counts[s] = section_counts.get(s, 0) + 1
    print(f"  By section: {dict(sorted(section_counts.items()))}")

if __name__ == "__main__":
    main()
