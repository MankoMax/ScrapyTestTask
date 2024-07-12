import os
import json
from typing import Dict


class RentalPipeline:
    def process_item(self, item: Dict, spider) -> Dict:
        country = "Germany"
        domain = item['domain'].replace("/", "_").strip()
        rental_object = item['title'].replace("/", "_").strip()

        directory = os.path.join("output", country, domain, rental_object)
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, 'data.json')

        # we have to remove the domain key from the item before writing
        # it to a file to compile the output data structure
        item_copy = item.copy()
        item_copy.pop('domain')

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dict(item_copy), f, ensure_ascii=False, indent=4)

        return item
