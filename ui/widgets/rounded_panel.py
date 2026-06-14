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
    create_rounded_rect(
        widget,
        2, 2, w-2, h-2,
        radius=20,
        fill=const.ROUNDED_PANELS_COLOR,
        outline=const.ROUNDED_PANELS_BORDER_COLOR,
        width=1.5,
        tags="rounded_bg"
    )
    widget.tag_lower("rounded_bg")

def resize_inner(widget, event=None):
    w = widget.winfo_width()
    h = widget.winfo_height()
    widget.itemconfig("inner", width=w-40, height=h-40)