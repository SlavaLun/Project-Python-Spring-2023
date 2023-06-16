def draw_on_canvas():
    global canvas, draw
    data = request.get_json()

    if not canvas or not draw:
        return 'No canvas created.'

    if 'tool' not in data or 'position' not in data:
        return 'Invalid request data.'

    tool = data['tool']
    position = data['position']

    if tool == 'brush':
        draw.ellipse((position[0] - brush_size, position[1] - brush_size,
                      position[0] + brush_size, position[1] + brush_size), fill=color)

    if tool == 'eraser':
        draw.rectangle((position[0] - brush_size, position[1] - brush_size,
                        position[0] + brush_size, position[1] + brush_size), fill=(255, 255, 255, 0))

    return 'Drawing added to canvas.'


def save_canvas():
    global canvas

    if not canvas:
        return 'No canvas created.'

    canvas.save('static/modified_image.png')
    return send_file('static/modified_image.png', as_attachment=True)


def clear_canvas():
    global canvas, draw

    canvas = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    return 'Canvas cleared.'


with app.app_context():
    db.create_all()
app.run(debug=True)
