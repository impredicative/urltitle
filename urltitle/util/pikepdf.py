"""Get PDF title using pikepdf in a separate process.

pikepdf==1.0.5 is not thread safe. Refer to https://github.com/pikepdf/pikepdf/issues/27
"""

from concurrent.futures import ProcessPoolExecutor
from io import BytesIO


def _get_pdf_title(pdf_bytes: bytes) -> str:
    import pikepdf  # This must be imported only here, or else it won't work.
    pdf = pikepdf.open(BytesIO(pdf_bytes))

    title = str(pdf.docinfo.get('/Title', '')).strip()
    if not title:
        with pdf.open_metadata() as metadata:
            title = str(metadata.get('dc:title', '')).strip()
    return title


def get_pdf_title(pdf_bytes: bytes) -> str:
    with ProcessPoolExecutor(max_workers=1) as executor:
        return next(executor.map(_get_pdf_title, [pdf_bytes]))
