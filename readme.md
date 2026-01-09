# 携程酒店信息爬虫

## 使用方法

### 1. 创建虚拟环境
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器
```bash
python -m playwright install chromium
```

或者安装所有浏览器：
```bash
python -m playwright install
```

### 4. 首次使用需要登录
程序会自动打开浏览器，请手动登录携程账号。登录信息会被保存，后续使用无需重复登录。

**注意**：
- 如果使用 `inheritChromeInfo` 继承本地 Chrome 的登录信息，需要先在本地 Chrome 浏览器中登录携程
- 首次运行时会检测 Playwright 环境，如有问题会提示重新安装

### 5. 运行程序
```bash
python main.py
```

## 常见问题

### Q: 提示 "浏览器未安装" 或 "启动失败"
A: 运行以下命令重新安装浏览器：
```bash
python -m playwright install chromium
```

### Q: 更换电脑后无法运行
A: Playwright 浏览器路径可能失效，重新执行安装命令：
```bash
python -m playwright install chromium --force
```

### Q: 无法继承 Chrome 登录信息
A: 确保本地 Chrome 浏览器已登录携程，并关闭所有 Chrome 进程后重试

## 项目结构
```
ctrip-hotel-spider/
├── main.py              # 主程序入口
├── pipline.py           # 爬取流程控制
├── saveInfo.py          # 数据保存逻辑
├── configs.py           # 配置文件
├── requirements.txt     # 依赖列表
└── readme.md           # 使用说明
```

## 功能说明
1. 获取酒店基本信息和图片
2. 下载酒店图片（官方图、用户图、精选图）
3. 获取酒店评论（可设置评分过滤）
4. 获取酒店详细描述
5. 智能筛选精选图片

## 输出目录
```
hotel_images/
└── {酒店名称}_{酒店ID}/
    ├── hotel_images/        # 官方图片
    ├── user_images/         # 用户上传图片
    ├── hotel_top_images/    # 精选图片
    ├── picked_images/       # 智能筛选的精选图片
    └── comments_and_descriptions/
        ├── {hotel_id}_comments.json
        └── {hotel_id}_description.json
```