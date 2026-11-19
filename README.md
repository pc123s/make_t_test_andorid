# make_t_test_andorid

做T参考工具 Android 版：WebView 壳应用，内置做T策略参考页面（ECharts 图表），支持交易记录导出为 CSV（通过原生接口保存到手机存储）。

## 快速安装

下载仓库根目录的 [zuot_v1.apk](zuot_v1.apk) 传到手机，点击安装即可（需允许"安装未知来源应用"）。

## 目录结构

```
zuot-build/
├── app/                  # 应用源码与资源
│   ├── AndroidManifest.xml
│   ├── assets/           # index.html / data.js / echarts.min.js（前端页面）
│   ├── res/              # 图标等资源
│   └── src/com/pcc/zuot/MainActivity.java
├── scripts/              # 构建辅助脚本（生成图标、patch index.html）
├── build.sh              # 一键构建脚本（Git Bash）
└── out/zuot_v1.apk       # 构建产物（不入库，由 build.sh 生成）
```

## 构建（Windows）

环境要求：
- Git Bash
- JDK 17（javac / java / keytool）
- Python 3（生成图标、patch 页面）
- Android SDK 组件（放置位置见 build.sh 顶部变量）：
  - build-tools 35.0.0 → `zuot-build/bt/android-15/`（含 aapt2.exe、zipalign.exe、lib/apksigner.jar、lib/d8.jar）
  - platforms;android-35 → `zuot-build/plat/android-35/android.jar`

构建：

```bash
cd zuot-build
bash build.sh
```

产物：`zuot-build/out/zuot_v1.apk`（首次构建会自动生成 keystore：别名 zuot，密码 android）。

## 安装到手机

```bash
adb install -r zuot-build/out/zuot_v1.apk
```

## 说明

- 签名 keystore 不入库，请自行保管（`zuot-build/out/zuot.keystore`）。更新版本需使用同一 keystore 签名才能覆盖安装并保留数据。
- 前端页面源码（index.html / data.js）直接维护在 `zuot-build/app/assets/` 下。
- 若存在网页源项目 `D:/stock/make_t_test`，build.sh 会从中 patch index.html 并复制 assets；否则直接使用 `app/assets` 下的现有文件。
