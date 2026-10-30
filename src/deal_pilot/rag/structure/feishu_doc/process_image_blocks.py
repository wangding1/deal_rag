"""飞书文档树中图片块的后处理（下载、识别、写入切片内容等）。"""

from __future__ import annotations

from deal_pilot.rag.structure.feishu_doc.block_node import BlockNode
from deal_pilot.rag.structure.feishu_doc.block_type import BlockType


async def process_image_blocks(root: BlockNode) -> None:
    """按树顺序处理所有图片节点。

    构树阶段 ``content`` 仅为 ``image.token``；本步骤负责后续 enrich。
    当前为占位实现，不修改节点。
    """
    for node in _iter_nodes(root):
        if node.block_type != int(BlockType.IMAGE):
            continue
        await _process_image_node(node)


async def _process_image_node(node: BlockNode) -> None:
    """单张图片处理占位；后续可下载素材并更新 ``content`` / ``payload``。"""
    node.payload = {
        "token": node.content,
    }
    node.content = f"图片token: {node.content}"


def _iter_nodes(root: BlockNode) -> list[BlockNode]:
    ordered: list[BlockNode] = []

    def walk(node: BlockNode) -> None:
        ordered.append(node)
        for child in node.children:
            walk(child)

    walk(root)
    return ordered
