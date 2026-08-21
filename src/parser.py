import os

class ResumeParser:
    @staticmethod
    def extract_text(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check whether the file is a text file or PDF
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()

        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                raise ImportError("Please install pypdf by running: pip install pypdf")

            try:
                reader = PdfReader(file_path)
                pages_text = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)

                full_text = "\n".join(pages_text).strip()
                if full_text:
                    return full_text

                raise ValueError("PDF has no readable text layer (might be a scanned image).")

            except Exception:
                # Fallback: if pypdf fails or a plain text file was renamed to .pdf
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read().strip()

        else:
            raise ValueError(f"Unsupported file extension '{ext}'. Only .txt and .pdf are supported.")