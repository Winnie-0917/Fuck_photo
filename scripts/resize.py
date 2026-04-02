import argparse
from pathlib import Path
from PIL import Image


def parse_resolution_token(token: str) -> tuple[int, int]:
    # 解析並驗證寬/高解析度字串。
    parts = token.split("/")
    if len(parts) != 2:
        raise ValueError("Resolution format must be WIDTH/HEIGHT, e.g. 300/400")

    width_text, height_text = parts[0].strip(), parts[1].strip()
    if not width_text.isdigit() or not height_text.isdigit():
        raise ValueError("Resolution values must be positive integers")

    width, height = int(width_text), int(height_text)
    if width <= 0 or height <= 0:
        raise ValueError("Resolution values must be greater than 0")

    return width, height


def resize_image(input_path: Path, output_path: Path, resolution: tuple[int, int]) -> None:
    # 將圖片縮放為指定解析度並輸出為 PNG。
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as img:
        resized = img.resize(resolution, Image.Resampling.LANCZOS)
        resized.save(output_path, format="PNG")


def process_single_file(
    input_path: Path,
    output_path: Path | None,
    resolution: tuple[int, int],
    png_only: bool,) -> None:
    # 處理單一檔案縮放與輸出命名規則。
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if png_only and input_path.suffix.lower() != ".png":
        raise ValueError("--png-only mode requires PNG input file.")

    if output_path is None:
        width, height = resolution
        output_path = input_path.with_name(f"{input_path.stem}_{width}x{height}.png")

    resize_image(input_path, output_path, resolution)
    print(f"Done (resized only, no background removal): {output_path}")


def process_directory(
    input_dir: Path,
    output_dir: Path | None,
    resolution: tuple[int, int],
    png_only: bool,) -> None:
    # 批次處理資料夾內圖片並統一縮放。
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    width, height = resolution
    if output_dir is None:
        output_dir = input_dir / f"output_{width}x{height}"

    valid_ext = {".png"} if png_only else {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in valid_ext]

    if not files:
        print("No supported images found in directory.")
        return

    for file_path in files:
        out_path = output_dir / f"{file_path.stem}.png"
        resize_image(file_path, out_path, resolution)
        print(f"Done (resized only, no background removal): {out_path}")


def build_parser() -> argparse.ArgumentParser:
    # 建立縮放腳本的命令列參數定義。
    parser = argparse.ArgumentParser(description="Resize image(s) without background removal.")
    parser.add_argument("resolution", type=str, help="Resolution in WIDTH/HEIGHT format, e.g. 300/400")
    parser.add_argument("input", type=Path, help="Path to input image file or directory.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output file path for single image mode, or output directory for directory mode.",
    )
    parser.add_argument(
        "--png-only",
        action="store_true",
        help="Process only PNG files (useful after bg conversion in same directory).",
    )
    return parser


def main(raw_args: list[str] | None = None) -> None:
    # 解析參數後分流到單檔或資料夾縮放流程。
    parser = build_parser()
    args = parser.parse_args(raw_args)

    try:
        resolution = parse_resolution_token(args.resolution)
    except ValueError as exc:
        parser.error(str(exc))

    input_path: Path = args.input
    output_path: Path | None = args.output
    png_only: bool = args.png_only

    if input_path.is_file():
        process_single_file(input_path, output_path, resolution, png_only)
    elif input_path.is_dir():
        process_directory(input_path, output_path, resolution, png_only)
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")


if __name__ == "__main__":
    main()
