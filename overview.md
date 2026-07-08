# 英语趣学 H5 · 实现概览（v0.3 开发落地）

> 状态：**前端原型可运行 + 后端脚手架完成**。按 PRD v0.2 + 技术方案排期，落地了 P1（MVP）核心功能的可交互 H5 与原生可部署的 Laravel API 脚手架。

## 一、已实现（前端 H5，浏览器直接运行）
路径：`index.html` + `css/styles.css` + `js/words.js` + `js/sm2.js` + `js/app.js`

| 模块 | 实现要点 |
|------|----------|
| 移动优先外壳 | 480px 居中 App 壳，PC 端圆角卡片式长尾可用；玻璃拟态 + 渐变 |
| 主题切换 | 亮色 / 暗色 / 跟随系统（data-theme 实时切换，符合 Premium 规范） |
| 首页 | 每日签到 +10、积分/连续签到/已学词三统计、L1–L3 关卡进度条、到期复习入口 |
| 图像故事联想学习 | 词卡：Emoji 大图 → 点"看释义/联想"揭示音标·释义·💡联想故事·例句；🔊 浏览器 TTS 发音 |
| 学习→测验闭环 | 学完一组进入 4 选 1 释义测验，即时对错反馈（PRD 核心 WAL 闭环） |
| SM-2 间隔重复 | `js/sm2.js` 与后端算法对齐；错题次日重练，对题按系数推后 |
| 复习 | 到期词自动进入复习队列，断网本地队列（localStorage 持久化） |
| 排行榜 | 本周积分榜（本地模拟对手 + "我"），后端接实时周快照 |
| 成就系统 | 9 枚成就（破土/神枪手/百宝箱/小火苗/铁粉丝/L1–L3 通关/温故），解锁 toast |
| 底部导航 | 首页 / 复习 / 排行 / 成就 |

**数据**：36 词（L1–L3）演示词库，含音标/中文释义/Emoji/联想故事/例句，符合"趣味须准确"标准（联想区与正确拼写视觉分离）。

## 二、已完成（后端 Laravel 11 脚手架，可 `php artisan` 部署）
路径：`backend/`

- 迁移 6 张表：`users`(含 age_group 未成年分流) · `words`(含 accuracy_reviewed 审核位) · `review_items`(SM-2 字段) · `user_stats` · `checkins` · `leaderboard_snapshots`(周快照防全量排序)
- 模型 6 个：User / Word / ReviewItem / UserStat / Checkin / LeaderboardSnapshot（关系 + 类型转换）
- 服务：`SpacedRepetitionService`（SM-2 权威计算 + dueWords/advance）
- 种子：`WordSeeder`（36 词，口径 GSL+CET-4，accuracy_reviewed 默认待审）
- 路由 `api.php`：register/login(Sanctum) · /levels · /session/start · /session/submit(SM-2+积分) · /review/due · /checkin · /leaderboard
- `composer.json` / `.env.example`（含 `AD_MIN_AGE=18` 合规变量）

## 三、如何预览
- **直接打开**：浏览器打开 `index.html` 即可（相对路径已验证 200）。
- **本地服务**：`python -m http.server 8080` 后访问 `http://127.0.0.1:8080/`（已验证可访问）。
- 后端：`cd backend && composer install && cp .env.example .env && php artisan key:generate && php artisan migrate --seed`。

## 四、下一步建议（按性价比）
1. **A/B 验证假设 A1**：用零成本 Emoji 联想 vs 普通释义，验证"联想是否真提升留存"（MVP 最危险假设）。
2. **后端联调**：把前端 localStorage 替换为 Laravel API（契约已在 `api.php` 定好）。
3. **账号体系落地**：游客/注册、未成年家长同意流（age_group 分流已留字段）。
4. **内容审核流水线**：`words.accuracy_reviewed` 置位流程 + 首期扩词到 2000–3000。

## 五、关键决策回顾（已收敛）
免费+广告 · 趣味须准确 · 间隔重复(SM-2) · 移动优先 · 词库自整理(GSL+CET-4) 合规可商用。
