# wr-cl

word replacer command line tool

## 介绍

这是一款命令行工具，用于替换 word docx 文件中的指定单词。

## 特点

- 不改变原 word 样式
- 命令行工具，方便使用
- 支持批量替换，可以一次替换多个文件
- 支持正则表达式，可以匹配多个单词
- 使用 `python3` `pyinstaller` 打包成cli文件，方便 windows/macos/linux 用户使用
- 支持多线程处理，加速处理速度
- 使用 github actions 自动打包 windows/macos/linux 各个平台的cli文件，供下载

## 下载解压

[下载地址](https://github.com/lanseria/wr-cl/releases)

## 使用方法

1. 创建配置文件 `config.json`:

```json
{
  "replacements": {
    "pattern_type": "plain|regex",
    "rules": [
      {
        "old_text": "\\b公司A\\b",
        "new_text": "DeepSeek",
        "options": {
          "case_sensitive": true,
          "whole_word": true,
          "preserve_format": true
        }
      }
    ]
  },
  "file_settings": {
    "input_path": "./docs",
    "output_path": "./modified"
  },
  "advanced": {
    "max_workers": 4,
    "timeout": 30
  }
}
```

2. 运行命令：

```bash
wr-cl --config config.json
```

### 可选参数

- `--dry-run`: 预览模式，不会修改原文件
- `--log-level`: 日志等级 (debug/info/warning/error)

## 开发

1. 克隆仓库：

```bash
git clone https://github.com/lanseria/wr-cl.git
cd wr-cl
```

2. 安装依赖：

```bash
# 创建虚拟环境（venv 是 Python 内置工具）
python3 -m venv myenv
# macOS/Linux
source myenv/bin/activate

# Windows (PowerShell)
.\myenv\Scripts\Activate.ps1

pip install .

pip install ".[dev]"

pip install ".[build]"

deactivate
```

3. 运行测试：

```bash
pytest
# 运行代码格式化
black .
isort .
```

4. 打包

```bash
rm -rf dist/ build/
python build.py
```

5. 运行

```bash
# 复制配置模板
cp config.json.template config.json
# 编辑配置文件，修改所需的替换规则

# Windows
dist\wr-cl.exe --config config.json

# macOS/Linux
./dist/wr-cl --config config.json
```

6. 发布

```bash
git tag -d v1.1.0 
git push origin --delete v1.1.0
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## 许可证

MIT