import logging
import textwrap
from typing import TYPE_CHECKING

from .cog import ReportCog

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.report")

LOGO = textwrap.dedent(r"""
    +---------------------------------------+
    |   Ballsdex Report Pack by Ray Hsueh   |
    |       Licensed under Apache 2.0       |
    +---------------------------------------+
""").strip()


async def setup(bot: "BallsDexBot"):
    print(LOGO)
    log.info("Loading Report package...")
    await bot.add_cog(ReportCog(bot))
    log.info("Report package loaded successfully!")
