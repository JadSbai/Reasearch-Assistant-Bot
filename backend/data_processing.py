import re
import fitz


def is_likely_section_title(line):
    # Pattern to match section titles like '1INTRODUCTION', '2METHODS', etc.
    pattern = re.compile(r'^\d+\s*[A-Z].*')
    return pattern.match(line)


def is_new_paragraph(line, previous_line):
    # Check if the previous line ends with a period and the current line starts with an uppercase letter
    return previous_line.strip().endswith('.') and line.strip() and line.strip()[0].isupper()


def extract_text_with_sections(pdf_path):
    document = fitz.open(pdf_path)
    sections = {}
    current_section = None
    full_text = ""  # Variable to store the full plaintext

    for page in document:
        # Dimensions of the page
        page_height = page.rect.height
        header_threshold = page_height * 0.1  # Top 10% for header
        footer_threshold = page_height * 0.95  # Bottom 10% for footer
        try:
            # Attempt to find tables on the page
            tables = page.find_tables()
            table_bboxes = [fitz.Rect(table.bbox) for table in tables if table]
        except Exception as e:
            # Handle exceptions and continue processing the rest of the document
            print(f"Error processing tables on page {page.number}: {e}")
            table_bboxes = []
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda block: (block[1], block[0]))  # Sort by y0, then x0

        for block in blocks:
            x0, y0, x1, y1, text, block_type, block_no = block
            text = text.strip()
            full_text += text + "\n\n"  # Append the text to the full text
            word_counts = len(text.split())

            # Exclude headers and footers
            if y0 < header_threshold or y1 > footer_threshold:
                continue
            # Check if block is within any table bbox
            block_bbox = fitz.Rect(block[:4])
            if any(table_bbox.intersects(block_bbox) for table_bbox in table_bboxes):
                continue  # Skip this block as it's part of a table

            if is_likely_section_title(text):
                current_section = text
                sections[current_section] = []
            elif current_section and word_counts >= 20:
                sections[current_section].append(text)

    document.close()
    return sections, full_text


def extract_title_and_authors(pdf_path):
    document = fitz.open(pdf_path)
    first_page = document[0]
    blocks = first_page.get_text("blocks")
    blocks.sort(key=lambda block: (block[1], block[0]))  # Sort by y0, then x0

    # Identify the header region (e.g., top 10% of the page)
    header_threshold = first_page.rect.height * 0.1

    title, authors = None, None
    for _, y0, _, _, text, _, _ in blocks:
        if y0 < header_threshold:
            continue  # Skip header
        if 'ABSTRACT' in text.upper():
            break  # Stop at the ABSTRACT section
        if not title and len(text.split()) > 5:
            title = text
        elif title and not authors:
            authors = text
        elif authors:
            authors += text  # Stop at the next section

    document.close()
    return title, authors


def insert_and_process_pdf(mongo_handler, pdf_path, title=None, author=None):
    # Insert the whole paper
    sections, plain_text = extract_text_with_sections(pdf_path)
    if not title or not author:
        title, author = extract_title_and_authors(pdf_path)
    paper_id = mongo_handler.insert_paper(title, pdf_path, plain_text, author)

    cleaned_sections = {}
    for section in sections:
        # Remove digits and newline characters
        clean_title = re.sub(r'\d+\n', '', section)
        if clean_title != "REFERENCES":
            cleaned_sections[clean_title] = sections[section]

    # Iterate over sections and paragraphs, inserting each paragraph
    prev_paragraph_id = None
    for section, paragraphs in cleaned_sections.items():
        for paragraph_text in paragraphs:
            paragraph_id = mongo_handler.insert_paragraph(paper_id, paragraph_text, section, prev_paragraph_id)
            if prev_paragraph_id is not None:
                mongo_handler.update_paragraph_next(prev_paragraph_id, paragraph_id)
            prev_paragraph_id = paragraph_id
    return cleaned_sections, title, author
