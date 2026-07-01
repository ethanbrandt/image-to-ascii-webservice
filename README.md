# Image to ASCII Webservice
**CURRENTLY UNDER CONSTRUCTION**

## Converting the images to ascii
The edge detection algorithm is a simple extended difference of gaussians + sobel filter edge detection algorithm. Then we just get the average luminance in each 8x8 pixel block and quantize the averaged values to one of a few characters. Layer the luminance below the edge outlines and the final ascii art image comes together.

### TODO
- [x] Implement the image to ascii algorithm
- [ ] Make it a webservice (?)