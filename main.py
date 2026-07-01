import cv2
import numpy as np

def xdog_filter(img, sigma=1.0, k=1.6, p=19.0, epsilon=0.1, phi=10.0):
	if img is None:
		raise FileNotFoundError("Could not open or find the image.")
	img = img.astype(np.float32) / 255.0

	blur1 = cv2.GaussianBlur(img, (0, 0), sigma)
	blur2 = cv2.GaussianBlur(img, (0, 0), sigma * k)

	xdog = (1.0 + p) * blur1 - p * blur2

	output = np.ones_like(xdog)

	mask = xdog < epsilon


	output[mask] = 1.0 + np.tanh(phi * (xdog[mask] - epsilon))

	output = (output > 0.5) * 1.0

	output = (output * 255.0).astype(np.uint8)
	return output

if __name__ == "__main__":
	img = cv2.imread("susie_deltarune.jpg", cv2.IMREAD_GRAYSCALE)
	print(img[700, 400])
	result = xdog_filter(img, sigma=0.8, k = 1.7, p = 25.0, epsilon=0.08, phi=12.0)
	sobeled_img_x = cv2.Sobel(result, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
	sobeled_img_y = cv2.Sobel(result, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=3)

	mag = cv2.magnitude(sobeled_img_x, sobeled_img_y)
	grad = np.degrees(np.arctan2(sobeled_img_y, sobeled_img_x))
	edge = (grad + 90) % 180

	cv2.imwrite("xdog.jpg", img)

	with open("sobel_data.txt", "w") as f:
		h, w = mag.shape

		h = h // 8
		w = w // 8

		for y in range(h):
			row_vals = []

			for x in range(w):
				m = 0.0

				vert = 0
				horiz = 0
				f_slash = 0
				b_slash = 0

				lum = 0

				for i in range(8):
					for j in range(8):
						lum += float(img[i + y * 8, j + x * 8])
						m += mag[i + y * 8, j + x * 8]
						e = edge[i + y * 8, j + x * 8]
						
						if e < 22.5 or e >= 157.5:
							horiz += 1
						elif e < 67.5:
							b_slash += 1
						elif e < 112.5:
							vert += 1
						else:
							f_slash += 1
			
				m = m / 64.0
				lum = lum / 64.0

				if m < 300:
					if lum < 50:
						row_vals.append(' ')
					elif lum < 100:
						row_vals.append('.')
					elif lum < 150:
						row_vals.append('*')
					elif lum < 200:
						row_vals.append('#')
					else:
						row_vals.append('@')
					continue
				
				best = max(vert, horiz, f_slash, b_slash)
				if vert == best:
					row_vals.append('|')
				elif horiz == best:
					row_vals.append('-')
				elif f_slash == best:
					row_vals.append('/')
				else:
					row_vals.append('\\')

			f.write("".join(row_vals) + "\n")

	print("done.")