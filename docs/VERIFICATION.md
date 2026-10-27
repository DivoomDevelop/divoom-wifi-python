# 验证报告 / Verification

日期：2026-10-27（Asia/Shanghai）。版本：0.1.0。

本页保留首次交付的验证记录。**后续四类设备直连复测及当前 Token 规则见
[局域网验证记录](LAN_CHECKS.md)**；0.1.2 仅要求硬件 90、92、400 的 LAN 请求提供 Token。

## 自动化与分发验证

验证环境为 Windows、CPython 3.13、requests 2.34.2、pytest 9.1.1。

| 检查 | 结果 |
| --- | --- |
| 自动测试 | **348 passed** |
| Ruff 静态检查 | 通过 |
| 文档生成一致性 | 144 页全部登记；生成内容与仓库一致 |
| 接口覆盖 | PIXOO64 45、TIMEGATE 39、TIMEFRAME 16、ASTROTOO 38，共 138 个操作 |
| Python 3.11 语法检查 | 22 个 Python 文件通过；没有在本机执行 Python 3.11 运行时测试 |
| 源码包构建 | `divoom_wifi-0.1.0.tar.gz` 成功；wheel 由源码包构建 |
| wheel 构建 | `divoom_wifi-0.1.0-py3-none-any.whl` 成功 |
| 包元数据 | `twine check` 通过 |
| 干净环境安装 | 新 venv 安装 wheel 及运行依赖成功，`pip check` 通过 |
| 安装独立性 | 使用 `python -I` 从新 venv 的 site-packages 导入，全部运行文件与源码一致 |
| 安装后命令行 | 独立 CLI 的版本、离线产品目录及修正后的 TimeFrame 字体参数正常 |

自动测试对 138 个操作分别执行显式方法和协议字段调用，共 276 个操作场景。
请求真正经过本地 HTTP 服务，检查方法、路径、JSON 请求体、嵌套数据、Token、状态码、
multipart 文件字节、每部分及完整 Content-Length、HEAD、下载和错误处理。
其余场景覆盖所有九种硬件路由、改名/同名/未知设备、缺失硬件查询、云端设备信息填充、
命令行完整交互、有限超时、写入不重试、JSON 大小及同一设备串行发送。

测试中的媒体文件部分使用合成文件头，用于验证尺寸检查和传输协议；不构成视频编码或固件解码认证。
GitHub Actions 已配置 Windows/macOS/Linux 和 Python 3.11/3.13；本次没有在远程执行该矩阵。

## 现场只读验证

调用公开发现接口，并从现场返回的设备中按硬件抽样；名称中明确标识模拟的设备被排除。
只执行发现、身份、能力、配置、时间、亮度/屏幕状态、字体和表盘列表查询。
没有执行重启、亮度修改、切换显示、上传、删除或其他设备写操作。

| 产品 / 硬件 | 观察结果与边界 |
| --- | --- |
| PIXOO64 90 | 两个样本的配置、时间查询均成功；验证 POST `:80/post` |
| PIXOO64 92 | 两个样本的配置、时间查询均成功；验证 POST `:80/post` |
| TIMEGATE 400 | 字体列表及设备通道信息云端查询成功；未提供 LocalToken，未执行 LAN 控制验证 |
| TIMEFRAME 510 | 表盘云端列表查询成功；可达样本返回固件 510175；GET＋JSON 身份查询成功 |
| TIMEFRAME 511 | 两个样本返回固件 511175；GET＋JSON 身份查询与表盘列表成功 |
| ASTROTOO 530 | 一个可达样本返回固件 530062；身份、LAN 能力、亮度和屏幕状态查询成功 |
| PIXOO64 96 / TIMEGATE 402 / TIMEFRAME 512 | 发现列表中没有对应样本，路由仅完成本地 HTTP 自动化验证 |

发现结果中有不可达的 TimeFrame/AstroToo 地址。它们被记录为网络不可用，未据此修改硬件映射或自动重发写入。
一次 TimeFrame 复测中的字体及表盘云端请求超时；其他样本已确认相同修正后的字体请求可用。

原始精简记录（不含现场设备 IP、MAC、设备 ID、名称或业务数据）：

- [首次现场检查](verification/read_only_smoke.json)
- [TimeFrame 字体修正后复测](verification/timeframe_followup.json)
- [TimeFrame GET＋JSON 身份验证](verification/timeframe_get_identity.json)

## 文档差异与限制

TimeFrame 字体接口文档第 379 页未列请求参数。首次按空 JSON 调用返回
`ReturnCode:12`、`ReturnMessage:"Request data is null"`；传入所选设备的 `DeviceId` 后返回字体列表。
注册表和显式方法已增加可自动填入的 `device_id`，并有单独回归测试。
直接 IP 连接且没有设备 ID 时，调用该云端接口会在本地要求补齐 ID。

完整文档覆盖代表封装了已公布接口，不代表所有固件、参数组合、可见效果、视频编码或长时间运行已实机验证。
媒体上传、表盘写入和删除在本次只做宿主端协议验证；后续针对专用测试设备验证实际写入及回读效果。
其他文档拼写差异、GET 请求体、上传分块边界和返回码规则见 [协议说明](PROTOCOL.md)。

复现：

```console
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests tools examples
python tools/build_reference.py --check
python -m build
python -m twine check dist/*
```

现场检查需主动执行 `python tools/smoke_readonly.py --output 新报告路径.json`，已有文件不会覆盖。
未来的网络状态和固件响应可能不同，本报告记录的是本次观察结果。
