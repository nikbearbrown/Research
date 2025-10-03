import re
import fitz  # pip install pymupdf

QUESTION_RE = re.compile(r"^\s*\d+\.\s*")  

def _gather_lines_and_images(page):
    """
    Return:
      lines: [(text, Rect)] in reading order
      img_rects: [Rect] for image blocks on the page
    """
    d = page.get_text("dict")  # blocks -> lines -> spans
    lines = []
    img_rects = []
    for b in d.get("blocks", []):
        btype = b.get("type", 0)
        if btype == 1:
            # image block with bbox
            if "bbox" in b and b["bbox"]:
                img_rects.append(fitz.Rect(*b["bbox"]))
            continue
        if btype != 0:
            continue  # skip non-text, non-image
        for ln in b.get("lines", []):
            spans = ln.get("spans", [])
            if not spans:
                continue
            x0 = min(s["bbox"][0] for s in spans)
            y0 = min(s["bbox"][1] for s in spans)
            x1 = max(s["bbox"][2] for s in spans)
            y1 = max(s["bbox"][3] for s in spans)
            text = "".join(s.get("text", "") for s in spans)
            lines.append((text, fitz.Rect(x0, y0, x1, y1)))
    lines.sort(key=lambda t: (t[1].y0, t[1].x0))
    return lines, img_rects

def _nearest_line_index(lines, target_rect):
    cy = (target_rect.y0 + target_rect.y1) / 2.0
    best_i, best_d = None, 1e18
    for i, (_, r) in enumerate(lines):
        d = abs(((r.y0 + r.y1) / 2.0) - cy)
        if d < best_d:
            best_i, best_d = i, d
    return best_i

def _find_prev_question_idx(lines, start_idx):
    for i in range(start_idx, -1, -1):
        if QUESTION_RE.match(lines[i][0].strip()):
            return i
    return None

def _find_next_question_idx(lines, start_idx):
    for i in range(start_idx, len(lines)):
        if QUESTION_RE.match(lines[i][0].strip()):
            return i
    return None

def _union_rect_of_lines(lines, i0, i1):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for _, r in lines[i0:i1+1]:
        xs0.append(r.x0); ys0.append(r.y0); xs1.append(r.x1); ys1.append(r.y1)
    return fitz.Rect(min(xs0), min(ys0), max(xs1), max(ys1))

def _pad(rect, m, page_rect):
    return fitz.Rect(
        max(page_rect.x0, rect.x0 - m),
        max(page_rect.y0, rect.y0 - m),
        min(page_rect.x1, rect.x1 + m),
        min(page_rect.y1, rect.y1 + m),
    )

def extract_qna_by_solution(
    pdf_path="/content/UniversityPhysicsVolume1-Ch10.docx.pdf",
    dpi=300,
    search_text="Solution",
    margin_pt=10,          # a little more padding
    extra_down=80,         # push bottom to avoid clipping equations
    pages="all",
):
    """
    QUESTION: from nearest preceding '^\d+\.' line up to just above 'Solution'
    ANSWER:   from **'Solution' line (included)** down to next '^\d+\.' (or page end),
              also union any image blocks in that vertical span, plus extra bottom.
    """
    doc = fitz.open(pdf_path)
    page_indices = range(len(doc)) if pages == "all" else pages

    for pi in page_indices:
        page = doc[pi]
        lines, img_rects = _gather_lines_and_images(page)

        sol_rects = page.search_for(search_text)  # list[Rect]
        if not sol_rects:
            continue

        for k, sol_r in enumerate(sol_rects, start=1):
            sol_idx = _nearest_line_index(lines, sol_r)
            if sol_idx is None:
                continue

            # ----- QUESTION -----
            q_start = _find_prev_question_idx(lines, sol_idx)
            if q_start is None:
                continue
            q_end = max(q_start, sol_idx - 1)
            q_rect = _union_rect_of_lines(lines, q_start, q_end)

            # ----- ANSWER -----
            # Include "Solution" line itself
            a_start = sol_idx  # CHANGED: include Solution
            nxt_q = _find_next_question_idx(lines, sol_idx + 1)
            a_end = (nxt_q - 1) if (nxt_q is not None and nxt_q > a_start) else (len(lines) - 1)

            if a_start <= a_end:
                a_rect = _union_rect_of_lines(lines, a_start, a_end)
            else:
                a_rect = fitz.Rect(sol_r.x0, sol_r.y1, sol_r.x1, sol_r.y1 + 40)

            # Also include any image blocks that overlap the answer's vertical band
            # (equations are often images)
            if a_rect is not None:
                y0, y1 = a_rect.y0, a_rect.y1
                add_imgs = [ib for ib in img_rects if not (ib.y1 < y0 or ib.y0 > y1)]
                for ib in add_imgs:
                    a_rect |= ib
                # push bottom a bit more
                a_rect = fitz.Rect(a_rect.x0, a_rect.y0, a_rect.x1, min(page.rect.y1, a_rect.y1 + extra_down))

            # pad & clamp
            pagebox = page.rect
            q_rect = _pad(q_rect, margin_pt, pagebox)
            a_rect = _pad(a_rect, margin_pt, pagebox)

            # ----- render -----
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            q_pix = page.get_pixmap(matrix=mat, clip=q_rect, alpha=False)
            a_pix = page.get_pixmap(matrix=mat, clip=a_rect, alpha=False)

            q_fname = f"page{pi+1}_sol{k}_question.png"
            a_fname = f"page{pi+1}_sol{k}_answer.png"
            save_path = "Evaluating_LLM_Performance_on_Physics_Problems/University_Physics_Vol_1_Student_Resources/Chapter_10_QA/"
            q_pix.save(save_path+q_fname)
            a_pix.save(save_path+a_fname)

def get_pdf_page_count(file_path):
    with fitz.open(file_path) as pdf_file:
        return pdf_file.page_count

if __name__ == "__main__":
    path = "Evaluating_LLM_Performance_on_Physics_Problems/University_Physics_Vol_1_Student_Resources/UniversityPhysicsVolume1-Ch10.docx (1).pdf"
    num_of_pages = get_pdf_page_count(path)
    extract_qna_by_solution(
        pdf_path=path,
        dpi=450,            
        search_text="Solution",
        margin_pt=10,
        extra_down=0,
        pages="all",       
    )
    