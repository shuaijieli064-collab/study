import os
import sys
from flask import Blueprint, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.ai_service import chat_completion
from services.kb_service import get_affair_info, search_knowledge

affairs_bp = Blueprint("affairs", __name__, url_prefix="/api/affairs")

# 事务关键词映射
AFFAIR_KEYWORDS = {
    "请假": ["请假", "病假", "事假", "外出", "缺课"],
    "奖学金": ["奖学金", "国奖", "校奖", "学业奖学金"],
    "助学金": ["助学金", "助学", "贫困补助", "经济困难"],
    "证件补办": ["补办", "证件", "学生证", "一卡通", "校园卡"],
    "转专业": ["转专业", "换专业", "专业调整"],
    "休学": ["休学", "暂停学业", "停课"],
    "复学": ["复学", "返校", "恢复学业"],
    "成绩查询": ["成绩", "绩点", "GPA", "挂科", "补考", "重修"],
    "毕业手续": ["毕业", "毕业证", "学位证", "离校"],
    "宿舍调换": ["宿舍", "换寝室", "调寝", "住宿"],
}


def _detect_affair_type(query):
    """检测查询中包含的事务类型"""
    query_lower = query.lower()
    for affair, keywords in AFFAIR_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            return affair
    return None


def _build_kb_context(affair_type):
    """构建知识库上下文"""
    info = get_affair_info(affair_type) if affair_type else None
    if info:
        if isinstance(info, dict):
            return "\n".join(f"**{k}**：{v}" for k, v in info.items())
        return str(info)
    return ""


@affairs_bp.route("/query", methods=["POST"])
def query_affair():
    """校园事务智能问答"""
    data = request.json or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "请输入您的问题"}), 400

    affair_type = _detect_affair_type(query)
    kb_context = _build_kb_context(affair_type)

    # Supplement with full-text knowledge search when structured info is missing
    if not kb_context:
        search_results = search_knowledge(query)
        if search_results:
            kb_context = "\n".join(r["content"] for r in search_results)

    system_prompt = (
        "你是一位专业的高校学生事务助手，熟悉高校各类学生事务的办理流程、"
        "所需材料和注意事项。请用清晰、结构化的方式回答学生的问题，包括：\n"
        "1. 办理流程（分步骤说明）\n"
        "2. 所需材料清单\n"
        "3. 办理地点和时间\n"
        "4. 注意事项\n"
        "如果涉及具体规定，请说明仅供参考，以学校实际规定为准。"
        "使用 Markdown 格式，配合 emoji 增加可读性。"
    )

    if kb_context:
        system_prompt += f"\n\n【知识库参考信息】\n{kb_context}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]
    result = chat_completion(messages, temperature=0.4)
    return jsonify({"result": result, "affair_type": affair_type})


@affairs_bp.route("/template", methods=["POST"])
def generate_template():
    """生成标准化申请模板"""
    data = request.json or {}
    template_type = data.get("type", "").strip()
    user_info = data.get("user_info", {})

    if not template_type:
        return jsonify({"error": "请指定申请类型"}), 400

    info_str = ""
    if user_info:
        info_str = "\n".join(f"{k}：{v}" for k, v in user_info.items() if v)

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位专业的高校学生事务助手，擅长撰写各类学生申请材料。"
                "请生成规范、正式的申请模板，格式清晰，可直接使用或稍作修改后使用。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"请生成一份【{template_type}】的标准申请模板。\n"
                f"{'学生信息：' + chr(10) + info_str if info_str else ''}\n\n"
                "要求：格式规范，包含必要的申请要素，用[...]标注需要填写的内容。"
            ),
        },
    ]
    result = chat_completion(messages, temperature=0.3)
    return jsonify({"result": result})


@affairs_bp.route("/types", methods=["GET"])
def get_affair_types():
    """获取支持的事务类型列表"""
    types = list(AFFAIR_KEYWORDS.keys())
    return jsonify({"types": types})


@affairs_bp.route("/chat", methods=["POST"])
def affairs_chat():
    """多轮对话（校园事务）"""
    data = request.json or {}
    history = data.get("history", [])
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "请输入消息"}), 400

    messages = [
        {
            "role": "system",
            "content": (
                "你是智校通平台的校园事务助手，专门帮助大学生解答校园事务相关问题，"
                "包括请假、奖助学金申请、证件补办、成绩查询、宿舍调换等。"
                "回答要简洁准确，分步骤说明，并提示学生以学校实际规定为准。"
            ),
        }
    ]
    for item in history[-10:]:
        if item.get("role") in ("user", "assistant") and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": message})

    result = chat_completion(messages, temperature=0.5)
    return jsonify({"result": result})
