"""pikepdf utilities."""
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO


def _get_pdf_title(pdf_bytes: bytes) -> str:
    import pikepdf  # pylint: disable=import-outside-toplevel

    # Note: pikepdf must be imported only here. This is a workaround for https://github.com/pikepdf/pikepdf/issues/27

    pdf = pikepdf.open(BytesIO(pdf_bytes))

    title = str(pdf.docinfo.get("/Title", "")).strip()
    if not title:
        metadata = pdf.open_metadata()
        try:
            title = metadata.get("dc:title")
        except AttributeError:  # Workaround for https://github.com/pikepdf/pikepdf/issues/23
            pass
        else:
            title = str(title or "").strip()  # Workaround for https://github.com/pikepdf/pikepdf/issues/28
    title = " ".join(title.split())
    # Note: The above is a workaround for consecutive whitespace characters,
    # e.g. https://pdfs.semanticscholar.org/1d76/d4561b594b5c5b5250edb43122d85db07262.pdf
    return title


def get_pdf_title(pdf_bytes: bytes) -> str:
    """Return the PDF title using pikepdf in a separate process."""
    with ProcessPoolExecutor(max_workers=1) as executor:
        return next(executor.map(_get_pdf_title, [pdf_bytes]))
