import requests

with open("tests_list.txt", "r") as test_list:
	lines_array = [line.rstrip() for line in test_list]

for test_image in lines_array:
	with open(test_image, "rb") as f:
		response = requests.post("http://127.0.0.1:5000/ascii",files={"image" : f})
		with open(test_image.split('.', 1)[0] + ".txt", 'w') as output:
			output.write(response.text)
			print("Finished: " + test_image)
