"""process_image_blocks._upload_minio 真实 MinIO 验收。"""

import asyncio
from functools import wraps

import pytest

from deal_pilot.config.nacos.nacos_schemas import ImageParserConfig, RagConfig
from deal_pilot.rag.structure.feishu_doc import process_image_blocks as module


def live_test(test):
    @wraps(test)
    def run(*args, **kwargs):
        async def scenario():
            async with kwargs["minio_env"].connect() as live:
                await test(*args, **(kwargs | {"minio_env": live}))

        asyncio.run(scenario())

    return run


@live_test
async def test_upload_minio_object_at_bucket_root(minio_env, monkeypatch):
    bucket = await minio_env.private_bucket()
    data = b"\x89PNG\r\n\x1a\n"

    async def rag_config(_name, _schema):
        return RagConfig(image_parser=ImageParserConfig(bucket_name=bucket))

    monkeypatch.setattr(module, "get_config", rag_config)

    result = await module._upload_minio(data, "image/png", "mock_image_block")
    assert result.bucket_name == bucket
    assert result.filename == "mock_image_block.png"
    assert await minio_env.get(bucket, result.filename) == data
    head = await minio_env.raw.head_object(Bucket=bucket, Key=result.filename)
    assert head["ContentType"] == "image/png"
