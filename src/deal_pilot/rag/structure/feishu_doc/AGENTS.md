# feishu_doc 结构层

## 职责

将飞书 Docx `list_blocks` 扁平块列表转为 `BlockNode` 大纲树，并做类型相关的字段提取与后处理。

| 模块 | 作用 |
| --- | --- |
| `block_node.py` | 树节点类型、兄弟/父子关系、`block_node_to_dict` |
| `block_type.py` / `code_language.py` | 飞书枚举常量 |
| `build_block_tree.py` | 构树、导出 JSON；入口为 **`build_block_tree_async`** |
| `process_image_blocks.py` | 构树后异步处理图片块（当前占位） |

## 调用顺序

1. `await build_block_tree_async(blocks)` — 同步构树逻辑 + `await process_image_blocks(root)`
2. 生成 `block_tree_from_mock.json`：`make block-tree-mock`（内部 `export_block_tree_json_from_mock_async`）

## 验证

```bash
make block-tree-mock
```

图片处理实现后，在同一 async 流程中扩展 `process_image_blocks._process_image_node`，勿在脚本里手改 JSON。
