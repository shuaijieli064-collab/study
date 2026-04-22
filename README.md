# 智校通——面向高校场景的AI学习与事务辅助平台

本仓库收录大学生创新大赛项目相关文档与完整实现代码。

## 项目简介

**智校通** 是一个面向高校场景的AI学习与事务辅助平台，基于成熟大模型技术与校园专属知识库，围绕大学生日常高频需求，构建集学习辅助、校园事务问答和个性化成长支持于一体的垂直AI应用系统。

## 核心功能

| 模块 | 功能 |
|------|------|
| 📚 AI学术辅助 | 课件知识点提炼、练习题生成、复习计划、文献综述框架、实验报告、错题分析 |
| 🏫 校园事务问答 | 请假/奖助学金/证件补办等流程查询、多轮对话、申请模板生成 |
| 🎯 个性化成长 | 学业规划建议、简历优化、面试训练、校园生活导航 |

## 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置 AI API（可选）

```bash
cp backend/.env.example backend/.env
# 编辑 .env 填入 AI_API_KEY 等配置
```

> 不配置 API Key 时，平台以演示模式运行，返回示例结果。

### 3. 启动服务

```bash
cd backend
python app.py
```

浏览器访问 `http://localhost:5000` 即可使用。

## 项目结构

```
study/
├── README.md
├── 项目书.md                  # 大学生创新大赛项目书
├── .gitignore
├── backend/                   # Python Flask 后端
│   ├── app.py                 # 主应用入口
│   ├── config.py              # 配置文件
│   ├── requirements.txt       # 依赖列表
│   ├── .env.example           # 环境变量示例
│   ├── routes/
│   │   ├── academic.py        # 学术辅助接口
│   │   ├── affairs.py         # 校园事务接口
│   │   └── growth.py          # 成长助手接口
│   └── services/
│       ├── ai_service.py      # AI API 调用封装
│       └── kb_service.py      # 知识库服务
├── data/
│   └── campus_knowledge.json  # 校园知识库（示例数据）
└── frontend/                  # Web 前端
    ├── index.html             # 单页面应用主页
    └── static/
        ├── css/style.css      # 样式表
        └── js/app.js          # 前端逻辑
```

## 技术栈

- **后端**：Python 3.8+，Flask 3.x，Flask-CORS
- **AI 接入**：OpenAI Python SDK（兼容任意 OpenAI 格式接口）
- **文档解析**：PyPDF2（PDF）、python-docx（Word）
- **前端**：原生 HTML5 / CSS3 / JavaScript（无需 Node.js）
- **知识库**：JSON 文件（可扩展为向量数据库）

## API 接口说明

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/academic/extract-knowledge` | 知识点提炼 |
| POST | `/api/academic/generate-questions` | 练习题生成 |
| POST | `/api/academic/study-plan` | 复习计划生成 |
| POST | `/api/academic/literature-review` | 文献综述框架 |
| POST | `/api/academic/lab-report` | 实验报告辅助 |
| POST | `/api/academic/wrong-questions` | 错题分析 |
| POST | `/api/affairs/chat` | 事务多轮对话 |
| POST | `/api/affairs/query` | 事务单次查询 |
| POST | `/api/affairs/template` | 申请模板生成 |
| GET  | `/api/affairs/types` | 事务类型列表 |
| POST | `/api/growth/career-plan` | 学业规划建议 |
| POST | `/api/growth/resume` | 简历优化 |
| POST | `/api/growth/interview` | 面试训练 |
| POST | `/api/growth/campus-nav` | 校园导航 |
| POST | `/api/growth/exam-reminder` | 考试提醒计划 |
| GET  | `/api/health` | 服务健康检查 |

## 文档目录

- [大学生创新大赛项目书初稿](./项目书.md)