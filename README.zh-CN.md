# divoom-wifi-python

[English](README.md) · [全部接口与来源](docs/API_COVERAGE.md) · [协议说明](docs/PROTOCOL.md)

支持 PIXOO64、TIMEGATE、TIMEFRAME、ASTROTOO，提供 Python 3.11+ 同步库和命令行。
按 `Hardware` 匹配产品及新旧硬件的端口、路径，设备改名不影响识别。

## 功能

- 发现并选择设备，按硬件编号自动匹配四款产品的接口。
- 提供 138 个产品操作，覆盖设置、表盘、动画/文字、工具、云端查询及 AstroToo 文件传输。
- 提供显式类型标注方法，以及可查看接口和参数的交互式 CLI。
- 保留原始响应字段，统一处理网络、协议、设备返回码与参数错误。

GitHub 仓库名为 `divoom-wifi-python`；Python 安装包和命令行为 `divoom-wifi`，
导入名为 `divoom_wifi`。已测固件及自动化、现场验证的具体范围见 [验证报告](docs/VERIFICATION.md)。

## 安装与快速使用

克隆仓库后安装：

```console
git clone https://github.com/DivoomDevelop/divoom-wifi-python.git
cd divoom-wifi-python
python -m pip install .
divoom-wifi
```

也可直接从 GitHub 安装（需要 Git）：

```console
python -m pip install "git+https://github.com/DivoomDevelop/divoom-wifi-python.git"
```

无参数启动后，选择设备，再选择对应 API、查看参数并执行。TimeGate 硬件 **400** 需要设备设置中的
`LocalToken`，命令行会隐藏输入；硬件 **402** 无需填写。需要时也可设置环境变量
`DIVOOM_LOCAL_TOKEN`，不会自动保存。

```python
from divoom_wifi import discover_devices, connect

devices = [d for d in discover_devices() if d.supported]
if not devices:
    raise SystemExit("未发现支持的设备，可尝试直接指定 IP 和硬件编号")
for i, d in enumerate(devices, 1):
    print(i, d.name, d.product, d.hardware, d.device_id, d.ip, d.mac)
choice = int(input("请选择设备编号："))
if not 1 <= choice <= len(devices):
    raise SystemExit("设备编号无效")
with connect(devices[choice - 1]) as device:
    print([api.name for api in device.list_apis()])
    print(device.describe_api("set_brightness").as_dict())
    print(device.set_brightness(brightness=40))
```

发现接口通过云端返回同网络设备，需要联网，返回的 IP 可能已失效；控制请求还需能访问设备局域网。
没有 `Hardware` 时尝试只读查询；无法识别时要求手动指定，不根据名称猜测。
未知硬件仍保留在发现列表中，并标记 `supported=False`。

可跳过发现服务，直接连接：

```python
with connect("192.168.1.50", hardware=530) as astro:
    print(astro.get_hardware_version())
    print(astro.get_brightness())
```

硬件编号：PIXOO64 为 90/92/96，TIMEGATE 为 400/402，TIMEFRAME 为 510/511/512，
ASTROTOO 为 530。旧版 PIXOO64 和 TimeGate 走端口 80 的 `/post`；其他版本走端口 9000 的
`/divoom_api`。TimeFrame 按现有文档使用 GET＋JSON 请求体，其余使用 POST。
`base_url="http://主机:端口"` 可覆盖访问地址。只指定 IP 时会在端口 9000 查询硬件，老设备需手动指定编号。
TimeFrame 字体服务实际需要设备 ID，库会自动填入；直接 IP 连接时使用 `get_fonts(device_id=...)`。

## 命令行

```console
divoom-wifi discover --json
divoom-wifi apis --product pixoo64
divoom-wifi describe send_text --product pixoo64
divoom-wifi call get_brightness --ip 192.168.1.50 --hardware 530 --json
divoom-wifi call get_brightness --device-id 300000001 --json
```

把 `{"brightness":40}` 保存为 `brightness.json`，再执行：

```console
divoom-wifi call set_brightness --ip 192.168.1.50 --hardware 530 --params '@brightness.json'
```

`--params` 支持 JSON、`@文件` 或 `-`（标准输入）。上传另用 `--file`、`--preview`、`--duration`；
下载用 `--destination`。参数可使用 Python 名称或协议原字段名，但不能重复指定同一字段。
非交互式多设备调用需提供设备 ID 或 IP。错误输出到 stderr 并返回退出码 2。

## 文件、表盘与错误处理

AstroToo 提供照片/视频上传、下载、HEAD、素材上传、创建及修改本地表盘。
媒体上传确认不等于后台入库完成，可调用
`wait_for_photo(clock_id=..., file_name="唯一照片名.jpg", timeout=30)` 查询。
视频必须提供 WebP 预览图、声明时长及实际宽高；库不转码，也不保证所有视频编码均能播放。
表盘背景限定 480×480 的 JPEG/WebP、大小小于 512000 字节；临时 `local://` 素材应尽快绑定。
完整示例见 [examples](examples) 和英文说明。下载不会覆盖已有文件。

接口结果保留协议业务字段，检查 `error_code` 或 `ReturnCode`，不会仅凭 HTTP 200 判断成功。
错误分为网络、HTTP、JSON/协议、设备拒绝、参数、Token 和产品不支持等类型，统一继承 `DivoomError`。
异常可携带 `api_name`、`response`、`status_code` 和 `code`。

普通请求默认 15 秒，上传默认 120 秒，可在 `connect()` 中配置。同一设备请求在进程内串行发送。
写操作超时不自动重试、不切换方法重发；超时也可能已经生效，可使用查询接口核对。
云端接口自动填入发现结果里的设备 ID/MAC；直接 IP 连接时可用 `DeviceInfo` 或方法参数补齐。

## 交付与开发

四个产品目录的 141 页文档及 3 页通用说明均有登记，合并重复项并补充下载 HEAD 后共 138 个操作。
每个操作都有显式 Python 方法、注册表元数据、来源链接与协议测试；运行时不读取文档网站。
实际验证范围见 [验证报告](docs/VERIFICATION.md)。提供接口不代表所有固件和参数组合均已实机验证。

```console
python -m pip install -e '.[dev]'
python -m pytest
python tools/build_reference.py --check
python -m build
python -m twine check dist/*
```

## 反馈与贡献

四类产品的最新直连测试见 [局域网验证记录](docs/LAN_CHECKS.md)。本地可执行：

```console
python tools/check_lan.py --output .venv/lan-checks/report.json
```

只有发现步骤访问云端，设备查询均直连局域网。没有业务字段的成功确认标为 `ack_only`；
部分只读探测并不属于该产品已公布的 Python 方法目录，会标为 `protocol_probe`。
报告含本地 IP，应保留在本机；已有报告不会覆盖。

问题和功能建议请提交至 [GitHub Issues](https://github.com/DivoomDevelop/divoom-wifi-python/issues)，
说明 SDK 版本、产品、硬件/固件版本、所用接口和最小复现代码。
增加接口时请同步维护注册表、显式方法、文档和协议测试。
Pull Request 会运行 Windows/macOS/Linux 与 Python 3.11/3.13 的检查。

采用 [MIT 许可证](LICENSE)。提供源码、构建配置、示例及测试；安装方式见上文。
范围不包含 PIXOO16、蓝牙、固件内部命令或表盘编辑器。
