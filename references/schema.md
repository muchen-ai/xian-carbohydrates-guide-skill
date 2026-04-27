# 数据 Schema

这份文档只描述仓库运行时使用的 JSON 数据结构。

当前 skill 只依赖下面 3 个本地数据文件：

- `data/stores.json`
- `data/knowledge.json`
- `data/taxonomy.json`

## 总原则

- 一家门店一条记录，不按品牌合并
- 连锁品牌不同分店分开记录
- 能确认的再写，不能确认就留空或写 `unknown`
- 营业时间、Wi-Fi、外卖等易变信息尽量填写 `last_verified_at`
- 双语场景下，中文和英文字段分开维护

## taxonomy.json

`data/taxonomy.json` 是固定分类词典，供门店和知识库复用。

当前固定 7 类：

- `noodles`：面类
- `mo`：馍类
- `cold_skin_and_jelly`：凉皮凉粉类
- `bing`：饼类
- `dumplings_and_wontons`：饺子馄饨类
- `sweet_snacks`：特色甜品类
- `specialty_staples`：特色主食类

每个分类对象结构如下：

```json
{
  "category_id": "noodles",
  "name_zh": "面类",
  "name_en": "Noodles",
  "query_keywords_zh": ["面", "面条", "面食"],
  "query_keywords_en": ["noodles", "noodle"],
  "dishes_zh": ["油泼面", "biangbiang面"],
  "dishes_en": ["youpo noodles", "biangbiang noodles"]
}
```

## stores.json

`data/stores.json` 使用 JSON 数组，每个元素代表一家具体门店。

### 主要字段

| JSON 字段 | 必填 | 说明 |
|---|---|---|
| `store_id` | 是 | 稳定唯一 ID |
| `brand_name` | 是 | 品牌名 |
| `brand_name_en` | 否 | 品牌英文名 |
| `branch_name` | 是 | 分店名 |
| `branch_name_en` | 否 | 分店英文名 |
| `aliases` | 否 | 中文别名数组 |
| `aliases_en` | 否 | 英文别名数组 |
| `district` | 是 | 行政区 |
| `district_en` | 否 | 行政区英文 |
| `area` | 是 | 商圈或片区 |
| `area_en` | 否 | 商圈英文 |
| `landmarks` | 否 | 附近地标数组 |
| `landmarks_en` | 否 | 附近地标英文数组 |
| `address` | 是 | 详细地址 |
| `address_en` | 否 | 英文地址 |
| `lat` | 建议 | 纬度 |
| `lng` | 建议 | 经度 |
| `primary_category_id` | 是 | 主分类，取值来自 taxonomy |
| `secondary_category_ids` | 否 | 次分类数组 |
| `dish_types` | 是 | 中文菜式数组 |
| `dish_types_en` | 否 | 英文菜式数组 |
| `search_keywords_zh` | 否 | 中文检索词数组 |
| `search_keywords_en` | 否 | 英文检索词数组 |
| `food_tags` | 是 | 中文标签数组 |
| `food_tags_en` | 否 | 英文标签数组 |
| `signature_dishes` | 否 | 中文招牌数组 |
| `signature_dishes_en` | 否 | 英文招牌数组 |
| `recommended_reason` | 否 | 中文推荐理由 |
| `recommended_reason_en` | 否 | 英文推荐理由 |
| `hours` | 否 | 每周营业时间对象 |
| `queue_notes` | 否 | 中文排队说明 |
| `queue_notes_en` | 否 | 英文排队说明 |
| `takeout_supported` | 否 | `yes/no/unknown` |
| `delivery_supported` | 否 | `yes/no/unknown` |
| `delivery_platforms` | 否 | 外卖平台数组 |
| `wifi_policy` | 否 | `public/ask_staff/none/unknown` |
| `wifi_name` | 否 | Wi-Fi 名称 |
| `wifi_password` | 否 | Wi-Fi 密码 |
| `notes` | 否 | 中文补充说明 |
| `notes_en` | 否 | 英文补充说明 |
| `last_verified_at` | 建议 | 最近核验日期 |
| `source_url` | 否 | 来源链接 |
| `confidence` | 否 | `high/medium/low/unknown` |
| `priority_score` | 否 | 整数，越高越优先 |

### 营业时间格式

`hours` 是对象，包含：

- `mon`
- `tue`
- `wed`
- `thu`
- `fri`
- `sat`
- `sun`

每个值支持以下格式：

- `09:00-21:00`
- `09:00-14:00;17:00-21:00`
- `closed`
- `unknown`

