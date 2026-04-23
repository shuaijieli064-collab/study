import io
import os
import sys
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import MAX_TEXT_LENGTH, MAX_QUERY_LENGTH
from services.ai_service import chat_completion

academic_bp = Blueprint("academic", __name__, url_prefix="/api/academic")

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "md"}

# 文件魔数（Magic Bytes）白名单
_MAGIC_BYTES = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "docx",  # ZIP-based formats (docx, doc with compat)
}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _check_magic_bytes(content, filename):
    """基于文件魔数校验文件类型是否与扩展名匹配（宽松策略：未命中魔数时按扩展名放行）"""
    for magic, ftype in _MAGIC_BYTES.items():
        if content.startswith(magic):
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            # PDF 魔数 → 只允许 .pdf 扩展名
            if ftype == "pdf" and ext != "pdf":
                return False
            # ZIP/docx 魔数 → 只允许 .docx/.doc 扩展名
            if ftype == "docx" and ext not in ("docx", "doc"):
                return False
            return True
    # 文本类文件无魔数，直接放行
    return True


def _extract_text(file):
    """从上传文件中提取文本"""
    raw_name = file.filename or ""
    filename = secure_filename(raw_name).lower()
    if not filename:
        return ""
    content = b""
    try:
        content = file.read()
    except Exception:
        return ""

    if not _check_magic_bytes(content, filename):
        return ""

    if filename.endswith(".txt") or filename.endswith(".md"):
        return content.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return content.decode("utf-8", errors="ignore")

    if filename.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return content.decode("utf-8", errors="ignore")

    return content.decode("utf-8", errors="ignore")


@academic_bp.route("/extract-knowledge", methods=["POST"])
def extract_knowledge():
    """上传课件/教材，提炼知识点"""
    text = ""
    if "file" in request.files:
        f = request.files["file"]
        if f and f.filename and _allowed_file(secure_filename(f.filename or "")):
            text = _extract_text(f)
    if not text:
        json_data = request.get_json(silent=True) or {}
        text = request.form.get("text", "") or json_data.get("text", "")
    text = (text or "").strip()
    if not text:
        return jsonify({"error": "请上传文件或输入文本内容"}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"文本内容过长，请控制在 {MAX_TEXT_LENGTH} 字符以内"}), 400

    preview = text[:3000]
    messages = [
        {
            "role": "system",
            "content": (
                "你是一位专业的大学课程辅导助手。请对用户提供的课程资料进行深度分析，"
                "提炼核心知识点，生成结构化的学习笔记。要求：\n"
                "1. 列出3-8个核心知识点，每个知识点配以简洁解释\n"
                "2. 标注重要程度（★☆☆/★★☆/★★★）\n"
                "3. 指出易错点或注意事项\n"
                "4. 使用 Markdown 格式输出"
            ),
        },
        {"role": "user", "content": f"请提炼以下课程资料中的知识点：\n\n{preview}"},
    ]
    result = chat_completion(messages, temperature=0.5)
    return jsonify({"result": result, "chars_processed": len(text)})


@academic_bp.route("/generate-questions", methods=["POST"])
def generate_questions():
    """根据文本或知识点生成练习题"""
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    try:
        count = max(1, min(int(data.get("count", 5)), 20))
    except (TypeError, ValueError):
        count = 5
    q_type = data.get("type", "mixed")  # single/multiple/short/mixed

    if not content:
        return jsonify({"error": "请提供知识点或课程内容"}), 400
    if len(content) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"内容过长，请控制在 {MAX_TEXT_LENGTH} 字符以内"}), 400

    type_desc = {
        "single": "单选题",
        "multiple": "多选题",
        "short": "简答题",
        "mixed": "单选题、简答题和综合题的混合",
    }.get(q_type, "混合题型")

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位专业的大学课程出题助手。请根据提供的知识点内容出题，"
                "题目要有针对性、难度适中、能考查核心知识。使用 Markdown 格式输出。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"请根据以下内容生成 {count} 道{type_desc}，并附上参考答案：\n\n{content[:2000]}"
            ),
        },
    ]
    result = chat_completion(messages, temperature=0.6)
    return jsonify({"result": result})


