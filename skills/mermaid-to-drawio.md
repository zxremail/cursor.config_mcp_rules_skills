# Skill: Mermaid 时序图转换为 Draw.io 格式

当用户要求将 Mermaid 语法的时序图转换为 Draw.io 格式时，必须遵循以下所有规则。

---

## 1. 输出格式

- 必须以 `.drawio` 格式保存为文件。
- 文件名使用英文，小写连字符风格，例如：`i2c-init-sequence.drawio`

## 2. 语言规范

- 技术术语使用**英文**（如 `I2C`、`SDA`、`ACK`、`NACK`、`Reset`、`Init` 等）。
- 说明文字使用**中文**（如 "发送启动信号"、"等待应答"、"初始化完成" 等）。

## 3. 箭头规则

### 3.1 移除环形箭头

- 原 Mermaid 中的自循环箭头（`participant ->> participant`）或自调用箭头，**不使用环形箭头**。
- 改为简洁的**垂直向下箭头**，表示自身内部操作。

### 3.2 箭头颜色

| 箭头方向 | 颜色 | 色值 |
|---------|------|------|
| 垂直向下（自调用） | 黑色 | `#000000` |
| 向右（调用） | 蓝色 | `#0000FF` |
| 向左（返回） | 绿色 | `#00AA00` |

### 3.3 分离文本标签

- 操作描述文字**不直接放在箭头上**。
- 将文字作为**独立的文本元素**，放置在箭头旁边。
- 所有文字标签**不要有背景颜色**（`fillColor=none`）。
- 消息箭头上的描述文字也**不要有背景颜色**。

## 4. 参与者样式

### 4.1 形状

- 参与者使用**矩形框**表示（不使用圆角、圆形或其他形状）。

### 4.2 配色方案

采用**明亮、丰富多彩**的配色方案，不同参与者使用不同色系加以区分。推荐配色：

| 参与者序号 | 填充色 | 边框色 | 文字色 |
|-----------|--------|--------|--------|
| 第 1 个 | `#2E86AB` | `#1B4965` | `#FFFFFF` |
| 第 2 个 | `#E63946` | `#B52D38` | `#FFFFFF` |
| 第 3 个 | `#2D936C` | `#1E6B4E` | `#FFFFFF` |
| 第 4 个 | `#F18F01` | `#C67500` | `#FFFFFF` |
| 第 5 个 | `#A23B72` | `#7B2D55` | `#FFFFFF` |
| 第 6 个 | `#6A4C93` | `#4A3566` | `#FFFFFF` |
| 更多 | 从上述色板循环使用 | | |

## 5. 生命线与布局

### 5.1 生命线

- 每个参与者下方有一条垂直虚线作为生命线。
- **垂直向下的自调用箭头**必须在生命线内部**居中显示**。

### 5.2 整体布局原则

- **简洁**：去除不必要的装饰和冗余元素。
- **多彩**：通过色彩区分不同参与者和交互方向。
- **层次分明**：消息之间保持合理间距，文本标签清晰可读。

## 6. Draw.io XML 结构参考

生成的 `.drawio` 文件应遵循标准的 Draw.io XML 结构：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile>
  <diagram name="Sequence Diagram">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 参与者矩形框 -->
        <mxCell id="participant_1" value="参与者名称"
          style="shape=rectangle;fillColor=#2E86AB;strokeColor=#1B4965;fontColor=#FFFFFF;fontStyle=1;"
          vertex="1" parent="1">
          <mxGeometry x="..." y="..." width="120" height="40" as="geometry"/>
        </mxCell>
        <!-- 生命线（虚线） -->
        <mxCell id="lifeline_1"
          style="endArrow=none;dashed=1;strokeColor=#888888;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- 消息箭头（向右，蓝色） -->
        <mxCell id="msg_1"
          style="endArrow=block;strokeColor=#0000FF;endFill=1;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- 消息文本标签（无背景） -->
        <mxCell id="label_1" value="描述文字"
          style="text;fillColor=none;strokeColor=none;align=left;"
          vertex="1" parent="1">
          <mxGeometry x="..." y="..." width="..." height="20" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```
