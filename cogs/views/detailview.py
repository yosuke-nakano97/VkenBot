import discord

class JumpView(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(JumpButton())


class JumpButton(discord.ui.Button):
    def __init__(self,timeout=180):
        link = "http://test.com/"
        super().__init__(style=discord.ButtonStyle.gray, label="click here!", url="https://www.youtube.com/watch?v=g8NxFO-BPo4")
        