@academic_bp.route("/study-plan", methods=["POST"])
def study_plan():
    """生成个性化复习计划"""
    data = request.get_json(silent=True) or {}
    subject = data.get("subject", "").strip()
    exam_date = data.get("exam_date", "").strip()
    weak_points = data.get("weak_points", "").strip()
    available_hours = data.get("available_hours", "2")

    if not subject:
        return jsonify({"error": "请填写课程名称"}), 400
    if len(subject) > MAX_QUERY_LENGTH:
        return jsonify({"error": "课程名称过长"}), 400
    if len(weak_points) > MAX_TEXT_LENGTH:
        return jsonify({"error": "薄弱知识点内容过长"}), 400

    available_hours_value = None
    if available_hours not in (None, ""):
        try:
            available_hours_value = float(available_hours)
        except (TypeError, ValueError):
            return jsonify({"error": "每日可用学习时间格式不正确"}), 400
        if available_hours_value <= 0 or available_hours_value > 24:
            return jsonify({"error": "每日可用学习时间应在 0-24 小时之间"}), 400

    context = f"课程：{subject}"
    if exam_date:
        context += f"\n考试日期：{exam_date}"
    if weak_points:
        context += f"\n薄弱知识点：{weak_points}"
    if available_hours_value is not None:
        context += f"\n每天可用学习时间：{available_hours_value:g} 小时"

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位经验丰富的学习规划师。请根据学生提供的信息，"
                "制定详细、可执行的复习计划。计划要包含：\n"
                "1. 每日/每周学习任务安排\n"
                "2. 重点知识点复习顺序\n"
                "3. 练习题和模拟测试安排\n"
                "4. 考前注意事项\n"
                "使用 Markdown 格式，配合 emoji 增加可读性。"
            ),
        },
        {"role": "user", "content": f"请为我制定复习计划：\n{context}"},
    ]
    result = chat_completion(messages, temperature=0.6)
    return jsonify({"result": result})


@academic_bp.route("/literature-review", methods=["POST"])
def literature_review():
    """文献综述框架辅助"""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "").strip()
    field = data.get("field", "").strip()

    if not topic:
        return jsonify({"error": "请填写研究主题"}), 400
    if len(topic) > MAX_QUERY_LENGTH:
        return jsonify({"error": "研究主题过长"}), 400

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位专业的学术写作助手。请帮助学生构建文献综述框架，"
                "提供写作思路和参考结构，帮助其理清研究脉络。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"研究主题：{topic}\n"
                f"{'研究领域：' + field if field else ''}\n\n"
                "请提供：\n"
                "1. 文献综述的整体框架结构\n"
                "2. 每个部分的写作要点\n"
                "3. 建议关注的研究方向和关键词\n"
                "4. 写作注意事项"
            ),
        },
    ]
    result = chat_completion(messages, temperature=0.6)
    return jsonify({"result": result})


@academic_bp.route("/lab-report", methods=["POST"])
def lab_report():
    """实验报告初稿辅助"""
    data = request.get_json(silent=True) or {}
    experiment = data.get("experiment", "").strip()
    purpose = data.get("purpose", "").strip()
    method = data.get("method", "").strip()
    data_input = data.get("data", "").strip()

    if not experiment:
        return jsonify({"error": "请填写实验名称"}), 400
    if len(experiment) > MAX_QUERY_LENGTH:
        return jsonify({"error": "实验名称过长"}), 400
    if len(purpose) + len(method) + len(data_input) > MAX_TEXT_LENGTH:
        return jsonify({"error": "输入内容过长，请适当精简"}), 400

    content = f"实验名称：{experiment}"
    if purpose:
        content += f"\n实验目的：{purpose}"
    if method:
        content += f"\n实验方法/步骤：{method}"
    if data_input:
        content += f"\n实验数据/观察结果：{data_input}"

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位专业的理工科实验报告写作助手。请根据提供的实验信息，"
                "帮助学生生成规范的实验报告初稿框架和内容建议。"
            ),
        },
        {
            "role": "user",
            "content": f"请帮我撰写实验报告初稿：\n\n{content}",
        },
    ]
    result = chat_completion(messages, temperature=0.5)
    return jsonify({"result": result})


@academic_bp.route("/wrong-questions", methods=["POST"])
def wrong_questions():
    """错题本整理与分析"""
    data = request.get_json(silent=True) or {}
    questions = data.get("questions", "").strip()
    subject = data.get("subject", "").strip()

    if not questions:
        return jsonify({"error": "请输入错题内容"}), 400
    if len(questions) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"错题内容过长，请控制在 {MAX_TEXT_LENGTH} 字符以内"}), 400

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位专业的辅导老师。请对学生提供的错题进行分析，"
                "找出错误原因，给出正确解析，并总结该类题型的解题规律。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"{'课程：' + subject + chr(10) if subject else ''}"
                f"以下是我的错题，请帮我分析错误原因并给出解析：\n\n{questions[:2000]}"
            ),
        },
    ]
    result = chat_completion(messages, temperature=0.5)
    return jsonify({"result": result})
