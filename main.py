import cv2
import numpy as np
from flask import Flask, request, Response
import time

app = Flask(__name__)

@app.post("/ascii")
def ascii_from_image():
	if "image" not in request.files:
		return {"error" : "missing image field"}, 400
	
	file = request.files["image"]
	data = file.read()

	arr = np.frombuffer(data, np.uint8)
	img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
	if img is None:
		return {"error" : "could not decode image"}, 400
	
	ascii_text = image_to_ascii(img)

	return Response(ascii_text, mimetype="text/plain")

def xdog_filter(img, blur_sigma, simga_mult, edge_strength, threshold, sharpness):
	img = img.astype(np.float32) / 255.0

	blur1 = cv2.GaussianBlur(img, (0, 0), blur_sigma)
	blur2 = cv2.GaussianBlur(img, (0, 0), blur_sigma * simga_mult)

	xdog = (1.0 + edge_strength) * blur1 - edge_strength * blur2

	mask = xdog < threshold

	output = np.ones_like(xdog)
	output[mask] = 1.0 + np.tanh(sharpness * (xdog[mask] - threshold))
	output = (output > 0.5) * 1.0
	output = (output * 255.0).astype(np.uint8)
	return output

def image_to_ascii(img, block_size=8):
	start_time = time.perf_counter()
	
	# xdog or extended difference of gaussians is being used as a preprocessing pass to make the sobel filter much clearer
	xdoged_img = xdog_filter(img, blur_sigma=0.8,  sigma_mult=1.7, edge_strength=25.0, threshold=0.08, sharpness=12.0)

	xdog_time = time.perf_counter()

	# sobel gives us the 2D vector field of edge directions which we can use to determine the right edge character
	sobeled_img_x = cv2.Sobel(xdoged_img, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
	sobeled_img_y = cv2.Sobel(xdoged_img, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=3)

	sobel_time = time.perf_counter()

	magnitudes = cv2.magnitude(sobeled_img_x, sobeled_img_y)
	gradient = np.degrees(np.arctan2(sobeled_img_y, sobeled_img_x))
	edge_angles = (gradient + 90) % 180

	h, w = magnitudes.shape

	ascii_rows = h // block_size
	ascii_cols = w // block_size
	crop_h = ascii_rows * block_size
	crop_w = ascii_cols * block_size

	if ascii_rows == 0 or ascii_cols == 0:
		return ""

	img_crop = img[:crop_h, :crop_w]
	mag_crop = magnitudes[:crop_h, :crop_w]
	edge_crop = edge_angles[:crop_h, :crop_w]

	block_shape = (ascii_rows, block_size, ascii_cols, block_size)
	img_blocks = img_crop.reshape(block_shape)
	mag_blocks = mag_crop.reshape(block_shape)
	edge_blocks = edge_crop.reshape(block_shape)

	lum = img_blocks.mean(axis=(1, 3))
	avg_mag = mag_blocks.mean(axis=(1, 3))

	horiz = ((edge_blocks < 22.5) | (edge_blocks >= 157.5)).sum(axis=(1, 3))
	b_slash = ((edge_blocks >= 22.5) & (edge_blocks < 67.5)).sum(axis=(1, 3))
	vert = ((edge_blocks >= 67.5) & (edge_blocks < 112.5)).sum(axis=(1, 3))
	f_slash = ((edge_blocks >= 112.5) & (edge_blocks < 157.5)).sum(axis=(1, 3))

	edge_scores = np.stack((vert, horiz, f_slash, b_slash), axis=0)
	edge_chars = np.array(('|', '-', '/', '\\'))
	ascii_grid = edge_chars[np.argmax(edge_scores, axis=0)]

	lum_chars = np.select(
		(lum < 50, lum < 100, lum < 150, lum < 200),
		(' ', '.', '*', '#'),
		default='@'
	)
	ascii_grid = np.where(avg_mag < 300, lum_chars, ascii_grid)

	output = "".join("".join(row) + "\n" for row in ascii_grid)

	ascii_time = time.perf_counter()
	if app.debug:
		print("xdog_time:", xdog_time - start_time)
		print("sobel_time:", sobel_time - xdog_time)
		print("ascii_time:", ascii_time - sobel_time)
	return output

if __name__ == "__main__":
	app.run(debug=True)
