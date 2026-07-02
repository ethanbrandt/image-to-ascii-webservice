import requests

with open("tests_list.txt", "r") as test_list:
	lines_array = [line.rstrip() for line in test_list]

failures = 0

for test_image in lines_array:
	with open(test_image, "rb") as f:
		response = requests.post("http://127.0.0.1:5000/ascii",files={"image" : f})
		print(response.text)
		with open(test_image.split('.', 1)[0] + ".txt", 'r') as output:
			if output.read() != response.text:
				print("Test Failed: ", test_image)
				failures += 1

print("\nTests Passed:", (len(lines_array) - failures), "/", len(lines_array))