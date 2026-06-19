import os
import fitz  # PyMuPDF

# ── Chapter list with PRINTED page numbers (from Contents page) ──
CHAPTERS = [
    {"num": 1,  "title": "Some Basic Concepts of Chemistry", "start": 1,   "end": 12},
    {"num": 2,  "title": "Introduction to Analytical Chemistry", "start": 13,  "end": 26},
    {"num": 3,  "title": "Basic Analytical Techniques", "start": 27,  "end": 34},
    {"num": 4,  "title": "Structure of Atom", "start": 35,  "end": 54},
    {"num": 5,  "title": "Chemical Bonding", "start": 55,  "end": 80},
    {"num": 6,  "title": "Redox Reactions", "start": 81,  "end": 92},
    {"num": 7,  "title": "Modern Periodic Table", "start": 93,  "end": 109},
    {"num": 8,  "title": "Elements of Group 1 and 2", "start": 110, "end": 122},
    {"num": 9,  "title": "Elements of Group 13 14 and 15", "start": 123, "end": 134},
    {"num": 10, "title": "States of Matter", "start": 135, "end": 159},
    {"num": 11, "title": "Adsorption and Colloids", "start": 160, "end": 173},
    {"num": 12, "title": "Chemical Equilibrium", "start": 174, "end": 189},
    {"num": 13, "title": "Nuclear Chemistry and Radioactivity", "start": 190, "end": 203},
    {"num": 14, "title": "Basic Principles of Organic Chemistry", "start": 204, "end": 232},
    {"num": 15, "title": "Hydrocarbons", "start": 233, "end": 260},
    {"num": 16, "title": "Chemistry in Everyday Life", "start": 261, "end": 270},
]

# Offset between printed page number and actual PDF page index
# (We found: printed page "1" = PDF index 9, so offset = 8)
PAGE_OFFSET = 8


def safe_folder_name(num, title):
    safe = "".join(c if c.isalnum() or c == " " else "" for c in title)
    safe = "_".join(safe.lower().split())
    return f"chapter{num}_{safe}"


def split_pdf(pdf_path, output_base, subject, class_name):
    doc = fitz.open(pdf_path)
    print(f"📖 Total PDF pages: {len(doc)}\n")

    for ch in CHAPTERS:
        start_idx = ch["start"] + PAGE_OFFSET - 1   # -1 because 0-indexed
        end_idx = ch["end"] + PAGE_OFFSET            # exclusive end

        # Safety clamp
        start_idx = max(0, start_idx)
        end_idx = min(len(doc), end_idx)

        chapter_text = ""
        for p in range(start_idx, end_idx):
            chapter_text += doc[p].get_text()

        folder_name = safe_folder_name(ch["num"], ch["title"])
        chapter_folder = os.path.join(output_base, subject, class_name, folder_name)
        os.makedirs(chapter_folder, exist_ok=True)

        output_path = os.path.join(chapter_folder, "content.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(chapter_text)

        print(f"✅ Chapter {ch['num']}: {ch['title']}")
        print(f"   PDF pages {start_idx}-{end_idx} → {len(chapter_text)} chars")
        print(f"   Saved: {output_path}\n")

    doc.close()
    print("🎉 All chapters split and saved successfully!")


if __name__ == "__main__":
    pdf_path = input("Enter full path to your PDF: ").strip().strip('"')
    subject = input("Subject: ").strip().lower()
    class_name = input("Class (class11/class12): ").strip().lower()

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
    else:
        split_pdf(pdf_path, "../content", subject, class_name)