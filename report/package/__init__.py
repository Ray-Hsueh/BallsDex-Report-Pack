import logging
from typing import TYPE_CHECKING

from .cog import ReportCog

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.report")

LOGO = """
╔═══════════════════════════════════════╗
║  Ballsdex Report Pack by Ray Hsueh    ║
║        Licensed under Apache 2.0      ║
╚═══════════════════════════════════════╝
"""


async def setup(bot: "BallsDexBot"):
    log.info(LOGO)
    log.info("Loading Report package...")
    await bot.add_cog(ReportCog(bot))
    log.info("Report package loaded successfully!")
