# agents/runner.py
import os
import tempfile

def save_files(file_dict: dict) -> str:
    """
    Save frontend files (HTML/CSS/JS) in a temporary folder.
    Returns folder path for live preview.
    """
    tmp_dir = tempfile.mkdtemp()
    for fname, content in file_dict.items():
        with open(os.path.join(tmp_dir, fname), "w") as f:
            f.write(content)
    return tmp_dir
