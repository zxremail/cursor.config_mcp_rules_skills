# GoldEngle/os live-build 落点

仓库是 Debian live-build。装进**已安装系统**的文件，默认放在 `config/includes.chroot_after_packages/`，相对路径 = 镜像内绝对路径去掉根。

ISO 启动阶段才需要的文件走 `config/includes.binary/`。组 chroot 时跑的脚本走 `config/hooks/live/*.chroot`。

## 落点表

| 要进镜像的东西 | 配方位置 | 还要做 |
|---|---|---|
| `/etc/systemd/system/*.service` 与 `.d/*.conf` | `config/includes.chroot_after_packages/etc/systemd/system/` | `[Install]` 则加 `*.wants/` 符号链接；hook + deploy 里 `systemctl enable` |
| 覆盖发行版 unit（如 plymouth-reboot） | 同上文件名 | `/etc` 覆盖 `/lib`；不要改构建机 `/lib` |
| `/usr/local/sbin`、`/usr/local/bin`、`/usr/local/scripts` | `.../usr/local/...` | 脚本 `chmod +x`；hook 里可再 chmod |
| Plymouth 主题 / 自定义 deb | `.../home/rigol/deb.images/` | 安装步骤写在 `usr/local/scripts/rigolos_packages_initial_deploy.sh` |
| GDM drop-in | `.../etc/systemd/system/gdm.service.d/` | 已有 `10-delay.conf` / `20-delay-more.conf`，按序新增 |
| udev rules | `.../etc/udev/rules.d/` | 对同类 usb 规则提交 |
| 开机 hook enable | `config/hooks/live/0099-enable-startup.chroot` | 常被 gitignore，已跟踪则 `git add -f` |
| 包部署后再 enable | `.../usr/local/scripts/rigolos_packages_initial_deploy.sh` | 锚点：`systemctl enable rigolos-gdm-delay.service` 附近 |

## 对照提交（落点样本）

- `7456173` Optimize startup and shutdown animations：rlogo 主题、`rigolos-gdm-delay.service`、GDM drop-in、wait 脚本、deploy.sh
- `f4b24e6` Hide systemd wall text before Plymouth shutdown splash：logind drop-in、plymouth-* 覆盖 unit、clear-vt、`/usr/local/sbin` 包装、0099 hook、deploy.sh

## 不要放

| 路径 | 原因 |
|---|---|
| `chroot/`、`cache/`、`binary/` | 构建产物 |
| 分析机 hostname 特化配置 | 配方要能装到所有 RIGOLOS |
| 未知 systemd 键（如 252 的 `WallMessages=`） | 开机 ignored，等于没配 |
