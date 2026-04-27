<h1 align="center">西安碳水美食指南 Skill</h1>

<p align="center">
  <a href="https://github.com/muchen-ai/xian-carbohydrates-guide-skill">
    <img alt="GitHub Repository" src="https://img.shields.io/badge/GitHub-muchen--ai%2Fxian--carbohydrates--guide--skill-181717?logo=github">
  </a>
  <img alt="Type: AI Skill" src="https://img.shields.io/badge/Type-AI%20Skill-22c55e">
  <img alt="Language: Chinese" src="https://img.shields.io/badge/Language-简体中文-e11d48">
  <img alt="Language: English" src="https://img.shields.io/badge/Language-English-2563eb">
</p>

<p align="center">
  <strong>简体中文</strong> |
  <a href="./README_EN.md">English</a>
</p>

> 一个由西安本地人整理的 AI 美食指南 Skill，尽量帮你避开游客向热门榜单，吃到更地道的西安碳水。

## 关于作者

我是沐晨，我在西安，同时也是一名 AI 爱好者和开发者。

很多来西安玩的朋友都会遇到同一个问题：想吃正宗碳水，但不知道去哪找本地人常去的店，也不知道每种东西到底该怎么吃才对味。这个 skill 就是为了解决这个问题而做的。

## 为什么做这个 Skill

我希望它不只是一个“餐厅列表”，而是一个更像本地朋友带路的美食助手：

- 告诉你去哪吃
- 告诉你吃什么
- 告诉你怎么吃更地道
- 也告诉你一些背后的历史、做法和讲究

## 项目特色

- 本地视角：以我和身边西安朋友的日常经验、口碑和筛选为基础整理
- 中英双语：支持中文和英文提问，方便本地用户和游客使用
- 门店信息可检索：支持按商圈、地标、菜品、外卖、Wi-Fi 等条件查找
- 知识问答：不仅能查店，还能回答由来、做法、区别和吃法
- 社区补充：用户可以本地提交自己看好的店，也可以补充评论和个人看法
- 持续补充：数据会继续补充和修正

## 这个 Skill 能做什么

安装后，AI 助手可以帮你查询西安知名碳水馆子，以及回答一些和西安碳水相关的饮食知识问题，比如：

- 钟楼、小寨、回民街附近有什么值得吃的
- 某家店在哪里、几点开门
- 招牌吃什么
- 能不能外卖
- 有没有 Wi-Fi
- `biangbiang` 面、肉夹馍、泡馍、油泼面这些食物的由来、做法、区别和吃法
- 也可以提交自己推荐的店铺，或给已有店铺补充评价

### GitHub 地址

- [https://github.com/muchen-ai/xian-carbohydrates-guide-skill](https://github.com/muchen-ai/xian-carbohydrates-guide-skill)

### 怎么安装

#### OpenClaw

直接把这个 GitHub 地址发给 OpenClaw，让它帮你安装这个 skill：

```text
请帮我安装这个 skill：
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

也可以直接说：

```text
安装这个 GitHub skill：
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

#### Hermes

直接把这个 GitHub 地址发给 Hermes，让它帮你安装这个 skill：

```text
请帮我安装这个 skill：
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

也可以直接说：

```text
安装这个 GitHub skill：
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

#### Claude Code

直接把这个 GitHub 地址发给 Claude Code，让它帮你安装这个 skill：

```text
请帮我安装这个 skill：
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

也可以直接说：

```text
Install this skill from GitHub:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

### 怎么触发

最简单的方式就是直接自然语言提问。

例如：

- `钟楼附近有什么值得吃的面？`
- `小寨附近有没有支持外卖的肉夹馍？`
- `回民街附近有 Wi-Fi 的馆子吗？`
- `吃泡馍有什么讲究？`

如果你的平台会把 skill 暴露成 slash command，比如 OpenClaw 或 Hermes，也可以直接这样触发：

```text
/xian-carbohydrates-guide-skill 钟楼附近有什么碳水推荐？
```

### 推荐怎么问

#### 餐厅查询

- `钟楼附近有什么碳水推荐？`
- `小寨附近有什么面？`
- `回民街附近有什么泡馍？`
- `附近有什么支持外卖的肉夹馍？`
- `钟楼附近有什么值得吃的甑糕？`

#### 门店详情

- `樊记肉夹馍钟楼店几点开门？`
- `这家店在哪里？`
- `这家店招牌吃什么？`
- `这家店能不能外卖？`
- `这家店有没有 Wi-Fi？`

#### 美食知识

- `biangbiang 面的由来是什么？`
- `肉夹馍是怎么做的？`
- `油泼面和臊子面有什么区别？`
- `吃泡馍有什么讲究？`

#### 社区补充

- `我想推荐一家自己很喜欢的面馆`
- `帮我加一家洒金桥附近的油泼面店`
- `我想给这家店补充一句评论`
- `大家对这家店有什么看法？`

这类场景下，正常使用时不需要你手写任何命令参数。你直接用自然语言说，AI 会只在必要时补问 1 轮左右，把信息整理好后再自动写入本地社区数据。

### 如何推荐店铺和评论店铺

#### 推荐店铺

你只需要直接说：

- `我想推荐一家面馆`
- `我想补充一家我很喜欢的泡馍店`

如果信息不够，AI 一般只会补问 1 轮，通常会问这些最少必要信息：

- 店名叫什么
- 大概在哪个区、商圈或地址
- 你为什么推荐它

例如：

- 你：`我想推荐一家油泼面店`
- AI：`可以，我帮你记下来。还差 3 个信息：店名叫什么、在哪个区或商圈、你为什么推荐它？`
- 你：`叫老李家，在洒金桥，我觉得辣子香味特别稳`

#### 评论店铺

你也可以直接说：

- `我想给这家店补一句评论`
- `我想说一下我对这家店的看法`
- `这家我觉得更适合早上去`

如果当前上下文里已经在聊某家店，AI 会默认评论这家店；如果目标不明确，AI 只会再问一句你说的是哪家。

评分和标签都是可选的，不填也可以。例如：

- 你：`我想给这家店补一句评论`
- AI：`可以，你想补充一句什么评价？如果你愿意，也可以顺手给个 1 到 5 分。`
- 你：`我觉得更适合早上去，给 4 分`

#### 当前保存范围

- 推荐店铺和评论店铺默认保存到当前本地安装副本
- 不会自动同步给所有用户
- 如果后面要做成所有用户共享，需要再接远端服务

### 支持什么

- 查询西安碳水馆子
- 按商圈、地标、菜品来找店
- 查询地址和营业时间
- 查询招牌菜
- 查询是否支持外卖
- 查询是否有 Wi-Fi
- 回答部分西安碳水饮食知识问题
- 本地提交推荐店铺
- 本地补充店铺评论和个人看法
- 查看本地社区反馈
- 中文提问返回中文
- 英文提问返回英文

### 注意事项

- 这是静态资料型 skill，不是实时平台
- 当前不支持真实代排队，只能回答资料里是否记录了排队说明
- 没有记录到的信息不会编造
- 如果你问“附近”，最好带上商圈、地标、街道或位置
- 当前用户提交和评论默认只保存在本地安装副本，不会自动同步给所有人
- 推荐店铺和评论店铺这类功能，正常应通过自然语言完成，不需要用户直接操作底层命令

### 许可证

本项目采用 MIT 许可证。
