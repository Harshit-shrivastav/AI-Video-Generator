from PIL import Image, ImageDraw, ImageFont

def generate_background_image(width, height, background_color, border_width, border_color):
    image = Image.new('RGBA', (width, height), background_color + (255,))  # Adding 255 for alpha channel
    border_top_bottom = Image.new('RGBA', (width, border_width), (*border_color, 255))
    border_left_right = Image.new('RGBA', (border_width, height), (*border_color, 255))
    image.paste(border_top_bottom, (0, 0))  # Top
    image.paste(border_top_bottom, (0, height - border_width))  # Bottom
    image.paste(border_left_right, (0, 0))  # Left
    image.paste(border_left_right, (width - border_width, 0))  # Right
    return image

def write_text_on_image(background_image, text, output_image_path, title=None, font_path="arial.ttf", font_size=36, text_color=(0, 0, 0), title_font_size=48):
    width, height = background_image.size
    draw = ImageDraw.Draw(background_image)
    font = ImageFont.truetype(font_path, size=font_size)
    title_font = ImageFont.truetype(font_path, size=title_font_size)

    text_x = 100
    text_y = 100

    title_height = 0
    if title:
        title_width = font.getlength(title)
        draw.text(((width - title_width) / 2, 20), title, font=title_font, fill=text_color)
        title_height = title_font_size + 20  # Add vertical spacing of 20 pixels
        text_y += title_height

    max_height = height - 100 - font_size  # Maximum height for text with a 100-pixel margin at the bottom and considering font height
    lines_written = 0

    words = text.split()
    remaining_text = []
    written_text = []
    last_period_index = None

    line_width = 0 

    for i, word in enumerate(words):
        word_width = font.getlength(word)

        if word_width >= width - 200:
            for char in word:
                char_width = font.getlength(char)
                if line_width + char_width >= width - 200:
                    text_y += font_size
                    lines_written += 1
                    if text_y >= max_height + title_height:  # Consider the height of the title (if provided)
                        remaining_text = words[i:]
                        break
                    line_width = char_width
                else:
                    line_width += char_width
                written_text.append(char)
                draw.text((text_x + line_width - char_width, text_y), char, font=font, fill=text_color)
            continue

        if word.endswith('.'):
            last_period_index = i + 1  # Store the index of the word after the last period

        if line_width + word_width >= width - 200:
            text_y += font_size
            lines_written += 1
            if text_y >= max_height + title_height:  # Consider the height of the title (if provided)
                remaining_text = words[i:]
                break
            line_width = word_width
        else:
            line_width += word_width + font.getlength(' ')

        written_text.append(word)
        draw.text((text_x + line_width - word_width, text_y), word, font=font, fill=text_color)

    if last_period_index is not None:
        written_text = written_text[:last_period_index]
        remaining_text = words[last_period_index:]

    background_image.save(output_image_path)
    extra_text = ' '.join(remaining_text)
    written_text = ' '.join(written_text)

    print(f"Text written on image: {written_text}")
    if extra_text:
        print(f"Extra text: {extra_text}")

    return extra_text

# without title 
background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
extra_text = write_text_on_image(background_image, "This is another sentence. This is another sentence.", "output_without_title.png")

# with title
background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
title = "Example Title"
extra_text = write_text_on_image(background_image, "This is another sentence. This is another sentence.", "output_with_title.png", title=title)
