# iguanren-home · 官仁有话说（静态壁纸版）

iguanren.eu.org 主站源码：读书分享 + 必应每日壁纸（近 30 天卡片流）。

纯静态站点，**零图片存储**——所有图片热链必应官方 CDN（cn.bing.com），流量不占本站。

## 文件结构

```
├── index.html              # 主页（壁纸卡片流 + 灯箱 + 归档 + 悬浮功能）
├── style.css               # 全手写样式，无任何前端框架依赖
├── data.json               # 壁纸数据（Actions 每日自动更新，全量归档）
├── favicon.svg
├── sitemap.xml             # 站点地图（提交搜索引擎收录）
├── robots.txt              # 爬虫规则（指向 sitemap）
├── scripts/fetch_bing.py   # 抓取脚本：必应 HPImageArchive idx=0..7 → data.json
└── .github/workflows/update.yml  # 每天北京时间 0:10 自动抓取并推送
```

## 工作原理

1. **GitHub Actions** 每天北京时间 0:10（UTC 16:10）运行 `fetch_bing.py`
2. 脚本抓必应官方接口最近 8 天壁纸（idx=0 今天 ~ idx=7），合并进 `data.json`，按日期去重
3. **全量归档**：数据永不删除，无限攒历史（每年约 +120KB，零成本）
4. 数据有变化才提交推送（无空提交）
5. **EdgeOne Pages** 连接仓库，检测到 push 自动重新部署
6. 用户访问 iguanren.eu.org 走 EdgeOne 边缘节点，图片直连必应 CDN（缩略图 400x240 / 大图 4K UHD）

## 页面功能

- **昨日壁纸 / 今日壁纸**：点击直接弹窗显示对应日期的 4K 大图
- **历史壁纸**：弹出月份归档选择器（新→旧排列），选择月份后卡片流切换为该月壁纸
- **卡片流**：默认显示最近 30 天，选月份后显示对应月份全部
- **灯箱**：全屏 4K 大图 + 右上角下载 + 底部日期/标题/版权，← → 翻图
- **夜间模式 / 回到顶部**：右下角悬浮（滚动后出现），环形进度条，偏好本地记忆

> 注：必应官方接口仅开放最近 8 天数据，因此**历史数据靠每日自动抓取慢慢攒**——今天上线的站，一年后就能翻看一年的壁纸。

## 部署步骤

1. 在 GitHub 新建仓库（如 `iguanren-home`），把本目录全部文件推送到 main 分支
2. 腾讯云控制台 → EdgeOne Pages → 新建项目，**区域选"中国大陆以外"**（eu.org 域名无法备案）
3. 连接 Git：选择仓库 + main 分支
4. **构建命令留空，输出目录留空**（纯静态，无需构建）
5. 绑定域名 iguanren.eu.org，配置 DNS 生效
6. Actions 每天自动更新，无需人工干预

## 手动更新

仓库 → Actions → `Update Bing Wallpaper Data` → Run workflow 即可立即抓取一次。

## 本地调试

```bash
python3 scripts/fetch_bing.py   # 生成/更新 data.json
python3 -m http.server 8899     # 本地预览 http://127.0.0.1:8899
```

依赖：Python 3.10+，`pip install requests`
