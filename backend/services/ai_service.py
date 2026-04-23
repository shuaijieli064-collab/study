import json
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AI_API_KEY, AI_API_BASE, AI_MODEL, AI_TIMEOUT_SECONDS


def chat_completion(messages, temperature=0.7, max_tokens=2000):
    """调用 AI 接口获取回复"""
    if not AI_API_KEY:
        return _mock_response(messages)

    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": AI_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            f"{AI_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=AI_TIMEOUT_SECONDS
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            return content
        else:
            error_msg = response.text
            return f"[AI服务返回错误: {response.status_code} - {error_msg}]"

    except requests.exceptions.Timeout:
        return "[AI服务超时，请稍后重试]"
    except Exception as e:
        return f"[AI服务暂时不可用: {str(e)}]"


def _mock_response(messages):
    last = messages[-1]["content"] if messages else ""
    if "知识点" in last or "课件" in last or "总结" in last:
        return (
            "**课件知识点提炼（演示）**\n\n"
            "### 核心知识点\n\n"
            "1. **核心概念** ★★★：本章围绕主要理论展开，包括基本定义、原理与应用场景。\n"
            "2. **重要��理** ★★★：掌握定理推导过程及其适用条件。\n"
            "3. **典型例题** ★★☆：通过例题理解知识点的实际应用方法。\n"
            "4. **易错点** ★★☆：注意区分相似概念，避免混淆。\n\n"
            "### 注意事项\n\n"
            "- 重点掌握定义与定理，理解其适用范围\n"
            "- 多做练习题，加深对概念的理解\n"
            "- 及时整理错题，避免重复犯错\n\n"
            "> ⚠️ 当前为演示模式，请在 `.env` 文件中配置 `AI_API_KEY` 以启用真实AI功能。"
        )
    if "面试题" in last or "面试问题" in last or "面试官" in last:
        return (
            "**常见面试题目（演示）**\n\n"
            "### 🧩 行为面试题\n\n"
            "1. 请做一下自我介绍（3分钟以内）\n"
            "2. 请介绍一个你主导完成的项目，遇到了哪些挑战？\n"
            "3. 你在团队合作中承担过什么角色？遇到冲突如何处理？\n\n"
            "### 💡 情景题\n\n"
            "4. 如果你和同事对某个方案有分歧，你会如何处理？\n"
            "5. 假设你同时有多个紧急任务，如何安排优先级？\n\n"
            "### 🔧 专业题\n\n"
            "6. 请介绍你掌握的核心技能及实际应用经验。\n"
            "7. 你对行业最新趋势有哪些了解和看法？\n"
            "8. 你有哪些需要提升的地方，有什么改进计划？\n\n"
            "> ⚠️ 当前为演示模式，请配置 `AI_API_KEY` 以启用真实AI功能。"
        )
    if "练习题" in last or "题目" in last:
        return (
            "**自动生成练习题（演示）**\n\n"
            "### 单选题\n\n"
            "1. 下列说法正确的是（ ）\n\n"
            "   A. 选项A  B. 选项B  C. 选项C  D. 选项D\n\n"
            "   **参考答案**：C\n\n"
            "### 简答题\n\n"
            "2. 请简述该知识点的核心原理及应用场景。\n\n"
            "   **参考答案**：该知识点的核心原理包括……主要应用于……\n\n"
            "> ⚠️ 当前为演示模式，请配置 `AI_API_KEY` 以启用真实AI功能。"
        )
    if "复习计划" in last or "计划" in last:
        return (
            "**个性化复习计划（演示）**\n\n"
            "### 第1周：基础巩固\n"
            "- 梳理基础概念，完成课本复习\n"
            "- 做课后习题，巩固基础知识\n\n"
            "### 第2周：重点攻克\n"
            "- 重点攻克薄弱章节，整理错题\n"
            "- 完成一套模拟练习题\n\n"
            "> ⚠️ 当前为演示模式，请配置 `AI_API_KEY` 以启用真实AI功能。"
        )
    if "请假" in last:
        return (
            "**请假流程（演示）**\n\n"
            "### 办理流程\n\n"
            "1. 登录学校教务系统，进入学生请假模块\n"
            "2. 填写请假原因、起止时间，上传证明材料\n"
            "3. 提交申请后，等待辅导员审批\n"
            "4. 审批通过后，系统自动通知\n\n"
            "> ⚠️ 当前为演示模式，请配置 `AI_API_KEY` 以启用真实AI功能。"
        )
    if "奖学金" in last or "助学金" in last:
        return (
            "**奖助学金申请流程（演示）**\n\n"
            "### 申请流程\n\n"
            "1. 关注学院通知，了解申请时间\n"
            "2. 在教务系统中填写申请表\n"
            "3. 准备所需材料提交辅导员\n"
            "4. 班级评议后上报学院审核\n\n"
            "> ⚠️ 当前为演示模式，请配置 `AI_API_KEY` 以启用真实AI功能。"
        )
    return (
        "**智校通 AI 助手**\n\n"
        "您好！我是智校通 AI 助手，可以帮助您：\n\n"
        "- 📚 提炼课程知识点、生成练习题\n"
        "- 🏫 查询校园事务流程\n"
        "- 🎯 提供学业规划建议\n\n"
        f"您的问题：{last[:100]}{'...' if len(last) > 100 else ''}\n\n"
        "> ⚠️ 当前为演示模式，请配置 `AI_API_KEY`。"
    )