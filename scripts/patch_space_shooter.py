from pathlib import Path


ROOT = Path("space-shooter")

GAME_STATE = (
    ROOT
    / "src"
    / "gh_space_shooter"
    / "game"
    / "game_state.py"
)

RENDERER = (
    ROOT
    / "src"
    / "gh_space_shooter"
    / "game"
    / "renderer.py"
)


# ============================================================
# 1. Store contribution data inside GameState
# ============================================================

game_state = GAME_STATE.read_text()

old = """        self.starfield = Starfield()
        self.ship = Ship(self)
        self.enemies: List[Enemy] = []
"""

new = """        # Keep the original contribution data so the renderer
        # can calculate the exact GitHub month positions.
        self.contribution_data = contribution_data

        self.starfield = Starfield()
        self.ship = Ship(self)
        self.enemies: List[Enemy] = []
"""

if old not in game_state:
    raise RuntimeError(
        "Could not find GameState insertion point."
    )

game_state = game_state.replace(old, new, 1)

GAME_STATE.write_text(game_state)


# ============================================================
# 2. Replace renderer
# ============================================================

renderer = """\"\"\"Renderer for drawing game frames using Pillow.\"\"\"

from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from ..constants import NUM_WEEKS, SHIP_POSITION_Y
from .game_state import GameState
from .render_context import RenderContext


WATERMARK_TEXT = "by czl9707/gh-space-shooter"


class Renderer:
    \"\"\"Renders game state as PIL Images.\"\"\"

    def __init__(
        self,
        game_state: GameState,
        render_context: RenderContext,
        watermark: bool = False,
    ):
        self.game_state = game_state
        self.context = render_context
        self.watermark = watermark

        self.grid_width = (
            NUM_WEEKS
            * (self.context.cell_size + self.context.cell_spacing)
        )

        self.grid_height = (
            SHIP_POSITION_Y
            * (self.context.cell_size + self.context.cell_spacing)
        )

        self.width = self.grid_width + 2 * self.context.padding
        self.height = self.grid_height + 2 * self.context.padding

        self.month_font = ImageFont.load_default()

    # ========================================================
    # MAIN FRAME
    # ========================================================

    def render_frame(self) -> Image.Image:
        \"\"\"Render the current game state.\"\"\"

        img = Image.new(
            "RGB",
            (self.width, self.height),
            self.context.background_color,
        )

        overlay = Image.new(
            "RGBA",
            (self.width, self.height),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(
            overlay,
            "RGBA",
        )

        # Original Space Shooter
        self.game_state.draw(
            draw,
            self.context,
        )

        # ====================================================
        # GitHub contribution calendar month labels
        # ====================================================

        self._draw_month_labels(draw)

        if self.watermark:
            self._draw_watermark(draw)

        combined = Image.alpha_composite(
            img.convert("RGBA"),
            overlay,
        )

        return combined.convert("RGB")

    # ========================================================
    # MONTH LABELS
    # ========================================================

    def _draw_month_labels(
        self,
        draw: ImageDraw.ImageDraw,
    ) -> None:

        weeks = self.game_state.contribution_data["weeks"]

        cell_width = (
            self.context.cell_size
            + self.context.cell_spacing
        )

        # GitHub places the month name above the week
        # containing the first day of that month.
        month_positions = []

        previous_month = None

        for week_index, week in enumerate(weeks):

            for day in week["days"]:

                current_date = datetime.strptime(
                    day["date"],
                    "%Y-%m-%d",
                )

                month = current_date.month

                # Only place a label on the first week
                # that contains day 1 of a month.
                if (
                    current_date.day == 1
                    and month != previous_month
                ):

                    month_positions.append(
                        (
                            week_index,
                            current_date.strftime("%b"),
                        )
                    )

                    previous_month = month

                    break

        # Draw labels
        for week_index, month_name in month_positions:

            x = (
                self.context.padding
                + week_index * cell_width
            )

            # Month labels sit just above the contribution grid.
            y = self.context.padding - 17

            draw.text(
                (x, y),
                month_name,
                font=self.month_font,
                fill=(139, 148, 158, 255),
            )

    # ========================================================
    # WATERMARK
    # ========================================================

    def _draw_watermark(
        self,
        draw: ImageDraw.ImageDraw,
    ) -> None:

        font = ImageFont.load_default()

        color = (
            100,
            100,
            100,
            128,
        )

        margin = 5

        bbox = draw.textbbox(
            (0, 0),
            WATERMARK_TEXT,
            font=font,
        )

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (
            self.width
            - text_width
            - margin
        )

        y = (
            self.height
            - text_height
            - margin
        )

        draw.text(
            (x, y),
            WATERMARK_TEXT,
            font=font,
            fill=color,
        )
"""


RENDERER.write_text(renderer)

print("✅ Space Shooter successfully modified!")
print("✅ GitHub-style month labels added.")
