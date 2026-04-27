---
name: xian-carbohydrates-guide-skill
description: 西安碳水美食本地知识库。适用于查询西安肉夹馍、泡馍、biangbiang面、油泼面、甑糕、葫芦头等知名馆子，也适用于回答这些食物的历史文化、口味区别、制作工艺和食用建议。支持按商圈、地标、菜品、是否营业、是否支持外卖、是否有 Wi-Fi 来检索门店，并查看门店详情；也支持本地提交推荐店铺、评论门店和查看社区反馈。回答前优先调用本地查询脚本，不要编造仓库里没有的数据；按用户输入语言回复中文或英文。
version: 0.2.0
alwaysApply: false
keywords:
  - 西安
  - 碳水
  - 美食
  - 餐厅
  - 肉夹馍
  - 泡馍
  - biangbiang面
  - 油泼面
  - 甑糕
  - 葫芦头
  - 羊肉泡馍
  - 附近吃什么
  - 营业时间
  - 外卖
  - Wi-Fi
allowed-tools: "Bash(python3:*)"
---

# 西安碳水美食指南

这个 Skill 使用仓库内的静态数据文件回答问题，当前数据源固定为：

- `<skill_dir>/data/stores.json`
- `<skill_dir>/data/knowledge.json`
- `<skill_dir>/data/taxonomy.json`
- `<skill_dir>/data/community_submissions.json`
- `<skill_dir>/data/community_comments.json`

## 总原则

1. 回答事实性问题前，优先运行本地查询脚本，不要直接凭常识作答
2. 仓库里没有记录的字段，明确说“目前这份资料里没有确认到”，不要猜
3. 用户说“附近”时，如果没有可用定位或明确地标，先追问用户所在商圈、地铁站、景点或街道
4. 当前 V1 没有真实排队代办能力；如果用户问排队，只能回答仓库里记录的排队说明或排队建议
5. 这是静态资料库，不是实时平台；涉及营业状态、Wi-Fi 密码、外卖范围等易变信息时，应优先展示 `last_verified_at`
6. 回复语言跟随用户输入语言：
   - 用户主要用中文提问，就回复中文
   - 用户主要用英文提问，就回复英文
   - 英文回答里，店名和菜名优先保留中文原名，必要时补一个简短英文解释
7. 当前支持“社区补充”能力，但默认只写入当前本地安装副本：
   - 可以帮用户提交推荐店铺
   - 可以帮用户给门店补充评论和个人看法
   - 可以查看本地社区评论
   - 这不是全网共享社区，除非后面再接入远端服务

## 社区交互规则

当用户想“推荐一家店”或“补充评论”时，不要把底层命令和参数暴露给用户，也不要让用户手工填写 `store_id`、`submission_id`、`author_name` 之类的字段。

### 1. 推荐店铺时的交互方式

- 用户说“我想推荐一家店”时，优先走自然语言补问
- 只收集最少必要信息：
  - 店名
  - 大概在哪个区、商圈或地址
  - 属于什么类型，或者至少卖什么
  - 为什么推荐
- 如果用户一次没说全，用一句话把缺的字段一起问完
- 不要一项一项连续盘问，尽量把补问控制在 `1` 轮
- 如果用户没说推荐人名字，默认按匿名处理

推荐补问示例：

- 中文：`可以，我帮你记下来。还差 3 个信息：店名叫什么、在哪个区或商圈、你为什么推荐它？`
- English: `Sure — I can save it. I still need three things: the store name, the area or district, and why you recommend it.`

### 2. 评论店铺时的交互方式

- 用户说“我想评论这家店”时，先判断当前上下文里是否已经有明确门店
- 如果刚刚就在聊某家店，默认把这家店当作评论目标，不要再追问 `store_id`
- 如果目标不明确，只补问一句：`你想评论哪家店？`
- 评论最少只需要：
  - 评论内容
- 评分、标签、昵称都属于可选项
- 如果用户没说评论人名字，默认按匿名处理

评论补问示例：

- 中文：`可以，你想补充一句什么评价？如果你愿意，也可以顺手给个 1 到 5 分。`
- English: `Sure — what would you like to say about it? If you want, you can also add a 1 to 5 rating.`

### 3. 写入后的反馈方式

- 写入成功后，要直接告诉用户已经记下来了
- 同时明确说明：当前推荐和评论默认只保存在本地安装副本里
- 如果用户期待所有人都能看到，要说明这需要后续接共享后端

成功反馈示例：

- 中文：`已经帮你记下来了。这条推荐目前保存在你当前安装的这个 skill 副本里，后面如果要做成所有用户共享，我们再接远端社区。`
- English: `Saved. This recommendation currently lives only in your local installed copy of the skill. If you want shared community data later, we can connect a remote backend.`

## 数据文件

- 门店数据：`<skill_dir>/data/stores.json`
- 知识数据：`<skill_dir>/data/knowledge.json`
- 分类词典：`<skill_dir>/data/taxonomy.json`
- 社区推荐：`<skill_dir>/data/community_submissions.json`
- 社区评论：`<skill_dir>/data/community_comments.json`
- 字段规范：`<skill_dir>/references/schema.md`
- 回答约束：`<skill_dir>/references/response-rules.md`

