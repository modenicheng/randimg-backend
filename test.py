from db import crud
from icecream import ic

l = crud.get_image_list(
    offset=0,
    limit=1000,
    desc=True,
    raw_obj=True,
    more_data=True,
    full_list=True,
    # tags='赤脚',
    author=None
)
for i in l:
    ic(i.id, i.title, [(j.name, j.translated_name) for j in i.tags])

ic(len(l))
