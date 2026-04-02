import argparse
from datetime import datetime
from pathlib import Path

from PIL import Image


SUPPORTED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def format_bytes(value: int) -> str:
    # 將位元組大小轉成人類可讀格式。
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{value} B"


def format_time(ts: float) -> str:
    # 將時間戳格式化為固定日期時間字串。
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def has_alpha_channel(img: Image.Image) -> bool:
    # 檢查圖片是否包含透明通道資訊。
    if img.mode in {"RGBA", "LA"}:
        return True
    return "transparency" in img.info


def collect_image_info(path: Path) -> dict[str, str]:
    # 收集單張圖片的完整中繼資料。
    stat = path.stat()

    with Image.open(path) as img:
        width, height = img.size
        info = {
            "path": str(path),
            "name": path.name,
            "format": str(img.format),
            "mode": img.mode,
            "resolution": f"{width}x{height}",
            "pixels": str(width * height),
            "alpha": "yes" if has_alpha_channel(img) else "no",
            "size": format_bytes(stat.st_size),
            "created": format_time(stat.st_ctime),
            "modified": format_time(stat.st_mtime),
        }

    return info


def print_image_info(info: dict[str, str]) -> None:
    # 以固定欄位格式輸出單張圖片資訊。
    print("-" * 72)
    print(f"Path      : {info['path']}")
    print(f"Name      : {info['name']}")
    print(f"Format    : {info['format']}")
    print(f"Mode      : {info['mode']}")
    print(f"Resolution: {info['resolution']}")
    print(f"Pixels    : {info['pixels']}")
    print(f"Alpha     : {info['alpha']}")
    print(f"Size      : {info['size']}")
    print(f"Created   : {info['created']}")
    print(f"Modified  : {info['modified']}")


def list_images(target: Path, recursive: bool) -> list[Path]:
    # 取得目標路徑下符合支援格式的圖片清單。
    if target.is_file():
        if target.suffix.lower() in SUPPORTED_EXT:
            return [target]
        raise ValueError(f"Unsupported image format: {target}")

    if not target.is_dir():
        raise FileNotFoundError(f"Input path not found: {target}")

    pattern = "**/*" if recursive else "*"
    files = [p for p in target.glob(pattern) if p.is_file() and p.suffix.lower() in SUPPORTED_EXT]
    return sorted(files)


def build_parser() -> argparse.ArgumentParser:
    # 建立 ls 模式的命令列參數定義。
    parser = argparse.ArgumentParser(description="List detailed metadata for image files.")
    parser.add_argument("input", type=Path, help="Path to an image file or directory.")
    parser.add_argument(
        "-R",
        "--recursive",
        action="store_true",
        help="Recursively scan subdirectories when input is a directory.",
    )
    return parser


def main(raw_args: list[str] | None = None) -> None:
    # 執行 ls 主流程並逐一輸出圖片詳細資訊。
    parser = build_parser()
    args = parser.parse_args(raw_args)

    paths = list_images(args.input, args.recursive)
    if not paths:
        print("No supported images found.")
        return

    print(f"Found {len(paths)} image(s)")
    for path in paths:
        try:
            info = collect_image_info(path)
            print_image_info(info)
        except Exception as exc:
            print("-" * 72)
            print(f"Path      : {path}")
            print(f"Error     : {exc}")


if __name__ == "__main__":
    main()
