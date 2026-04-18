# Prompt Review Round-Trip System

`prompt_review/` 是当前项目的 prompt 审阅、编辑、revision、round-trip 比对与源码回填准备目录。它不是静态导出页，而是以下三层同时存在的系统：

- 展示层：`index.html` + `app.js` + `styles.css`
- 用户真相层：`review.edited.json` + `revisions/*.json` + `patch.log.json`
- 溯源层：`review.map.json` + `coverage.report.json` + `ambiguities.json` + `roundtrip.report.json`

## 目录与职责

- `index.html`
  - 审阅入口页
  - 顶部列出全量 `生产链路 - 环节 - 角色`
  - 每个 group 一张独立编辑卡片
- `review.baseline.json`
  - 初始编译快照
  - 只读，不因后续编辑被覆盖
- `review.edited.json`
  - 当前用户编辑真相
  - 页面实时保存直接写回这里
- `review.regenerated.json`
  - 从项目源码重新编译后的对照版本
  - 仅用于 round-trip diff，不回写到 edited
- `review.map.json`
  - group/block/source 的双向映射表
- `patch.log.json`
  - 每次保存后的结构化 patch 日志
- `revisions/revisions.index.json`
  - revision 清单
- `revisions/rev-*.json`
  - 不可变完整快照
- `conflicts/active.json`
  - 冲突冻结态
- `coverage.report.json`
  - 覆盖率与未覆盖项/低置信度/镜像关系
- `ambiguities.json`
  - 无法安全自动回填的歧义记录
- `roundtrip.report.json`
  - 回填后 regenerated 与 edited 的对比结果

## 页面如何工作

页面按 `group_id` 渲染，不按文本去重。即使两个角色拿到完全相同的 prompt，也会是两张卡片，因为：

- group 是用户可见编辑单元
- block/span 是机器内部回填单元
- 相同文本但不同 receiver，必须保留不同 group_id 才能 round-trip

顶部索引和卡片都来自 `review.edited.json`。页面支持：

- 搜索任意 prompt 句子
- 按 `production_chain / stage / role` 过滤
- contenteditable 富文本编辑
- 自动保存
- revision 恢复
- frozen conflict 显示

## 不可见结构如何保留映射

页面中有两类肉眼不可见但可追溯的结构：

1. `data-*` 属性

- 卡片级：`data-group-id` `data-production-chain` `data-stage` `data-role`
- block 级：`data-block-id` `data-write-policy` `data-merge-rule`

这些属性跟着 DOM 走，用户改文字时不会丢。

2. 隐藏 JSON

页面会把 group/block/source 摘要写进：

```html
<script type="application/json" class="hidden-json group-meta-json">...</script>
```

这里保存的是该卡片的 block/source 信息，供后续：

- 保存时生成 patch
- 判断 block 是否 split/merge/reorder
- 回填时查主来源、镜像来源、placeholder
- 冲突或歧义分析

## review.map.json 的关键字段

每个 group 至少保留：

- `group_id`
- `group_label`
- `production_chain`
- `stage`
- `role`
- `display_order`
- `display_text`
- `editable_rich_text`
- `blocks[]`
- `target_refs[]`

每个 block 至少保留：

- `block_id`
- `text`
- `normalized_text`
- `source_refs[]`
- `primary_source`
- `placeholder_refs[]`
- `merge_rule`
- `write_policy`
- `propagation_rule`
- `confidence`
- `duplicate_fingerprint`
- `notes`

此外 `review.map.json` 还保留：

- `blocks[]` 扁平 registry
- `source_catalog`
- `source_registry`
- `duplicate_clusters`
- `mirrors`

## 如何从映射层回填源码

回填时不直接拿整段全文替换，而是优先按 `source_refs` 定点：

1. 先按 group 找 block
2. 再按 block 的 `primary_source` 定位源码
3. 若 `write_policy=primary_only`
   - 只改主来源
   - 其他 receiver 依靠重新编译继承
4. 若 `write_policy=fanout_to_mirrors`
   - 同步改所有确定镜像
5. 若 `write_policy=ambiguous`
   - 不自动写回
   - 进入 `ambiguities.json`

placeholder 不会在映射层消失：

- 原变量文本保存在 `placeholder_refs[].placeholder_text`
- 同时记录语义槽位 `semantic_slot`
- 写回策略记录在 `write_strategy`

因此展示层可以把变量弱化，但源码层和映射层不会丢失原 placeholder。

## 防回滚规则

- `review.edited.json` 是唯一用户编辑真相
- `review.baseline.json` 一经生成只读
- `review.regenerated.json` 只用于 diff，不覆盖 edited
- 每次保存都会写 revision snapshot
- block 对齐失败、来源冲突、round-trip 差异过大时：
  - 进入 `conflicts/active.json`
  - 冻结自动流程
  - 保留 edited，不自动覆盖

## 运行方式

启动现有 job webapp：

```bash
python3 -m runtime.job_webapp.main --host 127.0.0.1 --port 8765 --no-open-browser
```

然后访问：

- `http://127.0.0.1:8765/prompt_review`

关键 API：

- `GET /api/prompt-review`
- `POST /api/prompt-review/save`
- `GET /api/prompt-review/revisions`
- `POST /api/prompt-review/restore`
- `POST /api/prompt-review/regenerate`
- `POST /api/prompt-review/roundtrip`
- `GET /api/prompt-review/conflicts`
- `GET /api/prompt-review/coverage`
- `GET /api/prompt-review/ambiguities`

## 当前覆盖策略

当前页面包含两类 group：

- 实际生产 receiver group
  - 如 `runtime_main / generate / writer`
  - 如 `match_pipe / shared_writer / writer`
- source reference group
  - 用于纳入不直接走主 orchestrator、但确实承载 prompt 的来源
  - 如 inactive builder、indirect runtime、doc、design guide、test fixture

这样做的原因是：用户要求“项目里的任何 prompt 句子都能在页面上找到”，而有些 prompt-bearing 文本并不对应活跃 runtime receiver。对这类来源，系统仍给出独立卡片，但会把 `write_policy` 设为 `ambiguous`，避免误回填。
