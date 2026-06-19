import fitz

pdf_path = input("Enter full path to your PDF: ").strip().strip('"')

doc = fitz.open(pdf_path)
print(f"\nTotal pages: {len(doc)}\n")

start_page = int(input("Start page (0-indexed): ").strip())
end_page = int(input("End page: ").strip())

for page_num in range(start_page, min(end_page, len(doc))):
    text = doc[page_num].get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    print(f"--- Page {page_num} (first 12 lines) ---")
    for line in lines[:12]:
        print(f"   {repr(line)}")
    print()

doc.close()