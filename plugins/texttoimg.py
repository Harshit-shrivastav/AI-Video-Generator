from PIL import Image, ImageDraw, ImageFont

def generate_background_image(width, height, background_color, border_width, border_color):
    # Create a new image object with the specified size and background color
    image = Image.new('RGBA', (width, height), background_color)

    # Create a new image object with the border dimensions and color
    border_top_bottom = Image.new('RGBA', (width, border_width), border_color)
    border_left_right = Image.new('RGBA', (border_width, height), border_color)

    # Paste the borders onto the main image, adjusting positions and dimensions
    image.paste(border_top_bottom, (0, 0))  # Top
    image.paste(border_top_bottom, (0, height - border_width))  # Bottom
    image.paste(border_left_right, (0, 0))  # Left
    image.paste(border_left_right, (width - border_width, 0))  # Right

    return image

def draw_body_text_on_image(background_image, body_text, font_path, margin=100):
    # Load the font for body text with an increased font size
    body_text_font = ImageFont.truetype(font_path, 36)

    # Create a drawing object
    draw = ImageDraw.Draw(background_image)

    # Split the text into lines
    lines = body_text.split('\n')

    # Calculate the total height of the text
    total_height = body_text_font.size * len(lines)

    # Calculate the y-coordinate for starting the body text
    body_text_y = margin

    remaining_text = ''

    # Draw each line of the body text onto the background image
    for line in lines:
        words = line.split()
        line_width = 0
        line_text = ''
        for word in words:
            word_width = draw.textlength(word + ' ', font=body_text_font)
            if line_width + word_width > background_image.width - margin * 2:
                draw.text((margin, body_text_y), line_text, font=body_text_font, fill=(0, 0, 0))
                body_text_y += body_text_font.size
                if body_text_y + body_text_font.size > background_image.height - margin:
                    remaining_text += ' '.join(words) + '\n'
                    break
                line_width = 0
                line_text = ''
            line_width += word_width
            line_text += word + ' '
        if line_text:
            draw.text((margin, body_text_y), line_text, font=body_text_font, fill=(0, 0, 0))
            body_text_y += body_text_font.size

    if remaining_text:
        return background_image, remaining_text.strip()
    else:
        return background_image, None

background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235, 255))

result = draw_body_text_on_image(
    background_image,
    body_text='The definite article is the word the. It limits the meaning of a noun to one particular thing. For example, your friend might ask, "Are you going to the party this weekend?" The definite article tells you that your friend is referring to a specific party that both of you already know about. The definite article can be used with singular, plural, or uncountable nouns. Below are some examples of the definite article, the, used in context.',
    font_path="F.ttf",
    margin=100
)

if result[1]:
    print(f"Remaining text: {result[1]}")

background_image.save("final_image_with_text.png")
