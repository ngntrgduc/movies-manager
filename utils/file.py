from pathlib import Path

def convert_bytes(size: int) -> str:
    """Convert bytes to KB, MB, GB, TB."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f'{size:.1f} {unit}'
        size /= 1024

def get_file_size(file: str | Path) -> int:
    """Return file size as raw bytes (int)."""

    if isinstance(file, str):
        file = Path(file)

    return file.stat().st_size

def get_last_modified(file: Path) -> str:
    """Return the last modified timestamp of a file."""
    from datetime import datetime
    return f'{datetime.fromtimestamp(file.stat().st_mtime):%Y-%m-%d %X}'

# if __name__ == '__main__':
#     data_folder = Path('data/')
#     total = 0
#     for data_file in data_folder.iterdir():
#         # print(f'{data_file}: {get_file_size(data_file, human_readable=True)}')
#         total += get_file_size(data_file)
#     print(convert_bytes(total))