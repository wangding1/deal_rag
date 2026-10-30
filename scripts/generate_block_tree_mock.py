#!/usr/bin/env python3
"""根据 list_blocks_mock.json 生成 block_tree_from_mock.json（勿手改输出）。"""

from __future__ import annotations

import asyncio

from deal_pilot.rag.structure.feishu_doc.build_block_tree import (
    export_block_tree_json_from_mock,
)


async def _main() -> None:
    root = await export_block_tree_json_from_mock()
    print("Wrote block_tree_from_mock.json from resource/list_blocks_mock.json")
    print(f"  root: {root.block_id}  direct_children: {len(root.children)}")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
