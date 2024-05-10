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

def draw_body_text_on_image(background_image, body_text, font_path, margin=100, image_path=None):
    # Load the font for body text with an increased font size
    body_text_font = ImageFont.truetype(font_path, 36)

    # Create a drawing object
    draw = ImageDraw.Draw(background_image)

    # Split the text into lines, handling newlines within lines
    lines = [line.split(' ') for line in body_text.replace('\n\n', '\n').split('\n')]

    # Calculate the maximum line width
    max_line_width = background_image.width - margin * 2

    # Calculate the available height for body text
    available_height_for_text = background_image.height - margin
    if image_path:
        inserted_image = Image.open(image_path).convert('RGBA')  # Convert to RGBA mode
        inserted_image = inserted_image.resize((400, 300), resample=Image.BICUBIC)
        available_height_for_text -= (inserted_image.height + margin)

    remaining_text = ''

    # Draw each line of the body text onto the background image
    body_text_y = margin
    for line in lines:
        line_width = 0
        line_text = ''
        for word in line:
            word_width = draw.textlength(word + ' ', font=body_text_font)
            if line_width + word_width > max_line_width:
                draw.text((margin, body_text_y), line_text, font=body_text_font, fill=(0, 0, 0))
                body_text_y += body_text_font.size
                if body_text_y + body_text_font.size > available_height_for_text:
                    remaining_text += '\n' + ' '.join(line)
                    break
                line_width = 0
                line_text = ''
            line_width += word_width
            line_text += word + ' '
        if line_text:
            if body_text_y + body_text_font.size <= available_height_for_text:
                draw.text((margin, body_text_y), line_text, font=body_text_font, fill=(0, 0, 0))
                body_text_y += body_text_font.size
            else:
                remaining_text += '\n' + line_text.strip()

    # Insert the image at the bottom side of the background image if an image path is provided
    if image_path:
        inserted_image = Image.open(image_path).convert('RGBA')  # Convert to RGBA mode
        inserted_image = inserted_image.resize((400, 300), resample=Image.BICUBIC)
        background_image.paste(inserted_image, ((background_image.width - inserted_image.width) // 2, background_image.height - inserted_image.height - margin), inserted_image)
        if body_text_y + inserted_image.height + margin >= background_image.height:
            remaining_text += '\n[Image inserted]'

    return background_image, remaining_text.strip()
