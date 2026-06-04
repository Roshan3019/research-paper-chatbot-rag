from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DIRECTORIES = [
    "data/input_pdfs",
    "data/extracted_text",
    "data/chunks",
    "data/vector_store",
    "src/config",
    "src/ingestion",
    "src/retrieval",
]

PACKAGE_DIRS = [
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "src/config",
    PROJECT_ROOT / "src/ingestion",
    PROJECT_ROOT / "src/retrieval",
]


def create_project_structure():
    print(f"Creating project structure under: {PROJECT_ROOT}")

    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

    for rel_path in DIRECTORIES:
        path = PROJECT_ROOT / rel_path
        path.mkdir(parents=True, exist_ok=True)
        print(f"   - Created: {path}")

    for package_dir in PACKAGE_DIRS:
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Package initializer\n", encoding="utf-8")
            print(f"   - Created package marker: {init_file}")

    readme_path = PROJECT_ROOT / "README.md"
    if not readme_path.exists():
        readme_path.write_text("# Research Paper Chat Bot (RAG)\n", encoding="utf-8")
        print(f"   - Created: {readme_path}")

    print("Project structure setup complete")


if __name__ == "__main__":
    create_project_structure()
