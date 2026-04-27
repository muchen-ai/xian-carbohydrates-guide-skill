---
name: xian-carbohydrates-guide-skill
description: 西安碳水美食本地知识库。适用于查询西安肉夹馍、泡馍、biangbiang面、油泼面、甑糕、葫芦头等知名馆子，也适用于回答这些食物的历史文化、口味区别、制作工艺和食用建议。支持按商圈、地标、菜品、是否营业、是否支持外卖、是否有 Wi-Fi 来检索门店，并查看门店详情。回答前优先调用本地查询脚本，不要编造仓库里没有的数据；按用户输入语言回复中文或英文。
version: 0.1.0
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

## 数据文件

- 门店数据：`<skill_dir>/data/stores.json`
- 知识数据：`<skill_dir>/data/knowledge.json`
- 分类词典：`<skill_dir>/data/taxonomy.json`
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

如果字段缺失，可以这样回答：

> 这家店的位置和营业时间我能确认，但这份资料里暂时没有记到 Wi-Fi 信息；如果你要，我可以先给你看附近几家更适合坐着吃、资料也更完整的店。
