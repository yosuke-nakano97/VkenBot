import discord

class JumpView(discord.ui.View):
    def __init__(self, timeout=180, user_id=None):
        self.user_id = user_id
        super().__init__(timeout=timeout)
        self.add_item(JumpButton(user_id=self.user_id))


class JumpButton(discord.ui.Button):
    def __init__(self,timeout=180,user_id=None):
        link = "http://test.com/"
        self.user_id = user_id
        super().__init__(style=discord.ButtonStyle.gray, label=f"{self.user_id}", url="https://www.youtube.com/watch?v=g8NxFO-BPo4")
        