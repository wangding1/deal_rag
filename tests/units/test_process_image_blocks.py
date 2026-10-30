import asyncio
import base64

import pytest

from deal_pilot.config.nacos.nacos_schemas import ImageParserConfig, RagConfig
from deal_pilot.rag.structure.feishu_doc.block_node import BlockNode
from deal_pilot.rag.structure.feishu_doc.block_type import BlockType
from deal_pilot.rag.structure.feishu_doc import process_image_blocks as module


def test_generate_dataurl():
    data = b"\x89PNG\r\n"
    url = module._generate_dataurl(data, "image/png")
    assert url == f"data:image/png;base64,{base64.b64encode(data).decode('ascii')}"


def test_attachment_info_parent_trace_and_siblings(monkeypatch):
    async def rag_config(_name, _schema):
        return RagConfig(image_parser=ImageParserConfig(sibling_count=2))

    monkeypatch.setattr(module, "get_config", rag_config)

    root = BlockNode(block_id="page", block_type=int(BlockType.PAGE), content="")
    section = BlockNode(block_id="h1", block_type=int(BlockType.HEADING1), content="章节")
    root.append(section)
    text_a = BlockNode(block_id="a", block_type=int(BlockType.TEXT), content="前文")
    img_prev = BlockNode(block_id="img1", block_type=int(BlockType.IMAGE), content="图A")
    target = BlockNode(block_id="img2", block_type=int(BlockType.IMAGE), content="目标")
    img_skip = BlockNode(block_id="img3", block_type=int(BlockType.IMAGE), content="图B")
    text_b = BlockNode(block_id="b", block_type=int(BlockType.TEXT), content="后文1")
    text_c = BlockNode(block_id="c", block_type=int(BlockType.TEXT), content="后文2")
    for child in (text_a, img_prev, target, img_skip, text_b, text_c):
        section.append(child)

    info = asyncio.run(module._attachment_info(target))
    assert info.parent_trace == ["章节"]
    assert info.prevs == ["前文", "图A"]
    assert info.nexts == ["后文1", "后文2"]


def test_attachment_info_skips_empty_ancestors(monkeypatch):
    async def rag_config(_name, _schema):
        return RagConfig(image_parser=ImageParserConfig(sibling_count=1))

    monkeypatch.setattr(module, "get_config", rag_config)

    root = BlockNode(block_id="page", block_type=int(BlockType.PAGE), content="根")
    empty = BlockNode(block_id="empty", block_type=int(BlockType.TEXT), content="   ")
    parent = BlockNode(block_id="parent", block_type=int(BlockType.HEADING2), content="父")
    root.append(empty)
    root.append(parent)
    image = BlockNode(block_id="img", block_type=int(BlockType.IMAGE), content="x")
    parent.append(image)

    info = asyncio.run(module._attachment_info(image))
    assert info.parent_trace == ["根", "父"]
    assert info.prevs == []
    assert info.nexts == []
