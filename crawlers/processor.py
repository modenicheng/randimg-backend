from . import utils
from . import configs


def process_image(image: dict) -> dict:
    try:
        image_path = configs.IMAGE_DIR + image['image_path']
        colors, primary = utils.extract_theme_colors(image_path)
        data = {
            **image,
            "colors": {
                "primary_color": primary,
                "colors": colors
            },
        }
        return data
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(e)
        return image
