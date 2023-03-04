from dependency.EdgeGPT.src.EdgeGPT import Chatbot, ConversationStyle
from typing import List
import asyncio
import re
from logging import debug, info, warning, error, critical


class Config:
    start_prompt = {
        "head": "将以下整个文段使用ChatGPT翻译成简体中文并**润色**，不要使用其它软件，不要修改其中的公式、术语、引用链接和代码，语句应通顺且符合简体中文习惯。",
        "exclude_head": "**不要**翻译这些词语：",
        "exclude": [],
        "tail": "输出为markdown格式。只回答翻译结果，**不要**回复其它内容。\n\n"
    }
    conti_prompt = "继续翻译：\n"
    lett_limit = 2000
    conv_limit = 8

    def start_prompt_str(self):
        if len(self.start_prompt["exclude"]) == 0:
            return self.start_prompt["head"] + self.start_prompt["tail"]
        else:
            return self.start_prompt["head"] + \
                self.start_prompt["exclude_head"] + ",".join(self.start_prompt["exclude"]) + "。"\
                + self.start_prompt["tail"]


class Translator:
    def __init__(self, cookies: dict, exclude: list) -> None:
        self.bot = Chatbot(cookies=cookies)
        self.config = Config()
        self.config.start_prompt["exclude"] = exclude

    async def reset(self):
        await self.bot.reset()

    async def close(self):
        await self.bot.close()

    def slice(self, text: str) -> List[List[str]]:
        text = text + "\n\n"
        pattern = r'.{0,' f"{self.config.lett_limit - len(self.config.start_prompt_str())}" r'}\n\n'
        l = re.findall(pattern, text, re.DOTALL)
        len_l = len(l)
        return [[self.config.start_prompt_str() + l[i]]
                + [self.config.conti_prompt + l[j]
                    for j in range(i+1, min(i+self.config.conv_limit, len_l))]
                for i in range(0, len_l, self.config.conv_limit)]

    async def translate(self, text):
        texts = self.slice(text)
        for t in texts:
            await self.reset()
            for i in t:
                async for [finished, j] in self.bot.ask_stream(i, conversation_style=ConversationStyle.precise):
                    if not finished:
                        yield {"status": "ok", "type": "data", "data": j}
                yield {"status": "ok", "type": "conversation_finished"}
            yield {"status": "ok", "type": "bot_finished"}
