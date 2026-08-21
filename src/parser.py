import os

class ResumeParser:
    """
    Utility class to extract raw text from PDF and TXT resume files.
    """
    @staticmethod
    def extract_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()

        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
                from pypdf.errors import PdfStreamError
            except ImportError:
                raise ImportError(
                    "pypdf is required to read PDF files. Run 'pip install pypdf' in your terminal."
                )

            try:
                text = ""
                reader = PdfReader(file_path)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                
                if not text.strip():
                    raise ValueError("PDF contains no readable text (it might be an image-only scan).")
                
                return text.strip()

            except PdfStreamError:
                # If a text file was mistakenly named .pdf, read it cleanly as text fallback
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read().strip()
            except Exception as e:
                raise RuntimeError(f"Error parsing PDF file: {e}")

        else:
            raise ValueError(f"Unsupported file format '{ext}'. Please provide a .txt or .pdf file.")