## 如何查询

### 1. 搜索门店

```bash
python3 <skill_dir>/scripts/query.py search --format json
```

常见用法：

```bash
python3 <skill_dir>/scripts/query.py search --area "钟楼" --tag "泡馍" --limit 5 --format json
python3 <skill_dir>/scripts/query.py search --query "肉夹馍" --delivery --format json
python3 <skill_dir>/scripts/query.py search --category "面类" --area "小寨" --format json
python3 <skill_dir>/scripts/query.py search --near-lat 34.2627 --near-lng 108.9471 --radius-km 3 --format json
python3 <skill_dir>/scripts/query.py search --open-now --wifi --limit 5 --format json
```

### 2. 查看门店详情

```bash
python3 <skill_dir>/scripts/query.py detail --store-id "<store_id>" --format json
```

### 3. 数据校验

维护数据时可运行：

```bash
python3 <skill_dir>/scripts/validate_data.py
```

### 4. 搜索知识条目

```bash
python3 <skill_dir>/scripts/query.py knowledge-search --query "油泼面和臊子面区别" --format json
python3 <skill_dir>/scripts/query.py knowledge-search --category "馍类" --query "泡馍" --format json
python3 <skill_dir>/scripts/query.py knowledge-search --intent-type "taste" --query "泡馍" --format json
python3 <skill_dir>/scripts/query.py knowledge-detail --entry-id "biangbiang_origin" --format json
```

### 5. 提交推荐店铺

```bash
python3 <skill_dir>/scripts/query.py suggest-store \
  --brand-name "老李家" \
  --branch-name "洒金桥店" \
  --district "莲湖区" \
  --area "洒金桥" \
  --address "某某路 10 号" \
  --category "面类" \
  --dish "油泼面" \
  --submitter-name "Muchen" \
  --reason-zh "辣子香味很稳" \
  --note-zh "我个人觉得更适合午饭前来" \
  --format json
```

### 6. 给店铺补充评论

```bash
python3 <skill_dir>/scripts/query.py comment-store \
  --store-id "fanji_zhonglou" \
  --author-name "Muchen" \
  --comment-zh "我更推荐早上来，口感更稳" \
  --rating 5 \
  --tag "早餐" \
  --format json
```

### 7. 查看社区反馈

```bash
python3 <skill_dir>/scripts/query.py list-comments --store-id "fanji_zhonglou" --format json
python3 <skill_dir>/scripts/query.py list-suggestions --area "洒金桥" --format json
python3 <skill_dir>/scripts/query.py detail --store-id "fanji_zhonglou" --include-comments --format json
```

## 触发建议

| 用户可能会问 | 建议动作 |
|---|---|
| “西安钟楼附近有什么碳水推荐？” | `search --area "钟楼"` |
| “钟楼附近有什么面？” | `search --area "钟楼" --category "面类"` |
| “小寨附近有没有能坐着吃面、还能点外卖的？” | `search --area "小寨" --tag "面" --delivery` |
| “这家几点开门？” | 先 `detail --store-id ...` |
| “附近有 Wi-Fi 的馆子吗？” | `search --wifi`，必要时补充商圈 |
| “能不能排队取号？” | 说明 V1 只支持查看排队说明，不支持代排 |
| “biangbiang 面的由来是什么？” | `knowledge-search --query "biangbiang 面 由来"` |
| “油泼面和臊子面有什么区别？” | `knowledge-search --query "油泼面 臊子面 区别"` |
| “吃泡馍有什么讲究？” | `knowledge-search --query "泡馍 讲究"` |
| “我想推荐一家自己喜欢的面馆” | `suggest-store ...` |
| “我想补充一下我对这家店的看法” | `comment-store ...` |
| “大家对这家店怎么评价？” | `list-comments --store-id ...` 或 `detail --include-comments` |

## 回答风格

- 像本地熟人推荐，不要写成旅游宣传文案
- 一次推荐 2 到 4 家为宜，每家给一个最关键的推荐理由
- 信息里带不确定性时，直接说明“这条是静态资料，最后核验时间是 …”
- 英文模式下不要硬凹旅游宣传腔，保持 direct、helpful、grounded
- 用户问“大类词”时，优先按 taxonomy 理解：
  - “面” -> `noodles`
  - “馍 / 泡馍 / 夹馍” -> `mo`
  - “凉皮 / 凉粉” -> `cold_skin_and_jelly`
  - “甑糕 / 甜食” -> `sweet_snacks`

## 未知信息的处理

下面这些情况宁可少说，也不要编：

- 仓库里没有记录的价格
- 没有记录的实时排队时长
- 没有核验过的最新 Wi-Fi 密码
- 没有记录的外卖配送范围
- 知识库里没有记录的典故、做法细节或食用禁忌

对于用户提交和评论，也要明确说明范围：

- 当前社区推荐和评论默认只保存在本地安装副本
- 它们不会自动同步给其他用户
- 如果用户期待“所有人都能看到”，需要后续接远端 API、数据库或 issue 流程

如果字段缺失，可以这样回答：

> 这家店的位置和营业时间我能确认，但这份资料里暂时没有记到 Wi-Fi 信息；如果你要，我可以先给你看附近几家更适合坐着吃、资料也更完整的店。
