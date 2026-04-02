# Fuck Photo Background Remover

簡單的圖片工具，支援：

1. 去背
2. 縮放
3. 去背 + 縮放
4. 列出圖片詳細資訊

## 快速安裝

```sh
cd /path/to/Fuck_photo
python -m pip install -r requirements.txt
```

## 直接執行（不設別名）

```sh
python scripts/fuck_cli.py /help
```

## 設定 fuck 指令

### Windows PowerShell

```powershell
function fuck {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$InputArgs
    )
    python "D:\path\to\Fuck_photo\scripts\fuck_cli.py" @InputArgs
}
. $PROFILE
```

### Linux / macOS (bash or zsh)

```sh
function fuck(){ python3 /path/to/Fuck_photo/scripts/fuck_cli.py "$@"; }
```

## 指令速查

```sh
fuck /help
fuck ls /path/to/image_or_folder
fuck ls /path/to/folder -R

fuck bg /path/to/image.jpg
fuck bg -f /path/to/image.jpg
fuck bg -rf /path/to/image.jpg
fuck bg /path/to/image.jpg -o /path/to/out.png

fuck 300/400 /path/to/image.jpg
fuck bg 300/400 /path/to/image.jpg
fuck 300/400 bg /path/to/image.jpg -r
fuck 300/400 bg /path/to/image.jpg -rf
```

## 規則

1. `-r`、`-rf` 必須搭配 `bg`。
2. `-f` / `-rf` 不能和 `-o` 一起使用。
3. 支援格式：`.png`、`.jpg`、`.jpeg`、`.webp`、`.bmp`。

## 專案結構

```text
scripts/
  fuck_cli.py
  help.txt
  image_ls.py
  remove_bg.py
  resize.py
```
