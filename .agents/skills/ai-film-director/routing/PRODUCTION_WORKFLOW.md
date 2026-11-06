# 阶段与文件路由

状态文件为项目的 `00_admin/PROJECT_STATE.md`。每步记录输入版本、产物路径、验收人/依据、未完成事项；不能用“已写方案”代替媒体产物完成。题材差异见 `../workflows/WORKFLOW_OVERVIEW.md`。

| 阶段 | 输入 | 输出与岗位 | 验收和下一阶段条件 |
| --- | --- | --- | --- |
| 1 需求分析 | 用户目标与限制 | CREATIVE_BRIEF；production | 目标、时长、受众、约束可核，进入研究 |
| 2 资料研究 | 简报、原始来源 | RESEARCH_LOG；research | 引用与缺口标明，进入创意 |
| 3 故事创意 | 事实边界、主题 | 2—3 个方向；screenwriting/directing | 故事方向人工确认，进入人物世界观 |
| 4 人物和世界观 | 已选方向 | STORY_BIBLE；screenwriting/art-direction | 人物动机、规则和时代一致，进入大纲 |
| 5 故事大纲 | 故事圣经 | 场景节拍；screenwriting | 因果、转折和时长成立，进入剧本 |
| 6 完整剧本 | 大纲 | SCREENPLAY；screenwriting | 场景、动作、对白完整，进入压力测试 |
| 7 剧本压力测试 | 剧本 | 问题与修订记录；screenwriting/directing | 致命问题清零，剧本定稿人工确认 |
| 8 视觉圣经 | 已锁剧本 | VISUAL_BIBLE；directing/cinematography/art-direction | 画幅、色彩、角色和时代视觉一致，视觉方向人工确认 |
| 9 人物和场景设定 | 已确认视觉 | 角色、场景、道具约束；art-direction/continuity | 可复用编号与版本齐全，进入分镜 |
| 10 分镜 | 剧本与视觉圣经 | STORYBOARD_PLAN；storyboard/directing | 空间、动作、视线可读，进入镜头清单 |
| 11 镜头清单 | 分镜与约束 | SHOTLIST.csv；cinematography/production | 时长和批次可执行，编号稳定 |
| 12 关键帧与图像素材 | 已批准批次 | ASSET_MANIFEST.csv；art-direction/production | 真实文件存在才标 generated，来源和连续性登记 |
| 13 视频生成提示词 | 镜头与可用素材 | 每镜提示词；directing/cinematography | 与锁定设定一致，可交外部引擎 |
| 14 配音和音效设计 | 剧本与镜头 | AUDIO_CUES.csv；sound-design | 台词、音效和音乐权利/优先级明确 |
| 15 剪辑方案 | 可用视频与音频 | EDIT_PLAN；editing | 节奏、转场和缺片处理可执行 |
| 16 成片验收 | 真实成片及来源记录 | QA_REPORT、DELIVERY_MANIFEST；quality/production | 致命/重要问题清零，最终成片人工确认 |

素材不存在时后续步骤仅能作为计划，不能标记已生成或已验收。
