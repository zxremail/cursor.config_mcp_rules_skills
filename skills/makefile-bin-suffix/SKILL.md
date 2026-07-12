---
name: makefile-bin-suffix
description: >-
  凡是使用 Makefile 新生成的二进制可执行程序，都要以 .bin 作为后缀。
  Use when creating or editing Makefile / makefile / GNUmakefile, C/C++/Go/Rust
  link rules that produce executables, or when the user mentions make、二进制、
  可执行文件、TARGET、.bin 后缀。
---

# Makefile 可执行文件 `.bin` 后缀

## 强制规则

**凡是使用 makefile 新生成的二进制可执行程序，都要以 .bin 作为后缀。**

适用于：新建 Makefile、修改链接规则、新增可执行目标。共享库（`.so` / `.a` / `.dll`）与对象文件（`.o`）不加 `.bin`。

## 做法

1. 可执行目标名以 `.bin` 结尾，例如：
   - `TARGET = susidemo4.bin`
   - `BIN = myapp.bin`
   - `all: foo.bin bar.bin`
2. 链接命令的 `-o` 输出路径必须是带 `.bin` 的名字。
3. `clean` / `install` / 脚本引用等与产物名保持一致。
4. 若改名已有无后缀可执行文件：同步改 `TARGET`（或等价变量）、清理规则，以及文档/脚本中的旧名。

## 示例

```makefile
TARGET = susidemo4.bin

$(TARGET): $(OBJS)
	$(CC) $(ARCHFLAG) -o $@ $(OBJS) $(LDFLAGS)
```

```makefile
# 错误：可执行文件无 .bin
mytool: $(OBJS)
	$(CC) -o $@ $(OBJS)
```

```makefile
# 正确
mytool.bin: $(OBJS)
	$(CC) -o $@ $(OBJS)
```

## 检查清单

- [ ] 每个链接出的可执行产物名以 `.bin` 结尾
- [ ] `clean` 删除的是带 `.bin` 的名字
- [ ] 未给 `.so` / `.a` / `.o` 错误追加 `.bin`
