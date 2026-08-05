from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta
import calendar
import sys
import os


# ============================================================
# CONFIGURATION
# ============================================================

CELL_SIZE = 18
CELL_GAP = 3

TOP_SPACE = 32

TEXT_COLOR = (150, 160, 175)
BACKGROUND_COLOR = (13, 17, 23)

MONTH_FONT_SIZE = 10


# ============================================================
# FONT
# ============================================================

def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]

    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


MONTH_FONT = get_font(MONTH_FONT_SIZE)


# ============================================================
# FIND MONTH POSITIONS
# ============================================================

def get_month_positions(start_date, end_date, cell_width):
    """
    Return the x-position of each month label.

    GitHub contribution calendars are arranged by weeks.
    Each column represents one week.
    """

    # Move to Sunday before/at start date
    current = start_date - timedelta(
        days=(start_date.weekday() + 1) % 7
    )

    positions = []

    last_month = None

    while current <= end_date:

        if current.month != last_month:

            week_number = (
                current - start_date
            ).days // 7

            x = week_number * cell_width

            positions.append(
                (
                    current.strftime("%b"),
                    x
                )
            )

            last_month = current.month

        current += timedelta(days=7)

    return positions


# ============================================================
# DRAW MONTH LABELS
# ============================================================

def add_month_labels(frame):
    draw = ImageDraw.Draw(frame)

    width, height = frame.size

    # Approximate contribution grid area.
    #
    # Space Shooter uses the contribution graph as
    # its playing field. We reserve a small area above it.
    grid_left = 20
    grid_top = TOP_SPACE

    cell_width = CELL_SIZE + CELL_GAP

    # GitHub-style contribution graph:
    # 53 weeks × 7 days
    weeks = 53

    start = date.today() - timedelta(days=364)
    end = date.today()

    months = get_month_positions(
        start,
        end,
        cell_width
    )

    for month, week_position in months:

        x = grid_left + week_position

        # Keep labels inside image
        if x < 0 or x > width - 25:
            continue

        draw.text(
            (x, 7),
            month,
            fill=TEXT_COLOR,
            font=MONTH_FONT
        )

    return frame


# ============================================================
# PROCESS GIF
# ============================================================

def process_gif(input_file, output_file):

    gif = Image.open(input_file)

    frames = []

    frame_count = getattr(gif, "n_frames", 1)

    for frame_number in range(frame_count):

        gif.seek(frame_number)

        frame = gif.convert("RGBA")

        # ----------------------------------------------------
        # Add a dark strip at the top for month names
        # ----------------------------------------------------

        width, height = frame.size

        new_frame = Image.new(
            "RGBA",
            (
                width,
                height + TOP_SPACE
            ),
            BACKGROUND_COLOR
        )

        # Put original game below
        new_frame.alpha_composite(
            frame,
            (0, TOP_SPACE)
        )

        # Add month names
        new_frame = add_month_labels(new_frame)

        frames.append(
            new_frame.convert("P")
        )

    # --------------------------------------------------------
    # Save animated GIF
    # --------------------------------------------------------

    duration = gif.info.get("duration", 40)

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=False,
        disposal=2
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Usage: python add_calendar.py "
            "input.gif output.gif"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_gif(
        input_file,
        output_file
    )

    print(
        f"✅ Created calendar Space Shooter: "
        f"{output_file}"
    )
