import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def extract_domain(text):
    """从Markdown Metadata中提取domain。"""
    match = re.search(
        r"^\s*domain:\s*([^\n]+)",
        text,
        flags=re.MULTILINE
    )
    if not match:
        return None

    return match.group(1).strip()


def detect_language(section_title, current_language=None):
    """根据语言主标题判断当前section语言。"""
    normalized = section_title.strip().lower()

    if normalized in {"english", "en"}:
        return "en"

    if normalized in {"中文", "chinese", "zh"}:
        return "zh"

    return current_language


def build_chunk(
    source_file,
    domain,
    language,
    section,
    content
):
    """构造统一知识Chunk结构。"""
    return {
        "source_file": source_file,
        "domain": domain,
        "language": language,
        "section": section,
        "content": content.strip()
    }


def load_knowledge_file(file_path):
    """读取单个Markdown知识文档并按标题切分。"""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Knowledge file not found: {file_path}"
        )

    if file_path.suffix.lower() != ".md":
        raise ValueError(
            f"Unsupported knowledge file type: {file_path.suffix}"
        )

    text = file_path.read_text(encoding="utf-8")
    domain = extract_domain(text)

    heading_pattern = re.compile(
        r"^(#{1,6})\s+(.+?)\s*$",
        flags=re.MULTILINE
    )

    matches = list(heading_pattern.finditer(text))

    if not matches:
        return []

    chunks = []
    current_language = None

    for index, match in enumerate(matches):
        heading_level = len(match.group(1))
        section_title = match.group(2).strip()

        current_language = detect_language(
            section_title,
            current_language
        )

        content_start = match.end()

        if index + 1 < len(matches):
            content_end = matches[index + 1].start()
        else:
            content_end = len(text)

        content = text[
            content_start:content_end
        ].strip()

        if not content:
            continue

        if section_title.lower() == "metadata / 元数据":
            continue

        if heading_level == 1 and section_title not in {
            "English",
            "中文"
        }:
            continue

        if section_title in {
            "English",
            "中文"
        }:
            continue

        chunk = build_chunk(
            source_file=file_path.name,
            domain=domain,
            language=current_language,
            section=section_title,
            content=content
        )

        chunks.append(chunk)

    return chunks


def load_knowledge_base(
    knowledge_dir=DEFAULT_KNOWLEDGE_DIR
):
    """读取knowledge目录下全部Markdown文档。"""
    knowledge_dir = Path(knowledge_dir)

    if not knowledge_dir.exists():
        raise FileNotFoundError(
            f"Knowledge directory not found: {knowledge_dir}"
        )

    markdown_files = sorted(
        knowledge_dir.glob("*.md")
    )

    chunks = []

    for file_path in markdown_files:
        chunks.extend(
            load_knowledge_file(file_path)
        )

    return chunks


def main():
    chunks = load_knowledge_base()

    source_files = sorted(
        {
            chunk["source_file"]
            for chunk in chunks
        }
    )

    print(
        f"Loaded documents: {len(source_files)}"
    )

    print(
        f"Generated chunks: {len(chunks)}"
    )

    print()

    for chunk in chunks:
        print(
            f"{chunk['source_file']} | "
            f"{chunk['language']} | "
            f"{chunk['domain']} | "
            f"{chunk['section']}"
        )


if __name__ == "__main__":
    main()