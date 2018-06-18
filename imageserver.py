import os
import time
from flask import Flask, render_template, request, g
from flask_pymongo import PyMongo
from pymongo import MongoClient
from scipy.ndimage import filters
from numpy import zeros, array
import numpy as np
from PIL import Image, ImageFilter
import StringIO

app = Flask(__name__)
mongo = PyMongo(app)

client = MongoClient('localhost', 27017)
db = client['assets']
db_log = client['log']

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

@app.route('/')
def home_page():
	images = db.images.find()
	image_names = []
	for image in images:
		print image
		image_names.append(image['imagename'])
	return render_template('homepage.html', names=image_names)

@app.route('/list')
def search():
	max_width = int(request.args.get('max_width'))
	min_area = int(request.args.get('min_area'))
	min_bits_per_pix = int(request.args.get('min_bits_per_pix'))

	height = min_area/max_width
	size = min_bits_per_pix/8

	images = db.images.find({'width':{'$lte': max_width}, 'height':{'$gte': height}, 'size':{'$gte': size}})
	image_names = []
	for image in images:
		print image
		image_names.append(image['imagename'])
	return render_template('list_page.html', names=image_names)

@app.route('/image/<imagename>/<filtertype>')
def imageFilter(imagename, filtertype):
	value = int(request.args.get('value'))

	greyscale_image = Image.open(APP_ROOT+'/structura-techchallenge-assets/'+imagename+'.jpg').convert('LA')

	output = StringIO.StringIO()

	if filtertype == "grayscale":
		greyscale_image.save(output, "PNG")

	elif filtertype == "lowpass":
		lowpass_image = greyscale_image.filter(ImageFilter.GaussianBlur(radius=value))
		output = StringIO.StringIO()
		lowpass_image.save(output, "PNG")

	elif filtertype == "crop":
		width, height = greyscale_image.size
		left = (width - value) / 2
		top = (height - value) / 2
		right = (width + value) / 2
		bottom = (height + value) / 2

		cropped_image = greyscale_image.crop((left, top, right, bottom))
		cropped_image.save(output, "PNG")

	elif filtertype == "dx":
		greyscale_image_x_array = zeros(array(greyscale_image).shape)
		filters.sobel(greyscale_image, 1, greyscale_image_x_array)
		greyscale_image_x = Image.fromarray(np.uint8(greyscale_image_x_array * 255), 'LA')
		greyscale_image_x.save(output, "PNG")

	elif filtertype == "dy":
		greyscale_image_y_array = zeros(array(greyscale_image).shape)
		filters.sobel(greyscale_image, 0, greyscale_image_y_array)
		greyscale_image_y = Image.fromarray(np.uint8(greyscale_image_y_array * 255), 'LA')
		greyscale_image_y.save(output, "PNG")

	elif filtertype == "downsample":
		width, height = greyscale_image.size
		downsampled_image = greyscale_image.resize((width/value, height/value))
		downsampled_image.save(output, "PNG")

	elif filtertype == "rotate":
		rotated_image = greyscale_image.rotate(360-value)
		rotated_image.save(output, "PNG")

	else:
		return "invalid filter type"

	contents = output.getvalue().encode("base64")
	output.close()
	print request
	logs = db_log.logs
	log_data = {
		'imagename': imagename,
		'filtertype': filtertype,
		'request_timestamp': g.request_start_time,
		'processing_time': g.request_time()

	}
	result = logs.insert_one(log_data)
	print('One image: {0}'.format(result.inserted_id))
	return render_template('filtered_image_page.html', filtered_image=contents)

@app.route('/log')
def show_log():
	entries = db_log.logs.find().sort('id', -1).limit(100)
	return render_template('log_page.html', entries=entries)

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=3000)