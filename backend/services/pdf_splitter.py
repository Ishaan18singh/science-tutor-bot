import os
import re
import fitz  # PyMuPDF

# Maharashtra Board style: "1. Some Basic Concepts of Chemistry"
CHAPTER_PATTERN = r'^(\d{1,2})\.\s+([A-Z][a-zA-Z\s,&\-]{4,60})$'

def detect_chapter_starts(pdf_path):
    doc = fitz.open(pdf_path)
    chapter_starts = []
    seen_numbers = set()

    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        for line in lines[:6]:  # chapter title appears near top of its first page
            match = re.match(CHAPTER_PATTERN, line)
            if match:
                chapter_num = match.group(1)
                title = match.group(2).strip()

                # Avoid duplicate detections (same chapter mentioned again later, e.g. in exercises)
                if chapter_num in seen_numbers:
                    continue

                seen_numbers.add(chapter_num)
                chapter_starts.append({
                    "chapter_num": chapter_num,
                    "title": title,
                    "start_page": page_num
                })
                break

    doc.close()
    # Sort by page number to keep order correct
    chapter_starts.sort(key=lambda x: x["start_page"])
    return chapter_starts


def split_pdf_by_chapters(pdf_path, output_base_folder, subject, class_name):
    print(f"📖 Scanning {pdf_path} for chapter breaks...")
    chapters = detect_chapter_starts(pdf_path)

    if not chapters:
        print("⚠️  No chapter patterns detected.")
        return []

    print(f"\n✅ Detected {len(chapters)} chapters:")
    for ch in chapters:
        print(f"   Chapter {ch['chapter_num']}: {ch['title']} (page {ch['start_page']})")

    confirm = input("\nDoes this list look correct? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted. Let's fix the pattern.")
        return []

    doc = fitz.open(pdf_path)
    results = []

    for i, ch in enumerate(chapters):
        start_page = ch["start_page"]
        end_page = chapters[i + 1]["start_page"] if i + 1 < len(chapters) else len(doc)

        chapter_text = ""
        for p in range(start_page, end_page):
            chapter_text += doc[p].get_text()

        safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', ch["title"]).strip()
        safe_title = re.sub(r'\s+', '_', safe_title).lower()
        folder_name = f"chapter{ch['chapter_num']}_{safe_title}"

        chapter_folder = os.path.join(output_base_folder, subject, class_name, folder_name)
        os.makedirs(chapter_folder, exist_ok=True)

        output_path = os.path.join(chapter_folder, "content.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(chapter_text)

        print(f"   💾 Saved: {output_path} ({len(chapter_text)} chars)")
        results.append(output_path)

    doc.close()
    return results


if __name__ == "__main__":
    print("="*60)
    print("PDF CHAPTER SPLITTER")
    print("="*60)

    pdf_path = input("Enter full path to your PDF: ").strip().strip('"')
    subject = input("Subject (physics/chemistry/mathematics/biology): ").strip().lower()
    class_name = input("Class (class11/class12): ").strip().lower()

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
    else:
        split_pdf_by_chapters(pdf_path, "../content", subject, class_name)
        print("\n🎉 Done! Check your content/ folders.")