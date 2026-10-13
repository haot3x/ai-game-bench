# 点击计数游戏：DOM 交互契约 v0.2

在 `/workspace/game/` 创建一个 Web 点击计数游戏。构建入口为
`/workspace/game/dist/index.html`，由静态 HTTP 服务启动，不能依赖开发服务器。

<!-- MOPAN_PROMPT_START -->
做一个最简单的点击计数游戏，玩家每点击一次主要按钮，分数恰好加一。
页面初始分数为 0，不操作时分数保持不变，连续多次点击仍然有效。
分数必须显示在唯一可见的 DOM 元素 `[data-testid="score"]` 中，元素文本只包含
非负十进制整数；唯一可见且可点击的按钮使用 `data-testid="click-target"`。
不要仅在 canvas、隐藏属性或内部状态里记录分数。游戏必须离线运行，所有脚本、
样式和素材随构建产物提供，不使用外部 CDN、在线 API 或联机服务。
<!-- MOPAN_PROMPT_END -->

验证器通过浏览器鼠标操作检查初始分数、空闲期间不变、每次点击恰好加一以及
后续空闲期间不变，保存截图和动作证据。视觉风格不计分。不得修改验证器或为
测试实现另一套计数逻辑。这里评测 DOM 交互契约，不代表任意游戏的可玩质量。

完成后写入 `/workspace/gamebench/submission.json`：

```json
{
  "schema_version": "0.1",
  "kind": "local_directory",
  "entrypoint": "/workspace/game/dist/index.html"
}
```

本版本只接受本地构建产物；仅提交远程 URL 不满足本任务的离线交付要求。
若生成完成但没有产出游戏，可以提交合法的 `kind: "build_failure"`，计零分。
