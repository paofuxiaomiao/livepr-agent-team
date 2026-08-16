# LivePR 项目展示页

这是舆情宝 LivePR 的静态项目展示网站，采用编辑部案例文章的叙事结构，呈现真实问题、Agent 协作、Skill 契约、安全机制、MVP 证据和团队信息。

## 本地预览

在仓库根目录执行：

```bash
python3 -m http.server 4173 --directory web
```

然后打开 <http://127.0.0.1:4173>。

页面为零框架、零构建依赖的原生 HTML/CSS/JavaScript，直接托管到 GitHub Pages、Vercel、Cloudflare Pages 或任意静态服务器即可。

## 文件结构

```text
web/
├── index.html                    # 页面内容与语义结构
├── styles.css                   # 编辑部风格、响应式布局与动画
├── main.js                      # 阅读进度、章节定位、移动菜单
└── assets/
    ├── livepr-hero.jpg           # Image 2 概念配图
    ├── livepr-host-briefing.jpg  # Image 2 概念配图
    ├── livepr-evidence-table.jpg # Image 2 概念配图
    └── livepr-dashboard-evidence.png # MVP 实际运行截图
```

## 视觉与证据说明

- 三张情境图由 GPT Image 2 生成，用于概念演绎；页面中已逐张标注，不代表真实活动、人物或客户。
- 仪表盘图片来自仓库内可运行 MVP，属于真实项目运行证据；其中事件与数据为模拟场景。
- 视觉方向遵循 Awwwards 编辑型案例页：大标题、杂志式留白、右侧粘性索引、时间码和证据标签，并加入 LivePR 的安全橙识别色。

## 发布前检查

1. 确认 GitHub 仓库是否需要从私有改为公开。
2. 若使用 GitHub Pages，把发布目录设为 `web/`，或通过 Actions 发布该目录。
3. 若使用自定义域名，补充绝对地址形式的 Open Graph 图片链接。
