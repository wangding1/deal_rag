"""通过 HTTP URL 下载图片（不调用飞书 Open API）。"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


class ImageDownloadError(RuntimeError):
    """图片 URL 下载失败。"""


@dataclass(frozen=True, slots=True)
class DownloadedImage:
    mime: str
    data: bytes


def _mime_from_content_type(content_type: str | None) -> str:
    if not content_type:
        return "application/octet-stream"
    return content_type.split(";", 1)[0].strip().lower()


async def download_image(url: str) -> DownloadedImage:
    """从可访问的 HTTP(S) URL 下载图片二进制与 MIME 类型。"""
    image_url = url.strip()
    if not image_url:
        raise ValueError("url 不能为空")

    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        response = await client.get(image_url)

    if response.status_code not in (200, 206):
        raise ImageDownloadError(
            f"下载图片失败: HTTP {response.status_code} url={image_url!r}"
        )

    mime = _mime_from_content_type(response.headers.get("content-type"))
    return DownloadedImage(mime=mime, data=response.content)
