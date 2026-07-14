"""
AstrBot 更好用的帮助菜单插件
=============================

支持 WebUI 中一键添加多个自定义菜单，每个菜单 = 命令名 + 内容。
/h 和 /帮助 为默认命令，外加最多 10 个自定义命令。
"""

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

from astrbot.core.star.star_handler import star_handlers_registry, StarHandlerMetadata, EventType
from astrbot.core.star.filter.command import CommandFilter


@register("better_help", "摆烂人生", "纯文字自定义帮助菜单，支持多命令", "1.2.0")
class BetterHelp(Star):
    """帮助菜单插件。

    - /h 和 /帮助 始终可用，展示默认菜单
    - 在 WebUI 插件设置中可添加更多自定义命令，每个命令对应独立菜单内容
    """

    def __init__(self, context: Context, config: dict | None = None) -> None:
        super().__init__(context)
        self._config = config or {}
        self._dynamic_handlers: list[StarHandlerMetadata] = []

    # ============================================================
    # 生命周期：动态注册 + 清理自定义命令
    # ============================================================

    async def initialize(self) -> None:
        """插件激活时，根据配置动态注册自定义命令。"""
        menus = self._config.get("menus", [])
        if not menus:
            return

        module_path = self.__class__.__module__

        for i, menu in enumerate(menus):
            cmd = (menu.get("command", "") or "").strip().lstrip("/")
            content = menu.get("content", "")
            if not cmd or not content:
                continue

            # 跳过和默认命令冲突的
            if cmd in ("h", "帮助"):
                continue

            # 为每个自定义命令创建 handler
            handler_fn = self._make_handler(content)
            handler_name = f"_dynamic_cmd_{cmd}"

            cmd_filter = CommandFilter(command_name=cmd)
            handler_md = StarHandlerMetadata(
                event_type=EventType.AdapterMessageEvent,
                handler_full_name=f"{module_path}.{handler_name}",
                handler_name=handler_name,
                handler_module_path=module_path,
                handler=handler_fn,
                event_filters=[cmd_filter],
                desc=f"自定义菜单 /{cmd}",
            )
            cmd_filter.init_handler_md(handler_md)
            star_handlers_registry.append(handler_md)
            self._dynamic_handlers.append(handler_md)
            logger.info(f"[better_help] 已注册自定义命令: /{cmd}")

    async def terminate(self) -> None:
        """插件停用/重载时，移除动态注册的命令。"""
        for handler_md in self._dynamic_handlers:
            star_handlers_registry.remove(handler_md)
        self._dynamic_handlers.clear()
        logger.info("[better_help] 已清理所有动态命令")

    # ============================================================
    # 固定命令
    # ============================================================

    @filter.command("h")
    async def cmd_h(self, event: AstrMessageEvent):
        """/h - 显示默认菜单"""
        yield event.plain_result(self._read_default_menu())

    @filter.command("帮助")
    async def cmd_help_cn(self, event: AstrMessageEvent):
        """/帮助 - 同 /h"""
        yield event.plain_result(self._read_default_menu())

    # ============================================================
    # 内部方法
    # ============================================================

    def _make_handler(self, content: str):
        """创建一个返回固定内容的异步 handler 函数。"""
        async def handler(event: AstrMessageEvent):
            yield event.plain_result(content)
        return handler

    def _read_default_menu(self) -> str:
        """读取默认菜单（取 menus 列表中第一个，兜底用 menu_content）。"""
        menus = self._config.get("menus", [])
        if menus:
            first_cmd = menus[0].get("command", "").strip().lstrip("/")
            if first_cmd in ("h", "帮助"):
                content = menus[0].get("content", "")
                if content:
                    return content
            # 找第一个非空菜单
            for m in menus:
                content = m.get("content", "")
                if content:
                    return content

        # 兜底：旧的 menu_content 字段
        content = self._config.get("menu_content", "")
        return content if content else "菜单为空，请在插件设置中填写菜单内容"
