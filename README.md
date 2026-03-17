# 🤖 AutoJob - AI求职投递助手

> 自动搜索职位、自动投递简历、自动生成Cover Letter

## 功能特点

- 🔍 **多平台职位搜索** - 整合BOSS直聘、拉勾、猎聘等主流招聘平台
- 📝 **智能Cover Letter** - 基于LLM生成个性化求职信
- 🤖 **自动化投递** - 自动填写表单、上传简历
- 📊 **投递管理** - 追踪投递进度、统计分析
- 🔔 **消息推送** - Telegram/邮件实时通知
- 🛡️ **代理池支持** - 代理IP轮换，防封禁
- 🎯 **智能匹配** - 根据偏好筛选职位

## 支持平台

| 平台 | 状态 | 说明 |
|------|------|------|
| BOSS直聘 | ✅ 可用 | 中国主流招聘平台 |
| 拉勾 | 🔄 开发中 | |
| 猎聘 | 🔄 开发中 | |
| JobsDB | 🔄 开发中 | 香港平台 |
| LinkedIn | 🔄 开发中 | |

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 配置

编辑 `config/config.yaml`：

```yaml
database:
  path: "data/autojob.db"

llm:
  provider: "minimax"
  api_key: "your-api-key"

platforms:
  boss:
    enabled: true
```

### 使用

```bash
# 搜索职位
python -m src.cli search Web3 深圳

# 投递简历
python -m src.cli apply 123456 boss --resume resume.pdf

# 查看统计
python -m src.cli stats
```

## 项目结构

```
auto_job/
├── config/               # 配置文件
│   └── config.yaml
├── src/
│   ├── main.py          # 主程序入口
│   ├── cli.py           # 命令行界面
│   ├── core/            # 核心模块
│   │   ├── config.py    # 配置管理
│   │   ├── database.py  # 数据库
│   │   ├── browser.py   # 浏览器自动化
│   │   ├── filter.py    # 职位筛选
│   │   ├── proxy.py     # 代理池
│   │   ├── captcha.py   # 验证码处理
│   │   └── notification.py  # 通知
│   ├── platforms/       # 平台适配器
│   │   ├── base.py      # 基类
│   │   ├── boss.py      # BOSS直聘
│   │   └── ...
│   └── ai/              # AI模块
│       └── cover_letter.py  # Cover Letter生成
├── data/                # 数据存储
├── logs/                # 日志
└── requirements.txt     # 依赖
```

## 配置说明

### 平台配置

```yaml
platforms:
  boss:
    enabled: true
    login_url: "https://www.zhipin.com/"
    search_url: "https://www.zhipin.com/web/geek/job"
```

### 代理配置

```yaml
proxy:
  enabled: true
  pool:
    - host: "127.0.0.1"
      port: 8080
      username: ""
      password: ""
```

### 通知配置

```yaml
notification:
  telegram:
    enabled: true
    token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

## 开发计划

- [x] 基础框架搭建
- [x] 核心模块开发
- [x] BOSS直聘适配器
- [ ] 拉勾平台适配器
- [ ] 猎聘平台适配器
- [ ] JobsDB适配器
- [ ] LinkedIn适配器
- [ ] 代理池集成
- [ ] 验证码处理
- [ ] Telegram命令界面

## 注意事项

1. **合规使用**：请遵守各平台服务条款，控制投递频率
2. **账号安全**：建议使用小号进行测试
3. **数据安全**：简历信息本地存储，注意保护隐私

## License

MIT License
