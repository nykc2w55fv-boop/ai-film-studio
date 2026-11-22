# 公开分发验收｜2026-11-23

## 授权与内容边界

- 用户在本轮明确确认：当前完整 GitHub 仓库及 `v0.2.0` Release 中的内容拥有公开分发授权。此前授权仅覆盖私有仓库与私有 Plugin，不以那次授权代替本轮确认。
- 公开时的 `main` 提交 `a2a836a` 跟踪 102 个文件，其中 16 个为构建实际使用的顶层大师研究输入。`01_PROJECTS/`、`04_ASSET_LIBRARY/`、`dist/` 下无跟踪文件；原始私人影片项目和媒体素材未进入源码提交。
- 对这 102 个跟踪文件及其中的 ZIP 内容检查常见私钥、GitHub/OpenAI/Slack 令牌和 AWS 密钥特征，命中 0。另对 Release 下载的系统 ZIP（250 个文件）与 Plugin ZIP（252 个文件）检查同类特征，命中 0。该扫描不能证明不存在其他类型的敏感信息；公开权利由用户确认。

## 发布与访问证据

- `main` 上的公开说明提交 `a2a836a` 的 GitHub Actions 验证运行 `45047379928` 为 `completed/success`。
- 保持 `v0.2.0` 标签及原四个 Release 附件不变；Release 页面说明已更新，明确 GitHub 包公开与个人 ChatGPT Plugin 安装是两回事。下载 ZIP 的 SHA-256 验收沿用 `ACCEPTANCE_0.2.0_20261106.md` 中记录的结果。
- 用户个人 ChatGPT Plugin 元数据为 `scope=USER`、`discoverability=PRIVATE`、`version=0.2.0`；仓库公开不改变此权限，其他人不能仅凭 GitHub 链接在自己的 ChatGPT 中调用该实例。
- GitHub API 返回 `visibility=public`、`private=false`。不带登录凭据的仓库 API 请求也返回 `public`，不带凭据的 Release API 请求能读取 `v0.2.0` 和 4 个附件元数据。随后不带登录凭据下载四个附件到独立测试目录，两个 ZIP 均与公开的 `.sha256` 文件一致。

## 可见性事件边界

本轮开始时意外发现仓库为 `public`，与先前私有要求不符，已立即恢复 `private` 并由两个接口核对。用户随后明确要求公开当前完整仓库与 Release、确认公开分发授权；完成内容扫描和说明更新后，再切换为 `public` 并作未登录访问核对。GitHub 事件接口仅返回一条较早的 `PublicEvent`；无法据此确定本轮前公开状态持续的起止时间，也不能证明公开期间没有第三方复制。
