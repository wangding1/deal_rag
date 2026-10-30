# 飞书相关 HTTP 辅助

## 职责

供 RAG 图片处理等流程使用的图片下载；当前通过 **HTTP URL** 拉取，不调用飞书 Open API（便于本地无法连飞书时联调）。

## 子目录

| 路径 | 职责 |
| --- | --- |
| `api/` | `download_image(url)` → `DownloadedImage(mime, data)` |

## 验证

```bash
uv run python -c "from deal_pilot.feishu.api import download_image, DownloadedImage"
```

对可访问的公网图片 URL 调用 `await download_image(url)` 做连通性验证。
