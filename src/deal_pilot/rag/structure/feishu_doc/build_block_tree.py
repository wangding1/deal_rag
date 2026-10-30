"""将飞书 Docx list_blocks 扁平块列表构造成 BlockNode 树。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import JsonValue

from deal_pilot.rag.structure.feishu_doc.block_node import BlockNode, block_node_to_dict
from deal_pilot.rag.structure.feishu_doc.block_type import BlockType
from deal_pilot.rag.structure.feishu_doc.process_image_blocks import process_image_blocks

_METADATA_KEYS = frozenset({"block_id", "block_type", "parent_id", "children"})


def build_block_tree(
    blocks: list[dict[str, JsonValue]] | dict[str, JsonValue],
) -> BlockNode:
    """同步构树；不含图片后处理。请优先使用 ``build_block_tree_async``。"""
    return _build_block_tree(blocks)


async def build_block_tree_async(
    blocks: list[dict[str, JsonValue]] | dict[str, JsonValue],
) -> BlockNode:
    """把飞书 list_blocks 返回的扁平块列表构造成以页面块为根的 BlockNode 树。

    入参支持：
    - HTTP 响应体，如 ``{"code": 0, "data": {"items": [...]}}``；
    - 项目侧 ``list[DocxBlock]``，每项可含 ``raw`` 字段（见 ``list_blocks_mock.json``）；
    - 直接的 ``list[dict]``，结构与飞书 ``data.items`` 单页条目一致。

    按各块 ``children`` 顺序挂载飞书层级，再按标题级别整理为大纲树（如 H2 归入 H1）。
    兄弟 ``prev`` / ``next`` 在每次 ``append`` 时更新。
    节点 ``content`` 从块体提取：富文本块拼接 ``text_run``；图片块为 ``image.token``。
    ``payload`` 现阶段表格块写入 ``column_size``、``row_size``、``merge_info``，代码块写入
    ``language``，其余类型留空供后续扩展。
    构树完成后调用 ``process_image_blocks``（当前为占位）。
    """
    root = _build_block_tree(blocks)
    await process_image_blocks(root)
    return root


def _build_block_tree(
    blocks: list[dict[str, JsonValue]] | dict[str, JsonValue],
) -> BlockNode:
    items = _coerce_block_items(blocks)
    if not items:
        raise ValueError("块列表为空，无法构树")

    records = [_normalize_block_record(item) for item in items]
    nodes: dict[str, BlockNode] = {}
    for record in records:
        block_id = record["block_id"]
        if block_id in nodes:
            raise ValueError(f"重复的 block_id: {block_id}")
        block_type, content, payload = _extract_node_fields(
            int(record["block_type"]),
            record["body"],
        )
        nodes[block_id] = BlockNode(
            block_id=block_id,
            block_type=block_type,
            content=content,
            payload=payload,
        )

    for record in records:
        parent = nodes[record["block_id"]]
        for child_id in record["children"]:
            if not isinstance(child_id, str):
                raise ValueError(f"children 中存在非字符串 ID: {child_id!r}")
            try:
                parent.append(nodes[child_id])
            except KeyError as exc:
                raise ValueError(f"children 引用了未出现的 block_id: {child_id}") from exc

    roots = [
        record["block_id"]
        for record in records
        if _is_root_parent_id(record["parent_id"])
    ]
    if not roots:
        raise ValueError("未找到根块（parent_id 为空）")
    if len(roots) == 1:
        root = nodes[roots[0]]
        _apply_heading_outline(root)
        return root

    page_roots = [
        root_id
        for root_id in roots
        if nodes[root_id].block_type == int(BlockType.PAGE)
    ]
    if len(page_roots) == 1:
        root = nodes[page_roots[0]]
        _apply_heading_outline(root)
        return root
    raise ValueError(f"存在多个根块: {roots}")


def _heading_level(node: BlockNode) -> int | None:
    """标题层级 1–9，对应 block_type HEADING1(3) … HEADING9(11)。"""
    value = node.block_type
    if value < int(BlockType.HEADING1) or value > int(BlockType.HEADING9):
        return None
    return value - int(BlockType.HEADING1) + 1


def _apply_heading_outline(node: BlockNode) -> None:
    """按文档顺序把同级块按标题层级挂成大纲树（如二级标题挂到一级下）。"""
    for child in list(node.children):
        _apply_heading_outline(child)

    if not node.children:
        return

    ordered = list(node.children)
    for child in ordered:
        child.remove()

    stack: list[tuple[BlockNode, int]] = []

    for child in ordered:
        level = _heading_level(child)
        if level is not None:
            while stack and stack[-1][1] >= level:
                stack.pop()
            parent = stack[-1][0] if stack else node
            parent.append(child)
            stack.append((child, level))
        else:
            parent = stack[-1][0] if stack else node
            parent.append(child)


def _coerce_block_items(
    blocks: list[dict[str, JsonValue]] | dict[str, JsonValue],
) -> list[dict[str, JsonValue]]:
    if isinstance(blocks, list):
        return [_expect_block_dict(item, index) for index, item in enumerate(blocks)]

    data = blocks.get("data")
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            return [
                _expect_block_dict(item, index)
                for index, item in enumerate(items)
            ]

    raise ValueError(
        "无法识别的 blocks 格式，期望 list、data.items 或 list_blocks HTTP 响应体"
    )


def _expect_block_dict(item: JsonValue, index: int) -> dict[str, JsonValue]:
    if not isinstance(item, dict):
        raise ValueError(f"块列表第 {index} 项不是对象")
    return item


def _normalize_block_record(block: dict[str, JsonValue]) -> dict[str, Any]:
    raw = block.get("raw")
    if isinstance(raw, dict):
        body: dict[str, JsonValue] = raw
        block_id = _require_str(block.get("block_id"), "block_id")
        block_type = block.get("block_type", body.get("block_type"))
        parent_id = block.get("parent_id", body.get("parent_id"))
        children = block.get("children", body.get("children"))
    else:
        body = block
        block_id = _require_str(body.get("block_id"), "block_id")
        block_type = body.get("block_type")
        parent_id = body.get("parent_id")
        children = body.get("children")

    if block_type is None:
        raise ValueError(f"块 {block_id} 缺少 block_type")
    if not isinstance(block_type, int):
        raise ValueError(f"块 {block_id} 的 block_type 不是整数")

    normalized_children: list[str] = []
    if children is not None:
        if not isinstance(children, list):
            raise ValueError(f"块 {block_id} 的 children 不是数组")
        for child_id in children:
            normalized_children.append(_require_str(child_id, "children 项"))

    return {
        "block_id": block_id,
        "block_type": block_type,
        "parent_id": parent_id,
        "children": normalized_children,
        "body": body,
    }


def _require_str(value: JsonValue, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"缺少或非法的 {field_name}: {value!r}")
    return value


def _is_root_parent_id(parent_id: JsonValue) -> bool:
    return parent_id is None or parent_id == ""


def _resolve_block_type(block_type: int) -> int:
    try:
        return int(BlockType(block_type))
    except ValueError:
        return block_type


def _json_key_for_block_type(block_type: int) -> str | None:
    try:
        return BlockType(block_type).name.lower()
    except ValueError:
        return None


def _type_json_key(block_type: int, body: dict[str, JsonValue]) -> str | None:
    key = _json_key_for_block_type(block_type)
    if key is not None and key in body:
        return key
    for candidate in body:
        if candidate not in _METADATA_KEYS:
            return candidate
    return None


def _extract_node_fields(
    block_type: int,
    body: dict[str, JsonValue],
) -> tuple[int, str, dict[str, JsonValue]]:
    resolved_type = _resolve_block_type(block_type)
    json_key = _type_json_key(block_type, body)
    payload: dict[str, JsonValue] = {}
    if json_key is None:
        return resolved_type, "", payload

    type_body = body.get(json_key)
    if not isinstance(type_body, dict):
        return resolved_type, "", payload

    if resolved_type == int(BlockType.TABLE):
        property_obj = type_body.get("property")
        if isinstance(property_obj, dict):
            for key in ("column_size", "row_size"):
                value = property_obj.get(key)
                if isinstance(value, int):
                    payload[key] = value
            merge_info = property_obj.get("merge_info")
            if isinstance(merge_info, list):
                payload["merge_info"] = merge_info

    if resolved_type == int(BlockType.CODE):
        language = type_body.get("language")
        if isinstance(language, int):
            payload["language"] = language

    if resolved_type == int(BlockType.IMAGE):
        token = type_body.get("token")
        if isinstance(token, str):
            return resolved_type, token, payload
        return resolved_type, "", payload

    elements = type_body.get("elements")
    if not isinstance(elements, list):
        return resolved_type, "", payload

    parts: list[str] = []
    for element in elements:
        if not isinstance(element, dict):
            continue
        text_run = element.get("text_run")
        if not isinstance(text_run, dict):
            continue
        part = text_run.get("content")
        if isinstance(part, str):
            parts.append(part)
    return resolved_type, "".join(parts), payload


def export_block_tree_json(
    output_path: Path | str,
    blocks: list[dict[str, JsonValue]] | dict[str, JsonValue],
) -> BlockNode:
    """同步导出；不含图片后处理。请优先使用 ``export_block_tree_json_async``。"""
    root = build_block_tree(blocks)
    _write_block_tree_json(output_path, root)
    return root


async def export_block_tree_json_async(
    output_path: Path | str,
    blocks: list[dict[str, JsonValue]] | dict[str, JsonValue],
) -> BlockNode:
    """构树（含图片处理占位）并写入 JSON；顶层为 ``block_node_to_dict(root)``，勿手改输出文件。"""
    root = await build_block_tree_async(blocks)
    _write_block_tree_json(output_path, root)
    return root


def _write_block_tree_json(output_path: Path | str, root: BlockNode) -> None:
    path = Path(output_path)
    path.write_text(
        json.dumps(block_node_to_dict(root), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def export_block_tree_json_from_mock(
    mock_path: Path | str = "resource/list_blocks_mock.json",
    output_path: Path | str = "block_tree_from_mock.json",
    *,
    input_key: str = "list_blocks_result",
) -> BlockNode:
    """同步从 mock 生成 JSON；不含图片后处理。请优先使用 ``export_block_tree_json_from_mock_async``。"""
    mock_file = Path(mock_path)
    document = json.loads(mock_file.read_text(encoding="utf-8"))
    blocks = document.get(input_key)
    if not isinstance(blocks, list):
        raise ValueError(f"{mock_file} 中缺少数组字段 {input_key!r}")
    return export_block_tree_json(output_path, blocks)


async def export_block_tree_json_from_mock_async(
    mock_path: Path | str = "resource/list_blocks_mock.json",
    output_path: Path | str = "block_tree_from_mock.json",
    *,
    input_key: str = "list_blocks_result",
) -> BlockNode:
    """从 ``list_blocks_mock.json`` 的 ``input_key`` 段生成 ``block_tree_from_mock.json``。"""
    mock_file = Path(mock_path)
    document = json.loads(mock_file.read_text(encoding="utf-8"))
    blocks = document.get(input_key)
    if not isinstance(blocks, list):
        raise ValueError(f"{mock_file} 中缺少数组字段 {input_key!r}")
    return await export_block_tree_json_async(output_path, blocks)
