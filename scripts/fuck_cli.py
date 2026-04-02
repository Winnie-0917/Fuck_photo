import subprocess
import sys
from pathlib import Path


HELP_FILE = Path(__file__).with_name("help.txt")


def is_help_request(args: list[str]) -> bool:
    # 判斷參數中是否包含 help 相關旗標。
    help_aliases = {"/help", "/h", "/?", "-h", "--help"}
    return any(arg.lower() in help_aliases for arg in args)


def is_resolution_token(token: str) -> bool:
    # 檢查字串是否為有效的 寬/高 格式。
    parts = token.split("/")
    if len(parts) != 2:
        return False

    width_text, height_text = parts[0].strip(), parts[1].strip()
    return width_text.isdigit() and height_text.isdigit() and int(width_text) > 0 and int(height_text) > 0


def show_help() -> int:
    # 輸出外部 help 檔內容並回傳狀態碼。
    if HELP_FILE.exists():
        print(HELP_FILE.read_text(encoding="utf-8").rstrip())
        return 0

    print("Help file not found: help.txt")
    return 1


def run_script(script_name: str, script_args: list[str]) -> int:
    # 以子程序方式執行指定腳本並回傳退出碼。
    script_path = Path(__file__).with_name(script_name)
    cmd = [sys.executable, str(script_path), *script_args]
    result = subprocess.run(cmd, check=False)
    return result.returncode


def run_or_exit(script_name: str, script_args: list[str]) -> None:
    # 執行腳本，若失敗就用相同錯誤碼中止。
    code = run_script(script_name, script_args)
    if code != 0:
        sys.exit(code)


def parse_mode_args(args: list[str]) -> dict[str, object]:
    # 解析混合順序的模式參數並做基本規則驗證。
    parsed: dict[str, object] = {
        "bg": False,
        "resolution": None,
        "input": None,
        "output": None,
        "flag_r": False,
        "flag_rf": False,
        "flag_f": False,
    }

    i = 0
    while i < len(args):
        token = args[i]
        lower = token.lower()

        if lower == "bg":
            parsed["bg"] = True
        elif is_resolution_token(token):
            if parsed["resolution"] is not None:
                raise ValueError("Resolution can only be specified once.")
            parsed["resolution"] = token
        elif lower in {"-o", "--output"}:
            if i + 1 >= len(args):
                raise ValueError("-o/--output requires a value.")
            parsed["output"] = args[i + 1]
            i += 1
        elif lower == "-r":
            parsed["flag_r"] = True
        elif lower == "-rf":
            parsed["flag_rf"] = True
        elif lower == "-f":
            parsed["flag_f"] = True
        elif token.startswith("-"):
            raise ValueError(f"Unknown option: {token}")
        else:
            if parsed["input"] is not None:
                raise ValueError("Only one input path is allowed.")
            parsed["input"] = token

        i += 1

    if parsed["input"] is None:
        raise ValueError("Missing input path.")

    if parsed["flag_r"] and parsed["flag_rf"]:
        raise ValueError("-r and -rf cannot be used together.")

    if parsed["flag_f"] and (parsed["flag_r"] or parsed["flag_rf"]):
        raise ValueError("Use either -f or -r/-rf, not both.")

    return parsed

# 依使用者輸入分流到查詢、去背或縮放流程。
def main() -> None:
    args = sys.argv[1:]

    if not args or is_help_request(args):
        sys.exit(show_help())

    if args[0].lower() == "ls":
        if len(args) < 2:
            print("Usage: fuck ls <input> [-R]")
            sys.exit(2)
        sys.exit(run_script("image_ls.py", args[1:]))

    try:
        parsed = parse_mode_args(args)
    except ValueError as exc:
        print(str(exc))
        print("Use: fuck /help")
        sys.exit(2)

    has_bg = bool(parsed["bg"])
    resolution = parsed["resolution"]
    input_path = str(parsed["input"])
    output = parsed["output"]
    flag_r = bool(parsed["flag_r"])
    flag_rf = bool(parsed["flag_rf"])
    flag_f = bool(parsed["flag_f"])

    if (flag_r or flag_rf) and not has_bg:
        print("-r/-rf cannot appear alone. Use them only with bg mode.")
        sys.exit(2)

    if has_bg and resolution is not None:
        input_obj = Path(input_path)

        remove_args = ["fuck", input_path]
        if output is not None:
            remove_args.extend(["-o", str(output)])
        if flag_f or flag_r:
            remove_args.append("-f")
        if flag_rf:
            remove_args.append("-rf")

        run_or_exit("remove_bg.py", remove_args)

        if input_obj.is_file():
            if flag_f or flag_r or flag_rf:
                resize_target = input_obj.with_suffix(".png")
            elif output is not None:
                resize_target = Path(str(output))
            else:
                resize_target = input_obj.with_name(f"{input_obj.stem}_no_bg.png")

            run_or_exit("resize.py", [str(resolution), str(resize_target), "-o", str(resize_target)])
            sys.exit(0)

        if input_obj.is_dir():
            if flag_f or flag_r or flag_rf:
                resize_target = input_obj
            elif output is not None:
                resize_target = Path(str(output))
            else:
                resize_target = input_obj / "output_no_bg"

            run_or_exit(
                "resize.py",
                [str(resolution), str(resize_target), "-o", str(resize_target), "--png-only"],
            )
            sys.exit(0)

        print(f"Input path not found: {input_path}")
        sys.exit(1)

    if has_bg:
        script_args = ["fuck", input_path]
        if output is not None:
            script_args.extend(["-o", str(output)])
        if flag_f or flag_r:
            script_args.append("-f")
        if flag_rf:
            script_args.append("-rf")
        sys.exit(run_script("remove_bg.py", script_args))

    if resolution is not None:
        if output is not None:
            sys.exit(run_script("resize.py", [str(resolution), input_path, "-o", str(output)]))
        sys.exit(run_script("resize.py", [str(resolution), input_path]))

    print("Invalid mode. Use: fuck bg <input>  OR  fuck <width>/<height> <input>")
    sys.exit(2)


if __name__ == "__main__":
    main()
