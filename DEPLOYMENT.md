# 🚀 GitHub Pages 網站部署指南

本指南將協助您將 O-RAN × Nephio RAG 專案網站部署至 GitHub Pages，以獲得全球觸及和最佳 SEO 效果。

## 📋 部署前檢查清單

### 必要條件
- [x] GitHub 帳號
- [x] 專案代碼庫 (repository)
- [x] 基本的 Git 操作知識

### 檔案結構確認
```
oran-nephio-rag/
├── _config.yml                 # Jekyll 配置
├── _layouts/
│   └── default.html            # 預設版面
├── _includes/
│   └── head.html              # HTML head 部分
├── _pages/
│   └── documentation.md        # 文檔頁面
├── assets/
│   ├── styles/
│   │   └── main.css           # 主要樣式
│   ├── scripts/
│   │   └── main.js            # JavaScript 功能
│   └── images/                # 圖片資源
├── .github/
│   └── workflows/
│       └── pages.yml          # GitHub Actions 工作流程
├── index.html                 # 主頁面
├── robots.txt                 # 搜索引擎爬蟲指令
├── sitemap.xml               # 網站地圖
├── site.webmanifest          # PWA 清單
├── sw.js                     # Service Worker
├── Gemfile                   # Ruby 依賴
└── DEPLOYMENT.md             # 本部署指南
```

## 🔧 部署步驟

### 1. 啟用 GitHub Pages

1. 進入您的 GitHub 專案頁面
2. 點選 **Settings** 標籤
3. 滾動至 **Pages** 部分
4. 在 **Source** 下選擇 **GitHub Actions**
5. 點選 **Save**

### 2. 配置自訂網域 (可選)

如果您有自訂網域：

1. 在 **Pages** 設定中的 **Custom domain** 輸入您的網域
2. 勾選 **Enforce HTTPS**
3. 在您的網域 DNS 設定中添加 CNAME 記錄：
   ```
   www.yourdomain.com -> username.github.io
   ```

### 3. 更新配置文件

編輯 `_config.yml` 檔案，更新以下設定：

```yaml
# 基本資訊
title: "您的專案標題"
description: "您的專案描述"
url: "https://yourusername.github.io"  # 更新為您的 GitHub Pages URL
baseurl: "/your-repo-name"             # 更新為您的專案名稱

# 作者資訊
author:
  name: "您的名字"
  email: "your-email@example.com"

# GitHub 資訊
github_username: yourusername
repository: your-repo-name
github:
  repository_url: "https://github.com/yourusername/your-repo-name"
```

### 4. 設定 Google Analytics (可選)

1. 建立 Google Analytics 4 屬性
2. 取得追蹤 ID
3. 在 `_config.yml` 中新增：
   ```yaml
   google_analytics: G-XXXXXXXXXX
   ```

### 5. 提交並推送變更

```bash
git add .
git commit -m "feat: 新增 GitHub Pages 網站設定"
git push origin main
```

### 6. 檢查部署狀態

1. 前往 **Actions** 標籤
2. 查看 "Build and Deploy GitHub Pages" 工作流程
3. 等待部署完成 (通常需要 2-5 分鐘)

## 🌐 SEO 優化設定

### Google Search Console

