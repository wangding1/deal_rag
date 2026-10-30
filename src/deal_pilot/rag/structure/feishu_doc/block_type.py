"""飞书文档块类型枚举，数值对应飞书 block_type 编号。"""

from enum import IntEnum, unique


@unique
class BlockType(IntEnum):
    """已列出的飞书块类型；枚举成员不表示对应解析器已经实现。

    本表不宣称覆盖飞书未来或全部扩展类型。未列出的编号仍可作为 int
    保存在 BlockNode.block_type 中，不能统一改成 UNDEFINED 而丢失原值。
    UNDEFINED 仅表示飞书自身返回的 999。
    """

    PAGE = 1  # page · 页面 Block（文档根）
    TEXT = 2  # text · 文本 Block
    HEADING1 = 3  # heading1 · 一级标题
    HEADING2 = 4  # heading2 · 二级标题
    HEADING3 = 5  # heading3 · 三级标题
    HEADING4 = 6  # heading4 · 四级标题
    HEADING5 = 7  # heading5 · 五级标题
    HEADING6 = 8  # heading6 · 六级标题
    HEADING7 = 9  # heading7 · 七级标题
    HEADING8 = 10  # heading8 · 八级标题
    HEADING9 = 11  # heading9 · 九级标题
    BULLET = 12  # bullet · 无序列表
    ORDERED = 13  # ordered · 有序列表
    CODE = 14  # code · 代码块
    QUOTE = 15  # quote · 引用
    # 16 在飞书官方 BlockType 表中无定义
    TODO = 17  # todo · 待办事项
    BITABLE = 18  # bitable · 多维表格
    CALLOUT = 19  # callout · 高亮块
    CHAT_CARD = 20  # chat_card · 会话卡片
    DIAGRAM = 21  # diagram · 流程图 / UML
    DIVIDER = 22  # divider · 分割线
    FILE = 23  # file · 文件
    GRID = 24  # grid · 分栏
    GRID_COLUMN = 25  # grid_column · 分栏列
    IFRAME = 26  # iframe · 内嵌网页
    IMAGE = 27  # image · 图片
    ISV = 28  # isv · 开放平台小组件
    MINDNOTE = 29  # mindnote · 思维笔记
    SHEET = 30  # sheet · 电子表格
    TABLE = 31  # table · 表格
    TABLE_CELL = 32  # table_cell · 表格单元格
    VIEW = 33  # view · 视图
    QUOTE_CONTAINER = 34  # quote_container · 引用容器
    TASK = 35  # task · 任务
    OKR = 36  # okr · OKR
    OKR_OBJECTIVE = 37  # okr_objective · OKR Objective
    OKR_KEY_RESULT = 38  # okr_key_result · OKR Key Result
    OKR_PROGRESS = 39  # okr_progress · OKR 进展
    ADD_ONS = 40  # add_ons · 文档小组件
    JIRA_ISSUE = 41  # jira_issue · Jira 问题
    WIKI_CATALOG = 42  # wiki_catalog · Wiki 子页面列表（旧）
    BOARD = 43  # board · 画板
    AGENDA = 44  # agenda · 议程
    AGENDA_ITEM = 45  # agenda_item · 议程项
    AGENDA_ITEM_TITLE = 46  # agenda_item_title · 议程项标题
    AGENDA_ITEM_CONTENT = 47  # agenda_item_content · 议程项内容
    LINK_PREVIEW = 48  # link_preview · 链接预览
    SOURCE_SYNCED = 49  # source_synced · 源同步块
    REFERENCE_SYNCED = 50  # reference_synced · 引用同步块
    SUB_PAGE_LIST = 51  # sub_page_list · Wiki 子页面列表（新）
    AI_TEMPLATE = 52  # ai_template · AI 模板
    UNDEFINED = 999  # undefined · 未支持 Block
