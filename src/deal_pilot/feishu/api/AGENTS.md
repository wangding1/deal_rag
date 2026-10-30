# feishu.api

## 职责

图片等资源的无飞书网关 HTTP 下载封装。

| 模块 | 入口 | 说明 |
| --- | --- | --- |
| `download_image.py` | `download_image(url)` | GET 指定 URL，返回二进制与 Content-Type |

## 契约

- `download_image` 返回 `DownloadedImage(mime, data)`；`mime` 来自响应 `Content-Type` 主类型，缺省为 `application/octet-stream`。
- 空 URL 抛出 `ValueError`；非 200/206 抛出 `ImageDownloadError`。