1. 前往 [Google Search Console](https://search.google.com/search-console/)
2. 新增您的網站
3. 驗證所有權 (使用 HTML 標籤方法)
4. 提交 sitemap.xml：`https://yourusername.github.io/your-repo-name/sitemap.xml`

### Bing Webmaster Tools

1. 前往 [Bing Webmaster Tools](https://www.bing.com/webmasters/)
2. 新增並驗證您的網站
3. 提交 sitemap.xml

### 社交媒體優化

1. 建立高品質的 Open Graph 圖片 (1200x630px)
2. 將圖片放置於 `assets/images/og-image.png`
3. 測試社交媒體分享：
   - Facebook: [Sharing Debugger](https://developers.facebook.com/tools/debug/)
   - Twitter: [Card Validator](https://cards-dev.twitter.com/validator)
   - LinkedIn: [Post Inspector](https://www.linkedin.com/post-inspector/)

## 📊 效能監控設定

### Google PageSpeed Insights

定期檢查網站效能：
- 桌面版：目標 95+ 分
- 行動版：目標 90+ 分

### Core Web Vitals

監控重要指標：
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms  
- **CLS** (Cumulative Layout Shift): < 0.1

### GTmetrix

設定定期監控和警報：
1. 註冊 [GTmetrix](https://gtmetrix.com/) 帳號
2. 新增網站監控
3. 設定效能警報

## 🔍 國際化設定

### 多語言支援

如需支援多語言：

1. 建立語言特定目錄：
   ```
   /en/           # 英文版本
   /zh-tw/        # 繁體中文版本
   /ja/           # 日文版本
   ```

2. 更新 `_config.yml`：
   ```yaml
   plugins:
     - jekyll-multiple-languages-plugin
   
   languages: ["zh-tw", "en", "ja"]
   default_lang: "zh-tw"
   exclude_from_localizations: ["assets", "admin"]
   ```

### hreflang 標籤

確保每個頁面都有正確的 hreflang 標籤：
```html
<link rel="alternate" hreflang="zh-tw" href="https://example.com/" />
<link rel="alternate" hreflang="en" href="https://example.com/en/" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

## 🚀 進階優化

### CDN 設定

使用 Cloudflare 進行全球加速：

1. 註冊 [Cloudflare](https://www.cloudflare.com/) 帳號
2. 新增您的網域
3. 更新 DNS 名稱伺服器
4. 啟用以下功能：
   - Brotli 壓縮
   - 自動縮小化
   - 瀏覽器快取 TTL

### 安全標頭

在 Cloudflare 或您的伺服器設定中新增安全標頭：
```
Content-Security-Policy: default-src 'self' https:
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### PWA 優化

確保 Progressive Web App 功能正常：

1. 測試 Service Worker 運作
2. 驗證 Web App Manifest
3. 使用 Lighthouse 檢查 PWA 分數
4. 測試離線功能

## 📈 分析與監控

### 流量分析工具

1. **Google Analytics 4**
   - 設定目標轉換
   - 監控使用者行為流程
   - 追蹤自訂事件

2. **Microsoft Clarity** (可選)
   ```yaml
   # _config.yml
   microsoft_clarity: YOUR_CLARITY_ID
   ```

3. **Hotjar** (可選)
   ```yaml
   # _config.yml
   hotjar_id: YOUR_HOTJAR_ID
   ```

### 錯誤監控

設定前端錯誤監控：
1. 註冊 [Sentry](https://sentry.io/) 帳號
2. 建立新專案
3. 在 JavaScript 中新增 Sentry SDK

## 🔧 故障排除

### 常見問題

#### 1. 網站無法正常顯示
- 檢查 GitHub Actions 是否成功執行
- 確認 `_config.yml` 設定正確
- 檢查檔案路徑和命名

#### 2. CSS/JS 檔案載入失敗
- 確認 `baseurl` 設定正確
- 檢查檔案路徑是否使用相對 URL
- 確認檔案存在於正確位置

#### 3. Jekyll 建置失敗
- 檢查 `Gemfile` 依賴版本
- 確認 YAML 語法正確
- 查看 Actions 日誌錯誤訊息

#### 4. 搜索引擎未收錄
- 確認 `robots.txt` 允許爬蟲
- 檢查 `sitemap.xml` 格式正確
- 提交至 Google Search Console

### 除錯工具

1. **GitHub Actions 日誌**
   - 查看建置過程詳細資訊
   - 識別錯誤和警告

2. **瀏覽器開發者工具**
   - 檢查網路請求
   - 除錯 JavaScript 錯誤
   - 分析效能問題

3. **線上驗證工具**
   - [W3C HTML Validator](https://validator.w3.org/)
   - [CSS Validator](https://jigsaw.w3.org/css-validator/)
   - [Schema Markup Validator](https://validator.schema.org/)

## 📞 技術支援

如遇到部署問題，可透過以下方式尋求協助：

- 📧 **Email**: [dev-team@company.com](mailto:dev-team@company.com)
- 🐛 **GitHub Issues**: [專案 Issues 頁面](https://github.com/company/oran-nephio-rag/issues)
- 💬 **討論區**: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)
- 📖 **官方文檔**: [Jekyll 官方文檔](https://jekyllrb.com/docs/)

## 🎯 成功指標

部署成功後，您的網站應該達到以下標準：

### 技術指標
- [x] 部署成功無錯誤
- [x] 所有頁面正常載入
- [x] 響應式設計在各裝置運作良好
- [x] PWA 功能正常

### SEO 指標
- [x] Google PageSpeed Insights 分數 > 90
- [x] 所有頁面有正確的 meta 標籤
- [x] Sitemap 成功提交至搜索引擎
- [x] Social media 分享預覽正常

### 使用者體驗
- [x] 載入時間 < 3 秒
- [x] 互動功能正常運作
- [x] 導航直觀易用
- [x] 多語言切換順暢

---

**🎉 恭喜！您的 O-RAN × Nephio RAG 網站已成功部署至 GitHub Pages，準備好迎接全球使用者了！**