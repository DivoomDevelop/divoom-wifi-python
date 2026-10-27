# 四类产品局域网直连验证

日期：2026-10-27，Asia/Shanghai。SDK 修复版本：**0.1.1**。

**当前规则（0.1.2）：维护者确认只有硬件 90、92、400 的 LAN 请求需要 Token，其他硬件无需 Token。
本页保留 0.1.1 的历史只读观察，不能据此推断所有固件、设备设置和命令的 Token 要求。**

本次先调用发现接口，再直接请求设备的局域网 IP，不把云端查询成功算作设备直连成功。
名称明确包含模拟标志的设备不纳入结果。全程只读，没有修改亮度、切换屏幕、重启、上传或删除。

| 产品 | 本次测试设备数 | 返回有效业务数据 | 实际查询 |
| --- | --- | --- | --- |
| PIXOO64，90/92 | 6 | **6** | 配置含 Brightness；时间含 LocalTime/UTCTime |
| TimeGate，400/402 | 2 | **1（402）** | 402 不带 Token 返回亮度、屏幕开关和当前 ClockId |
| TimeFrame，510/511 | 6 | **5** | GET＋JSON 返回硬件、亮度、屏幕开关和当前 ClockId |
| AstroToo，530 | 12 | **8** | 硬件、能力、亮度、屏幕开关、当前 ClockId |

合计 **20 台设备、75 次有效业务查询**。此次发现列表没有 PIXOO64 96 或 TimeFrame 512 样本。
发现接口也返回了无法连接的地址：1 台 TimeFrame、4 台 AstroToo 未取得本次直连结果。

## TimeGate 的实际差异与修正

- **400**：不带 Token 的直接请求返回 `{"error_code":"DeviceToken is err"}`。本次未提供有效 Token，
  未把它记为业务功能通过。SDK 保留该硬件的 Token 要求。
- **402**：不带 Token 的 `Sys/GetBrightness`、`Channel/GetOnOffScreen`、`Channel/GetClockInfo`
  均返回对应业务字段；SDK 原来在发送前强制要求 Token，已按硬件修正。
- 0.1.1 曾在显式提供 Token 时附带发送到两版设备；0.1.2 以硬件规则为准，仅 90/92/400 的 LAN 请求注入 Token。
  库不自动重试写操作。
- 402 的 `Channel/GetAllConf`、`Device/GetDeviceTime` 返回 ReturnCode 0，但没有配置或时间字段，
  本次标为 **ack_only**，没有当作配置/时间功能已实现。

TimeFrame 的身份/状态查询，以及 TimeGate 402 的上述三个状态查询，是明确标记的只读
`protocol_probe`，用于验证直接通路；不表示这些命令都已经加入对应产品的公开 Python 方法目录。
可达的 TimeFrame 样本返回固件 510175/511175，AstroToo 可达样本包含 530062。

## 复现与结果边界

```console
python tools/check_lan.py --timeout 2 --workers 4 --output .venv/lan-checks/report.json
```

报告保存逐设备地址、HTTP 路由、调用种类、业务字段和耗时；新建文件，拒绝覆盖。
本次完整报告保存在本机被 Git 忽略的目录，不公开现场 IP、设备名称和业务值。
自动化回归保留 400 的必填要求，增加 402 无 Token 的 SDK 和非交互式 CLI 场景。

本次证明四类产品均存在可用的局域网只读业务通路，不等于所有 API、写操作、媒体传输或
每个固件版本都已完成实机验证。原始接口覆盖说明和首次交付记录见 [验证报告](VERIFICATION.md)。
