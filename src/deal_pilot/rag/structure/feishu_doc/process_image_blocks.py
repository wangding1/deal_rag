"""飞书文档树中图片块的后处理（下载、识别、写入切片内容等）。"""

from __future__ import annotations

import base64
from dataclasses import dataclass

from deal_pilot.config.minio_settings import minio_settings
from deal_pilot.config.nacos.nacos_config import get_config
from deal_pilot.config.nacos.nacos_schemas import RagConfig
from deal_pilot.rag.structure.feishu_doc.block_node import BlockNode
from deal_pilot.rag.structure.feishu_doc.block_type import BlockType
from deal_pilot.utils.minio import MinIO

_MIME_SUFFIX: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
}


@dataclass(frozen=True, slots=True)
class MinioUploadResult:
    bucket_name: str
    filename: str


@dataclass(frozen=True, slots=True)
class AttachmentInfo:
    parent_trace: list[str]
    prevs: list[str]
    nexts: list[str]


async def process_image_block(node: BlockNode) -> None:
    """处理单张图片块：下载、识别、更新 ``content`` / ``payload`` 等。

    调用方须传入 ``BlockType.IMAGE`` 节点；本模块不负责遍历文档树。
    """
    if node.block_type != int(BlockType.IMAGE):
        raise ValueError(
            f"process_image_block 只接受图片块，"
            f"当前 block_id={node.block_id!r} block_type={node.block_type}"
        )
    node.payload = {
        "token": node.content,
    }
    node.content = f"图片token: {node.content}"


def _generate_dataurl(data: bytes, mime: str) -> str:
    """将图片字节与 MIME 编码为 Data URL。"""
    if type(data) is not bytes:
        raise ValueError("data 必须是 bytes")
    normalized = _normalize_mime(mime)
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{normalized};base64,{encoded}"


async def _upload_minio(data: bytes, mime: str, block_id: str) -> MinioUploadResult:
    """上传图片到 RAG 配置的 MinIO 桶根目录，桶禁用公共读。"""
    if type(data) is not bytes:
        raise ValueError("data 必须是 bytes")
    normalized_mime = _normalize_mime(mime)
    object_id = block_id.strip()
    if not object_id:
        raise ValueError("block_id 不能为空")

    rag = await get_config("rag_config", RagConfig)
    bucket_name = rag.image_parser.bucket_name
    filename = f"{object_id}.{_suffix_for_mime(normalized_mime)}"

    client = MinIO(
        endpoint=minio_settings.endpoint,
        access_key=minio_settings.access_key,
        secret_key=minio_settings.secret_key,
        secure=minio_settings.secure,
    )
    await client.create_bucket(bucket_name, allow_public_read=False)
    await client.upload_bytes(
        bucket_name=bucket_name,
        filename=filename,
        data=data,
        mime=normalized_mime,
    )
    return MinioUploadResult(bucket_name=bucket_name, filename=filename)


async def _attachment_info(node: BlockNode) -> AttachmentInfo:
    """收集图片节点的父链与兄弟上下文，供图片理解使用。"""
    rag = await get_config("rag_config", RagConfig)
    sibling_count = rag.image_parser.sibling_count

    parent_trace: list[str] = []
    ancestor = node.parent
    collected: list[str] = []
    while ancestor is not None:
        if ancestor.content.strip():
            collected.append(ancestor.content)
        ancestor = ancestor.parent
    collected.reverse()
    parent_trace = collected

    prevs: list[str] = []
    sibling = node.prev
    while sibling is not None and len(prevs) < sibling_count:
        prevs.append(sibling.content)
        sibling = sibling.prev
    prevs.reverse()

    nexts: list[str] = []
    sibling = node.next
    while sibling is not None and len(nexts) < sibling_count:
        if sibling.block_type != int(BlockType.IMAGE):
            nexts.append(sibling.content)
        sibling = sibling.next

    return AttachmentInfo(parent_trace=parent_trace, prevs=prevs, nexts=nexts)


def _normalize_mime(mime: str) -> str:
    if not isinstance(mime, str) or not mime.strip() or "\r" in mime or "\n" in mime:
        raise ValueError("mime 必须是非空且不含换行的字符串")
    return mime.strip().split(";", 1)[0].lower()


def _suffix_for_mime(mime: str) -> str:
    if mime in _MIME_SUFFIX:
        return _MIME_SUFFIX[mime]
    if "/" not in mime:
        raise ValueError(f"无法从 MIME 推断文件后缀: {mime}")
    subtype = mime.split("/", 1)[1]
    if subtype == "jpeg":
        return "jpg"
    if "+" in subtype:
        return subtype.split("+", 1)[0]
    return subtype
