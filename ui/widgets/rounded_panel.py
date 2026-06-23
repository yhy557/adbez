import config.constants as const


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def draw_rounded(widget, event=None):
    widget.delete("rounded_bg")
    w = widget.winfo_width()
    h = widget.winfo_height()
    if w < 4 or h < 4:
        return
    create_rounded_rect(
        widget,
        1, 1, w-1, h-1,
        radius=18,
        fill=const.ROUNDED_PANELS_COLOR,
        outline=const.ROUNDED_PANELS_BORDER_COLOR,
        width=1,
        tags="rounded_bg"
    )
    widget.tag_lower("rounded_bg")


def resize_inner(widget, event=None):
    w = widget.winfo_width()
    h = widget.winfo_height()
    if w > 1 and h > 1:
        widget.itemconfig("inner", width=w-30, height=h-20)