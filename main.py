"""
AstrBot 更好用的帮助菜单插件
=============================

纯文字输出，在 WebUI 插件设置中填写菜单内容，
/h 和 /帮助 命令原样读出展示。
"""

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register("better_help", "摆烂人生", "纯文字自定义帮助菜单", "1.0.2")
class BetterHelp(Star):
    """极简帮助菜单插件。

    在 WebUI 插件设置面板中填写菜单内容，/h 命令直接展示。
    """

    def __init__(self, context: Context, config: dict | None = None) -> None:
        super().__init__(context)
        self._config = config or {}

    @filter.command("h")
    async def cmd_h(self, event: AstrMessageEvent):
        """/h - 显示自定义菜单"""
        yield event.plain_result(self._read_menu())

    @filter.command("帮助")
    async def cmd_help_cn(self, event: AstrMessageEvent):
        """/帮助 - 同 /h"""
        yield event.plain_result(self._read_menu())

    def _read_menu(self) -> str:
        """从配置中取出菜单内容返回。"""
        content = self._config.get("menu_content", "")
        return content if content else "菜单为空，请在插件设置中填写菜单内容"
