# feishu_doc 结构层

## 职责

将飞书 Docx `list_blocks` 扁平块列表转为 `BlockNode` 大纲树，并做类型相关的字段提取与后处理。

| 模块 | 作用 |
| --- | --- |
| `block_node.py` | 树节点类型、兄弟/父子关系、`block_node_to_dict` |
| `block_type.py` / `code_language.py` | 飞书枚举常量 |
| `build_block_tree.py` | 构树、按序调用图片处理、导出 JSON |
| `process_image_blocks.py` | **单张**图片块处理；含 Data URL、MinIO 上传与兄弟上下文 |

## 调用顺序

1. `root = await build_block_tree(blocks)` — 挂链后单次 `await _apply_heading_outline(root)`（大纲 + 图片先序）
2. 生成 `block_tree_from_mock.json`：`make block-tree-mock`

## 验证

```bash
make block-tree-mock
```

扩展图片逻辑时改 `process_image_block`，勿在脚本里手改 JSON。
