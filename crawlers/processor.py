from . import utils
from . import configs, uploader
from db import crud
import threading
def process_image(image: dict) -> dict:
    try:
        image_path = configs.IMAGE_DIR + image['image_path']
        colors, primary = utils.extract_theme_colors(image_path, scale=0.5)
        data = {
            **image,
            "image_url": image['url'],
            "colors": {
                "primary_color": primary,
                "colors": colors
            },
        }
        crud.create_image_rebuild(data)
        t = threading.Thread(target=uploader.upload_image_file, args=(image_path, image['image_path']))
        t.start()
        return data
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(e)
        return image
