import os
from pymongo import MongoClient
from PIL import Image

client = MongoClient('localhost', 27017)
db = client.assets
directory = os.path.dirname(os.path.abspath(__file__))+'/structura-techchallenge-assets/'

for filename in os.listdir(directory):
    if filename.endswith(".jpg"):
        jpgfile = Image.open(directory+filename)
        width, height = jpgfile.size
        size_bytes = os.stat(directory+filename).st_size
        images = db.images
        image_data = {
        	'imagename': filename.rsplit('.', 1)[0],
    		'width': width,
    		'height': height,
    		'size': size_bytes
    	}
        result = images.insert_one(image_data)
        print('One image: {0}'.format(result.inserted_id))
        continue
    else:
        continue
