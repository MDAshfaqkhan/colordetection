import cv2
import numpy as np
import pandas as pd
import colorsys
import streamlit as st
from PIL import Image

# Function to convert RGB to HLS (Hue, Lightness, Saturation)
def rgb_to_hls(r, g, b):
    return colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

# Function to convert HLS back to RGB
def hls_to_rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return [int(r*255), int(g*255), int(b*255)]

# Function to create complementary, triadic, and analogous colors
def create_contrast_colors(base_color):
    r, g, b = base_color
    h, l, s = rgb_to_hls(r, g, b)
    complementary_color = hls_to_rgb((h + 0.5) % 1.0, l, s)
    triadic_color1 = hls_to_rgb((h + 1/3) % 1.0, l, s)
    triadic_color2 = hls_to_rgb((h + 2/3) % 1.0, l, s)
    analogous_color1 = hls_to_rgb((h + 1/12) % 1.0, l, s)
    analogous_color2 = hls_to_rgb((h - 1/12) % 1.0, l, s)
    return [complementary_color, triadic_color1, triadic_color2, analogous_color1, analogous_color2]

# Function to create shades of the clicked color
def create_shades(base_color, num_shades=5):
    shades = []
    step = 20  # Difference between each shade
    for i in range(num_shades):
        new_shade = [max(0, min(c - i * step, 255)) for c in base_color]  # Adjust color
        shades.append(new_shade)
    return shades

# Reading the CSV for color names
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv("colors.csv", names=index, header=None)

# Function to get color name from RGB values
def getColorName(R, G, B):
    minimum = 10000
    cname = ""
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

# Function to crop a region around the selected coordinates
def crop_image(img, xpos, ypos, crop_size=50):
    # Get the dimensions of the image
    height, width, _ = img.shape
    
    # Define the cropping boundaries
    x_start = max(0, xpos - crop_size // 2)
    x_end = min(width, xpos + crop_size // 2)
    y_start = max(0, ypos - crop_size // 2)
    y_end = min(height, ypos + crop_size // 2)
    
    # Crop the image
    cropped_img = img[y_start:y_end, x_start:x_end]
    
    return cropped_img

# Function to draw grid lines and numbers on the image
def draw_grid(img, step=50):
    grid_img = img.copy()
    height, width, _ = grid_img.shape

    # Draw horizontal lines and numbers
    for y in range(step, height, step):
        cv2.line(grid_img, (0, y), (width, y), (255, 0, 0), 1)
        cv2.putText(grid_img, str(y), (5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # Draw vertical lines and numbers
    for x in range(step, width, step):
        cv2.line(grid_img, (x, 0), (x, height), (255, 0, 0), 1)
        cv2.putText(grid_img, str(x), (x, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    return grid_img

# Main function to display color, shades, and contrast colors
def display_colors(img, xpos, ypos):
    b, g, r = img[ypos, xpos]
    current_color = (r, g, b)

    color_name = getColorName(r, g, b)
    st.write(f"Selected Color: {color_name} (R={r}, G={g}, B={b}) at Coordinates: X={xpos}, Y={ypos}")

    # Display the cropped image around the selected coordinates
    cropped_img = crop_image(img, xpos, ypos)
    st.image(cropped_img, caption=f"Cropped Image around X={xpos}, Y={ypos}", use_column_width=False)

    # Display Shades
    shades = create_shades(current_color)
    st.write("Shades:")
    for shade in shades:
        st.write(f"Shade: {shade}")
        st.markdown(f"<div style='background-color: rgb({shade[0]}, {shade[1]}, {shade[2]}); height: 50px; width: 100%;'></div>", unsafe_allow_html=True)

    # Display Contrast Colors
    contrast_colors = create_contrast_colors(current_color)
    st.write("Contrast Colors:")
    for contrast in contrast_colors:
        st.markdown(f"<div style='background-color: rgb({contrast[0]}, {contrast[1]}, {contrast[2]}); height: 50px; width: 100%;'></div>", unsafe_allow_html=True)

# Streamlit app
st.title("Interactive Color Detection with Grid")

# Image upload
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
if uploaded_image is not None:
    # Load image using PIL
    img_pil = Image.open(uploaded_image)
    img = np.array(img_pil)

    # Draw grid on the image
    img_with_grid = draw_grid(img)

    # Display the image with grid in Streamlit
    st.image(img_with_grid, caption="Uploaded Image with Grid", use_column_width=True)
    
    # Let the user select the X and Y coordinates
    xpos = st.number_input("Select X coordinate", min_value=0, max_value=img.shape[1]-1, value=0)
    ypos = st.number_input("Select Y coordinate", min_value=0, max_value=img.shape[0]-1, value=0)
    
    # Display color, shades, contrast colors, and the cropped image
    if st.button("Get Colors"):
        display_colors(img, xpos, ypos)
