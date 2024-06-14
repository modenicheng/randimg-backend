import PIL

def get_image_resolution(image_path: str) -> dict:
    pass

def get_image_colours(image_path: str) -> dict:
    '''
    {
        "colour_primary": "hexcolour",
        "colour_series": [
            "hexcolour_light",
            "hexcolour_dark",
            ...
        ]
    }
    '''
    pass

from dogecloud import oss

def upload_image(image_path: str, image_name: str) -> str:
    '''
    upload image to dogecloud
    '''
    return oss.upload_file(image_path, image_name)