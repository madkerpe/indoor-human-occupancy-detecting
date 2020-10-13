from PIL import Image, ImageDraw
import random

def convert_to_thermal_image(width, height, pixels):
    img = Image.new('RGB', (width, height))
    d = ImageDraw.Draw(img)

    heat_min = min(pixels)
    heat_max = max(pixels) - heat_min

    red_pixels = [int(((pixel - heat_min) / heat_max)*255) for pixel in pixels]

    for x in range(width):
        for y in range(height):
            d.point((x,y), fill=(red_pixels[x + y * width], 0, 255 - red_pixels[x + y * width]))

    img.save('thermal_image.png')


if __name__ == "__main__":
    width = 32
    height = 24
    pixels = [random.randrange(0, 100) for _ in range(width * height)]
    convert_to_thermal_image(width, height, pixels)