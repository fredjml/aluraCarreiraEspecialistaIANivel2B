import html
import re
import sys
import zipfile
from pathlib import Path


NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def esc(value):
    return html.escape(value, quote=False)


def run(text, bold=False, italic=False):
    props = ""
    if bold:
        props += "<w:b/>"
    if italic:
        props += "<w:i/>"
    return f"<w:r><w:rPr>{props}</w:rPr><w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"


def inline(text):
    output = []
    pattern = re.compile(r"(\*\*.*?\*\*|\*.*?\*|`.*?`)")
    position = 0
    for match in pattern.finditer(text):
        if match.start() > position:
            output.append(run(text[position:match.start()]))
        token = match.group(0)
        if token.startswith("**"):
            output.append(run(token[2:-2], bold=True))
        elif token.startswith("*"):
            output.append(run(token[1:-1], italic=True))
        else:
            output.append(run(token[1:-1]))
        position = match.end()
    if position < len(text):
        output.append(run(text[position:]))
    return "".join(output)


def paragraph(text, style=None):
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ""
    return f"<w:p><w:pPr>{style_xml}</w:pPr>{inline(text)}</w:p>"


def table(rows):
    if not rows:
        return ""
    columns = max(len(row) for row in rows)
    grid = "".join("<w:gridCol w:w=\"2200\"/>" for _ in range(columns))
    body = [f"<w:tbl><w:tblPr><w:tblW w:w=\"9360\" w:type=\"dxa\"/><w:tblInd w:w=\"120\" w:type=\"dxa\"/><w:tblCellMar><w:top w:w=\"80\" w:type=\"dxa\"/><w:left w:w=\"120\" w:type=\"dxa\"/><w:bottom w:w=\"80\" w:type=\"dxa\"/><w:right w:w=\"120\" w:type=\"dxa\"/></w:tblCellMar><w:tblBorders><w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/><w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/><w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/></w:tblBorders></w:tblPr><w:tblGrid>{grid}</w:tblGrid>"]
    for row_index, row in enumerate(rows):
        cells = []
        for value in row + [""] * (columns - len(row)):
            shading = '<w:shd w:fill="D9EAF7"/>' if row_index == 0 else ""
            cells.append(f"<w:tc><w:tcPr>{shading}</w:tcPr>{paragraph(value)}</w:tc>")
        row_props = '<w:tblHeader/><w:cantSplit/>' if row_index == 0 else '<w:cantSplit/>'
        body.append(f"<w:tr><w:trPr>{row_props}</w:trPr>{''.join(cells)}</w:tr>")
    body.append("</w:tbl>")
    return "".join(body)


def parse_markdown(source):
    lines = source.splitlines()
    blocks = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.strip() == "<!-- PAGEBREAK -->":
            blocks.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
            index += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            blocks.append(paragraph(line[level:].strip(), f"Heading{min(level, 3)}"))
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+:?", lines[index + 1]):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                values = [item.strip() for item in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", value) for value in values):
                    rows.append(values)
                index += 1
            blocks.append(table(rows))
            continue
        if re.match(r"^[-*] ", line):
            blocks.append(paragraph(re.sub(r"^[-*] ", "", line), "ListBullet"))
            index += 1
            continue
        if re.match(r"^\d+\. ", line):
            blocks.append(paragraph(re.sub(r"^\d+\. ", "", line), "ListNumber"))
            index += 1
            continue
        collected = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith("#") and not lines[index].startswith("|") and not re.match(r"^[-*] |^\d+\. ", lines[index]):
            collected.append(lines[index].strip())
            index += 1
        blocks.append(paragraph(" ".join(collected)))
    return "".join(blocks)


def document_xml(body):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{NS}"><w:body>{body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/></w:sectPr></w:body></w:document>'''


def styles_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{NS}"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr></w:style><w:style w:type="paragraph" w:styleId="ListNumber"><w:name w:val="List Number"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr></w:style></w:styles>'''


def create_docx(markdown_path, output_path):
    source = Path(markdown_path).read_text(encoding="utf-8")
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    document_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document_xml(parse_markdown(source)))
        archive.writestr("word/styles.xml", styles_xml())
        archive.writestr("word/_rels/document.xml.rels", document_rels)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python gerar_relatorio_docx.py entrada.md saida.docx")
    create_docx(sys.argv[1], sys.argv[2])
