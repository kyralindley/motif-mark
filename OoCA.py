#!/usr/bin/env python
import cairo

# Set the dimensions of the surface
WIDTH, HEIGHT = 400, 400

# Create a Cairo surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Set the origin for drawing
ctx.translate(100, 100)  # Translate to (100, 100)

# Draw a line
ctx.set_source_rgb(1, 0, 0)  # Set color to red
ctx.set_line_width(5)  # Set line width
ctx.move_to(50, 50)  # Move to starting point
ctx.line_to(200, 200)  # Draw line to end point
ctx.stroke()  # Stroke the line

# Draw a rectangle
ctx.set_source_rgb(0, 0, 1)  # Set color to blue
ctx.rectangle(150, 150, 100, 50)  # Draw rectangle
ctx.stroke()  # Stroke the rectangle

# Save the surface to a PNG file
surface.write_to_png("line_and_rectangle.png")
