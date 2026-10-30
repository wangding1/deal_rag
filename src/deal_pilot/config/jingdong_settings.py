from typing import ClassVar

from pydantic_settings import SettingsConfigDict

from deal_pilot.config.base_settings import BaseSettingsWithEnv


class BenchMarkSettings(BaseSettingsWithEnv):
    app_id: str = ""
    app_secret: str = ""
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="JINGDONG_"
    )


benchmark_settings = BenchMarkSettings()
