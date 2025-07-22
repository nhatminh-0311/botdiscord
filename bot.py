import discord
import os
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

# Lấy token từ biến môi trường
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Bạn chưa thiết lập biến môi trường DISCORD_BOT_TOKEN!")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot đã đăng nhập: {bot.user}")

@bot.tree.command(name="ticket", description="Gửi nút mở ticket")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_command(interaction: discord.Interaction):
    button = Button(label="🎫 Mở Ticket", style=discord.ButtonStyle.green)

    async def button_callback(inter: discord.Interaction):
        guild = inter.guild
        staff_role = discord.utils.get(guild.roles, name="Admin/Supporter")  # Sửa lại nếu role có tên khác

        if not staff_role:
            await inter.response.send_message("❌ Không tìm thấy role 'Admin/Supporter'.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            inter.user: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True)
        }

        channel_name = f"ticket-{inter.user.name}".lower().replace(" ", "-")
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        close_button = Button(label="❌ Đóng Ticket", style=discord.ButtonStyle.red)

        async def close_callback(i: discord.Interaction):
            await i.channel.delete()

        close_button.callback = close_callback
        view = View()
        view.add_item(close_button)

        await channel.send(
            f"🎟️ Chào {inter.user.mention}, hãy nêu vấn đề của bạn. Staff sẽ hỗ trợ sớm!",
            view=view
        )

        await inter.response.send_message(f"✅ Đã tạo ticket: {channel.mention}", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)

    await interaction.response.send_message("📩 Bấm nút bên dưới để mở ticket!", view=view)

bot.run(TOKEN)
