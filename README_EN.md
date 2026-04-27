<h1 align="center">Xi'an Carbohydrates Guide Skill</h1>

<p align="center">
  <a href="https://github.com/muchen-ai/xian-carbohydrates-guide-skill">
    <img alt="GitHub Repository" src="https://img.shields.io/badge/GitHub-muchen--ai%2Fxian--carbohydrates--guide--skill-181717?logo=github">
  </a>
  <img alt="Type: AI Skill" src="https://img.shields.io/badge/Type-AI%20Skill-22c55e">
  <img alt="Language: Chinese" src="https://img.shields.io/badge/Language-简体中文-e11d48">
  <img alt="Language: English" src="https://img.shields.io/badge/Language-English-2563eb">
</p>

<p align="center">
  <a href="./README.md">简体中文</a> |
  <strong>English</strong>
</p>

> A locally curated AI food guide skill for Xi'an, built to help people skip tourist-trap lists and find more grounded, genuinely good carbohydrate-heavy food.

## About the Author

I'm Muchen. I live in Xi'an, and I'm also an AI enthusiast and developer.

Many friends visiting Xi'an run into the same problem: they want authentic local carbs, but they do not know which places locals actually go to, or how certain dishes are meant to be eaten. This skill is my attempt to make that easier.

## Why I Built This Skill

I wanted this project to be more than a restaurant list. It should feel more like a local friend guiding you through Xi'an food:

- where to eat
- what to order
- how to eat it properly
- and the stories, craft, and etiquette behind the dishes

## Highlights

- Local perspective: curated from everyday local experience, recommendations, and filtering
- Bilingual support: works for both Chinese and English queries
- Searchable store data: search by area, landmark, dish, delivery, Wi-Fi, and more
- Food knowledge Q&A: not just where to eat, but also origin stories, craft, differences, and eating tips
- Community add-ons: users can locally submit favorite spots and attach their own comments
- Ongoing refinement: the dataset will continue to be expanded and corrected

## What This Skill Does

After installation, your AI assistant can help you find famous carb-heavy restaurants in Xi'an and answer food knowledge questions such as:

- what to eat near Bell Tower, Xiaozhai, or Muslim Quarter
- where a store is and when it opens
- what its signature dishes are
- whether delivery is available
- whether Wi-Fi is available
- the origin, craft, differences, and eating tips for foods like biangbiang noodles, roujiamo, paomo, and youpo noodles
- and it can also record user-submitted recommendations and comments locally

### GitHub Repository

- [https://github.com/muchen-ai/xian-carbohydrates-guide-skill](https://github.com/muchen-ai/xian-carbohydrates-guide-skill)

### Installation

#### OpenClaw

Send this GitHub URL to OpenClaw and ask it to install the skill for you:

```text
Please install this skill:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

You can also say:

```text
Install this GitHub skill:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

#### Hermes

Send this GitHub URL to Hermes and ask it to install the skill for you:

```text
Please install this skill:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

You can also say:

```text
Install this GitHub skill:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

#### Claude Code

Send this GitHub URL to Claude Code and ask it to install the skill for you:

```text
Please install this skill:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

You can also say:

```text
Install this skill from GitHub:
https://github.com/muchen-ai/xian-carbohydrates-guide-skill
```

### How To Trigger

The simplest way is to ask in natural language.

Examples:

- `What are some good noodle spots near Bell Tower?`
- `Is there a good roujiamo place near Xiaozhai with delivery?`
- `Any paomo places near Muslim Quarter with Wi-Fi?`
- `What is the origin of biangbiang noodles?`

If your platform exposes the skill as a slash command, such as OpenClaw or Hermes, you can also trigger it like this:

```text
/xian-carbohydrates-guide-skill What should I eat near Bell Tower?
```

### Recommended Prompts

#### Restaurant Search

- `What are the best carb-heavy spots near Bell Tower?`
- `What noodles should I try near Xiaozhai?`
- `Where can I get good paomo near Muslim Quarter?`
- `Is there a good roujiamo place nearby with delivery?`
- `Where can I get good zenggao near Bell Tower?`

#### Store Details

- `When does this store open?`
- `Where is this place?`
- `What should I order there?`
- `Does this place offer delivery?`
- `Does this place have Wi-Fi?`

#### Food Knowledge

- `Where do biangbiang noodles come from?`
- `How is roujiamo made?`
- `What is the difference between youpo noodles and saozi noodles?`
- `Any etiquette or tips for eating paomo?`

#### Community Input

- `I want to recommend a noodle place I really like`
- `Help me add a good youpo noodle shop near Sajinqiao`
- `I want to leave a comment on this store`
- `What do people think about this place?`

In normal use, people do not need to type command arguments for this. They can just describe it naturally, and the assistant should ask only one short follow-up when key details are missing, then save it into the local community data.

### How To Recommend a Store or Leave a Comment

#### Recommending a Store

You can simply say:

- `I want to recommend a noodle place`
- `I want to add a paomo shop I really like`

If key details are missing, the assistant should usually ask only one short follow-up. The minimum details are normally:

- the store name
- the area, district, or address
- why you recommend it

Example:

- You: `I want to recommend a youpo noodle place`
- AI: `Sure — I can save it. I still need three things: the store name, the area or district, and why you recommend it.`
- You: `It's called Lao Li Jia, near Sajinqiao, and I think the chili aroma is especially good`

#### Leaving a Comment

You can also say:

- `I want to leave a comment on this store`
- `I want to add my opinion about this place`
- `I think this place is better in the morning`

If the conversation is already about a specific store, the assistant should treat that store as the default target. If the target is unclear, it should ask one short follow-up to identify the store.

Ratings and tags are optional. Example:

- You: `I want to leave a comment on this store`
- AI: `Sure — what would you like to say about it? If you want, you can also add a 1 to 5 rating.`
- You: `I think it is better in the morning. Give it a 4`

#### Current Storage Scope

- Store suggestions and comments are saved in the current local installed copy by default
- They are not automatically shared with every user
- If you want a shared community later, the project needs a remote backend

### What This Skill Supports

- find Xi'an carbohydrate-focused restaurants
- search by area, landmark, or dish
- check address and opening hours
- check signature dishes
- check delivery availability
- check Wi-Fi availability
- answer selected Xi'an food knowledge questions
- save local user-submitted store recommendations
- save local user comments and opinions
- browse local community feedback
- reply in Chinese for Chinese queries
- reply in English for English queries

### Notes

- This is a static-data skill, not a real-time service
- It does not support live queue handling
- If something is not recorded, the assistant should not invent it
- For nearby questions, it is best to include an area, landmark, street, or location
- Community submissions and comments are local to the installed copy by default and are not automatically shared with all users
- Recommendation and comment flows should normally happen through natural language rather than direct low-level commands

### License

This project is released under the MIT License.
