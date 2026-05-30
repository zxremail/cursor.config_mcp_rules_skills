# 示例：嵌入式 AMP 验证（节选）

计划标准：**AMP 通信方案在 RK3588 平台上的验证过程**。

### 1. 使用场景（节选）

RIGOLOS 在 RK3588 采用 Linux+RTOS AMP，需完成跨域 RPMsg 与实时性**完整验证**（非仅搭环境）。待测机 rigol@172.18.24.96，需整理拓扑、6 组万级采样与 idle/busy 对照。手工约 2～3 人日；用 Cursor 整理终端输出为表并撰写飞书报告，压缩至约 1 人日。

### 2. 如何使用（节选）

步骤1：SSH 执行 lscpu、linux-stress-isol.sh performance、perf-status → 产出 §1.1 锁频对比表 1 套。  
步骤3：执行 PERIOD/ISOL/RPMG/绑核 6 组，N=10000 → 产出 6 张结论表。  
步骤4：Cursor 整理 summary 输出 → §2 总览表。  
步骤5：飞书主报告 + 概要页各 1 份。

### 3. 输出成果（节选）

2 份飞书 docx；15+ 张表；10+ 画板；多张截图。  
数据：ISOL 下 RTOS |p99|=1µs；RPMG busy s=64 max=4648.5µs；绑核后 max 70～85µs。  
结论：算力隔离成立；尾延迟主因在 Linux 调度。

### 4. 成果证明链接

主报告：https://rigolportal.feishu.cn/docx/OCLRd8Dp2oqZc3xnxI2cCUM6nue  
概要：https://rigolportal.feishu.cn/docx/D9E3dpXPBo4REQxnt78cLuLcnte

---

完整粘贴版见用户任务目录 `成果说明-可直接粘贴.txt`。