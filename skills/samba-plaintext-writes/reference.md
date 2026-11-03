# windows-no-tsd-writes — 补充说明（按需阅读）

## 修复 Windows 本地 TSD（Python 字节直写）

```powershell
$py = "$env:LocalAppData\Programs\Python\Python313\python.exe"
& $py -c "from pathlib import Path; p=Path(r'PATH'); p.write_bytes(CONTENT_UTF8.encode('utf-8'))"
```

`CONTENT_UTF8` 必须是 Agent 已生成的正确文本，不要用 `read_text` 读已 TSD 的文件。

## Linux 抽查

```bash
grep -rl 'TSD-Header' ~/loop.AI 2>/dev/null || echo OK
file ~/path/to/file.py
```

## 布局建议

- 源码真源：`~/loop.AI` on 137（SSH 编辑）。
- Windows 本地：仅 `unattended-download` 运行时、`windows.tools` 等必须本机的内容。

## Explorer 加密锁

常与 TSD/受控盘同一套策略；Windows 读 UNC 像明文、137 上 `data` 即典型不同视角。