### 示例

```json
{
  "store_id": "example_store",
  "brand_name": "示例馆子",
  "brand_name_en": "Example Shop",
  "branch_name": "示例店",
  "branch_name_en": "Example Branch",
  "aliases": ["示例别名"],
  "aliases_en": ["Example Alias"],
  "district": "碑林区",
  "district_en": "Beilin District",
  "area": "钟楼",
  "area_en": "Bell Tower",
  "landmarks": ["钟楼"],
  "landmarks_en": ["Bell Tower"],
  "address": "示例地址",
  "address_en": "Example address",
  "lat": 34.2591,
  "lng": 108.9485,
  "primary_category_id": "mo",
  "secondary_category_ids": ["specialty_staples"],
  "dish_types": ["肉夹馍", "腊牛肉夹馍"],
  "dish_types_en": ["roujiamo", "cured beef roujiamo"],
  "search_keywords_zh": ["夹馍", "腊汁", "回民街肉夹馍"],
  "search_keywords_en": ["roujiamo", "meat sandwich"],
  "food_tags": ["肉夹馍", "清真"],
  "food_tags_en": ["roujiamo", "halal"],
  "signature_dishes": ["腊牛肉夹馍"],
  "signature_dishes_en": ["cured beef roujiamo"],
  "recommended_reason": "一句说明为什么值得推荐",
  "recommended_reason_en": "One short reason for recommendation",
  "hours": {
    "mon": "08:00-21:00",
    "tue": "08:00-21:00",
    "wed": "08:00-21:00",
    "thu": "08:00-21:00",
    "fri": "08:00-21:30",
    "sat": "08:00-21:30",
    "sun": "08:00-21:00"
  },
  "queue_notes": "饭点常排队",
  "queue_notes_en": "Busy at meal times",
  "takeout_supported": "yes",
  "delivery_supported": "yes",
  "delivery_platforms": ["美团", "饿了么"],
  "wifi_policy": "ask_staff",
  "wifi_name": "ExampleWifi",
  "wifi_password": "12345678",
  "notes": "高峰期可能拼桌",
  "notes_en": "Shared seating may happen at peak hours",
  "last_verified_at": "2026-04-26",
  "source_url": "https://example.com",
  "confidence": "high",
  "priority_score": 10
}
```

## knowledge.json

`data/knowledge.json` 使用 JSON 数组，每个元素代表一条知识问答。

### 主要字段

| JSON 字段 | 必填 | 说明 |
|---|---|---|
| `entry_id` | 是 | 稳定唯一 ID |
| `topic_slug` | 是 | 主题标识 |
| `intent_type` | 是 | `history/craft/taste/etiquette` |
| `category_id` | 是 | 所属大类，取值来自 taxonomy |
| `dish_types` | 是 | 中文关联菜式数组 |
| `dish_types_en` | 否 | 英文关联菜式数组 |
| `question_zh` | 是 | 中文问题 |
| `question_en` | 否 | 英文问题 |
| `answer_zh` | 是 | 中文答案 |
| `answer_en` | 否 | 英文答案 |
| `keywords_zh` | 否 | 中文检索词数组 |
| `keywords_en` | 否 | 英文检索词数组 |
| `notes` | 否 | 维护备注 |
| `last_verified_at` | 建议 | 最近核验日期 |
| `source_url` | 否 | 来源链接 |
| `confidence` | 否 | `high/medium/low/unknown` |
| `priority_score` | 否 | 整数，越高越优先 |

### intent_type 说明

- `history`：历史文化、由来、典故
- `craft`：制作工艺、做法、结构
- `taste`：口味特点、区别、风味比较
- `etiquette`：食用建议、讲究、吃法

### 示例

```json
{
  "entry_id": "biangbiang_origin",
  "topic_slug": "biangbiang_mian",
  "intent_type": "history",
  "category_id": "noodles",
  "dish_types": ["biangbiang面"],
  "dish_types_en": ["biangbiang noodles"],
  "question_zh": "biangbiang面的由来是什么？",
  "question_en": "Where do biangbiang noodles come from?",
  "answer_zh": "这里填写中文标准回答。",
  "answer_en": "Put the English answer here.",
  "keywords_zh": ["由来", "历史", "biangbiang"],
  "keywords_en": ["origin", "history", "biangbiang"],
  "notes": "注意区分传说和可确认史料",
  "last_verified_at": "2026-04-26",
  "source_url": "https://example.com",
  "confidence": "medium",
  "priority_score": 10
}
```
