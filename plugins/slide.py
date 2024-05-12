from PIL import Image, ImageDraw, ImageFont

def generate_background_image(width, height, background_color, border_width, border_color):
    image = Image.new('RGBA', (width, height), background_color + (255,))
    border_top_bottom = Image.new('RGBA', (width, border_width), border_color + (255,))
    border_left_right = Image.new('RGBA', (border_width, height), border_color + (255,))

    image.paste(border_top_bottom, (0, 0))
    image.paste(border_top_bottom, (0, height - border_width))
    image.paste(border_left_right, (0, 0))
    image.paste(border_left_right, (width - border_width, 0))

    return image

def write_text_on_image(background_image, text, font_path="assets/fonts/Roboto-Black.ttf", font_size=36, text_color=(0, 0, 0)):
    width, height = background_image.size
    draw = ImageDraw.Draw(background_image)
    font = ImageFont.truetype(font_path, size=font_size)
    text_x = 100
    text_y = 100
    line_width = 0
    max_height = height - 100 - font_size  # Maximum height for text with a 100-pixel margin at the bottom and considering font height
    words = text.split()
    remaining_text = []
    written_text = []
    last_period_index = None

    for i, word in enumerate(words):
        word_width = font.getsize(word)[0]

        # Handle long words that don't fit on a single line
        if word_width >= width - 200:
            for char in word:
                char_width = font.getsize(char)[0]
                if line_width + char_width >= width - 200:
                    text_y += font_size
                    if text_y >= max_height:
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
            if text_y >= max_height:
                remaining_text = words[i:]
                break
            line_width = word_width
        else:
            line_width += word_width + font.getsize(' ')[0]
        written_text.append(word)
        draw.text((text_x + line_width - word_width, text_y), word, font=font, fill=text_color)

    if last_period_index is not None:
        written_text = written_text[:last_period_index]
        remaining_text = words[last_period_index:]

    extra_text = ' '.join(remaining_text)
    written_text = ' '.join(written_text)
    print(f"Text written on image: {written_text}")
    if extra_text:
        print(f"Extra text: {extra_text}")
        return background_image, written_text, extra_text
    else:
        return background_image, written_text, None

"""
image = Image.open("background_image.jpg")
output_image, written_text, extra_text = write_text_on_image(image, "Hello, this is a long text to test the function")
output_image.show()
"""
