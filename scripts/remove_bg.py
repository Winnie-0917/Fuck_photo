import argparse
from pathlib import Path
from rembg import remove


def remove_background(input_path: Path, output_path: Path) -> None:
    # 對單張圖片執行去背並輸出結果檔。
    data = input_path.read_bytes()
    result = remove(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)


def process_single_file(
    input_path: Path,
    output_path: Path | None,
    force_png: bool,
    replace_and_remove: bool,) -> None:
    # 處理單一檔案模式的輸出命名與刪檔規則。
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if force_png or replace_and_remove:
        output_path = input_path.with_suffix(".png")
    elif output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_no_bg.png")

    remove_background(input_path, output_path)

    if replace_and_remove and input_path.resolve() != output_path.resolve():
        input_path.unlink()
        print(f"Removed source: {input_path}")

    print(f"Done: {output_path}")


def process_directory(
    input_dir: Path,
    output_dir: Path | None,
    force_png: bool,
    replace_and_remove: bool,) -> None:
    # 批次處理資料夾內所有支援格式圖片。
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    if not force_png and not replace_and_remove and output_dir is None:
        output_dir = input_dir / "output_no_bg"

    valid_ext = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in valid_ext]

    if not files:
        print("No supported images found in directory.")
        return

    for file_path in files:
        if force_png or replace_and_remove:
            out_path = file_path.with_suffix(".png")
        else:
            out_path = output_dir / f"{file_path.stem}_no_bg.png"

        remove_background(file_path, out_path)

        if replace_and_remove and file_path.resolve() != out_path.resolve():
            file_path.unlink()
            print(f"Removed source: {file_path}")

        print(f"Done: {out_path}")


def build_parser() -> argparse.ArgumentParser:
    # 建立去背腳本的命令列參數定義。
    parser = argparse.ArgumentParser(description="Remove image background using rembg.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fuck_parser = subparsers.add_parser(
        "fuck",
        help="Remove background from an image file or all images in a directory.",
    )
    fuck_parser.add_argument("input", type=Path, help="Path to input image file or directory.")
    fuck_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help=(
            "Output file path for single image mode, "
            "or output directory path for directory mode."
        ),
    )
    mode_group = fuck_parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-f",
        "--force-png",
        action="store_true",
        help="Save with same file name but .png extension; do not delete source file.",
    )
    mode_group.add_argument(
        "-rf",
        "--replace-and-remove",
        action="store_true",
        help="Save with same file name but .png extension and delete source file.",
    )
    return parser


def main() -> None:
    # 解析參數後分流到單檔或資料夾去背流程。
    parser = build_parser()
    args = parser.parse_args()

    input_path: Path = args.input
    output_path: Path | None = args.output
    force_png: bool = args.force_png
    replace_and_remove: bool = args.replace_and_remove

    if (force_png or replace_and_remove) and output_path is not None:
        parser.error("-f/-rf cannot be used together with -o/--output.")

    if input_path.is_file():
        process_single_file(input_path, output_path, force_png, replace_and_remove)
    elif input_path.is_dir():
        process_directory(input_path, output_path, force_png, replace_and_remove)
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")


if __name__ == "__main__":
    main()
