from PIL import Image, ImageDraw, ImageFont

def generate_background_image(width, height, background_color, border_width, border_color):
    image = Image.new('RGBA', (width, height), background_color + (255,))
    border_top_bottom = Image.new('RGBA', (width, border_width), (*border_color, 255))
    border_left_right = Image.new('RGBA', (border_width, height), (*border_color, 255))
    image.paste(border_top_bottom, (0, 0))
    image.paste(border_top_bottom, (0, height - border_width))
    image.paste(border_left_right, (0, 0))
    image.paste(border_left_right, (width - border_width, 0))
    return image

def gen_slide(background_image, body_text, font_path, margin=100, image_path=None):
    body_text_font = ImageFont.truetype(font_path, 52)
    draw = ImageDraw.Draw(background_image)
    lines = [line.split(' ') for line in body_text.replace('\n\n', '\n').split('\n')]
    max_line_width = background_image.width - margin * 2
    total_height = sum(body_text_font.size * (len(line) + (1 if any('\n' in word for word in line) else 0)) for line in lines)
    body_text_y = margin
    if image_path:
        inserted_image = Image.open(image_path).convert('RGBA')  # Convert to RGBA mode
        inserted_image = inserted_image.resize((400, 300), resample=Image.BICUBIC)
        background_image.paste(inserted_image, ((background_image.width - inserted_image.width) // 2, background_image.height - inserted_image.height - margin), inserted_image)
        body_text_y = margin
    remaining_text = ''
    remaining_lines = []
    for line in lines:
        line_width = 0
        line_text = ''
        for word in line:
            word_width = draw.textlength(word + ' ', font=body_text_font)
            if line_width + word_width > max_line_width:
                draw.text((margin, body_text_y), line_text, font=body_text_font, fill=(0, 0, 0))
                body_text_y += body_text_font.size
                if body_text_y + body_text_font.size >= background_image.height - margin - (inserted_image.height if image_path else 0):
                    remaining_lines.append(' '.join(line))
                    remaining_text += '\n' + ' '.join(remaining_lines)
                    return background_image, remaining_text.strip()
                line_width = 0
                line_text = ''
            line_width += word_width
            line_text += word + ' '
        if line_text:
            draw.text((margin, body_text_y), line_text, font=body_text_font, fill=(0, 0, 0))
            body_text_y += body_text_font.size
    return background_image, None