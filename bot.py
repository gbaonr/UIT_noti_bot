import logging

# Command handlers
from commands import *

# Background task define
from background_task import *


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    # Khởi tạo bot
    app = Application.builder().token(TOKEN).build()

    # Thêm handler cho command /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("see_my_id", see_my_id))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("check", check_new_notification))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("get", get))
    app.add_handler(
        MessageHandler((filters.TEXT | filters.Sticker.ALL & ~filters.COMMAND), echo)
    )

    # Tạo task nền chạy song song với bot
    asyncio.create_task(background_task())

    print("Bot đang chạy...")

    # init bot manually to avoid blocking while using with asyncio.run(main())
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Đợi vô hạn để bot và task nền tiếp tục chạy
    try:
        await asyncio.Event().wait()  # Chờ không bao giờ hết
    except KeyboardInterrupt:
        print("Đang dừng bot...")
    finally:
        # Dừng bot và giải phóng tài nguyên
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
