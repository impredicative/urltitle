"""json utilities."""
import json


def get_ipynb_title(json_bytes: bytes) -> str:
    """Return the title from the bytes representing a JSON representation of an IPYNB notebook."""
    obj = json.loads(json_bytes)
    metadata = obj.get("metadata", {})
    title = metadata.get("colab", {}).get("name", "").strip()
    if title:
        kernel = metadata.get("kernelspec", {}).get("display_name")
        if kernel:
            title += f" ({kernel})"
    return title
