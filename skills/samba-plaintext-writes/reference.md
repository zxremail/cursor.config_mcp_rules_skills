# reference.md — 按需阅读

## B. Windows 本地修复（仅用户要求 no tsd 时）

```powershell
$py = "$env:LocalAppData\Programs\Python\Python313\python.exe"
& $py -c "from pathlib import Path; Path(r'PATH').write_bytes(b'...utf8...')"
```

内容必须来自 Agent 已知明文，勿 `read_text` 已 TSD 的文件。

## A. Linux 恢复 TSD 文件（优先 git，省 tokens）

```bash
cd ~/loop.AI/REPO && git checkout -- path/to/file
grep -rl 'TSD-Header' ~/loop.AI 2>/dev/null || echo OK
```

## Explorer 加密锁

多与 TSD/受控盘相关；137 上 `file: data` 而 Windows 看 UNC 像明文，是常见现象。
