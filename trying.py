#!/usr/bin/env python

import argparse
import re
import cairo 


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fasta", help="Input fasta", required=True)
    parser.add_argument("-o","--output", help="Output picture", required=True)
    return parser.parse_args()

args = get_args()
f = args.fasta
o = args.output
# intializing lists to hold the name of the gene and the length of the gene, I want the length of longest gene plus 10 on either side of the gene length to be the length of my context 
name = []
length = []

def read_motifs_from_file(m):
    motifs = {}
    with open(m,'r') as file:
        for line in file:
            line = line.strip()
            # Create regex pattern with 'Y' replaced by character sets for 'C', 'T', and 'U'
            regex_pattern = re.sub(r'Y', '[CTU]', line)
            motifs[line] = regex_pattern
    return motifs
##### COME BACK TO SCALE THE X USING THE GENE DICT, WHATEVER THE LONGEST GENE IS ADD 10 ON EITHER SIDE THEN MAKE THAT THE LENGTH OF THE CONTEXT
def process_fasta(file:str):
    '''This function takes a multi-line FASTA file, converts it into a one-line FASTA file with a header line and a single sequence line per gene, 
    extracts the gene name using regex, and returns a dictionary containing gene names as keys and sequences as values.'''
    gene_dict = {}  # Initialize the gene dictionary
    with open(file, "r") as fh:
        current_gene = None
        sequence = ''
        for line in fh:
            line = line.strip()
            if line.startswith('>'):  # If it's a header line
                if current_gene is not None:  # If we have already processed a gene
                    gene_dict[current_gene] = sequence  # Store the sequence in the dictionary
                    length.append(len(sequence))
                    sequence = ''  # Reset sequence for the next gene
                match = re.match(r'^>(\S+)', line)  # Extract gene name using regex
                name.append(current_gene)
                if match:
                    current_gene = match.group(1)
                    name.append(current_gene)
            else:
                sequence += line  # Concatenate sequence lines
        if current_gene is not None:  # Store the last gene sequence
            gene_dict[current_gene] = sequence
            length.append(len(sequence))
            name.append(current_gene)
            print(current_gene)
        name.pop(0)
    return gene_dict


# Function to draw legend
def draw_legend(ctx, x, y):
    # Define legend items and their corresponding colors
    legend_items = ["gene", "exon", "ygcy", "GUAUG", "catag", "YYYYYYYYYY"]
    legend_colors = ["black", "green", "pink", "purple", "blue", "black"]
    
    # Set font properties
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    
    # Draw legend box
    ctx.set_source_rgb(0, 0, 0)  # Black color for box outline
    ctx.rectangle(x, y, 100, len(legend_items) * 15 + 10)  # Adjust width as needed
    ctx.stroke()
    
    # Draw legend items
    for i, item in enumerate(legend_items):
        ctx.set_source_rgb(*cairo_color(legend_colors[i]))  # Set color
        ctx.rectangle(x + 5, y + 5 + i * 15, 10, 10)  # Draw colored rectangle
        ctx.fill()
        ctx.set_source_rgb(0, 0, 0)  # Black color for text
        ctx.move_to(x + 20, y + 10 + i * 15)  # Position text
        ctx.show_text(item)  # Draw text

# Function to convert color name to RGB values
def cairo_color(color):
    if color == "black":
        return (0, 0, 0)
    elif color == "green":
        return (0, 1, 0)
    elif color == "pink":
        return (1, 0.75, 0.8)
    elif color == "purple":
        return (0.5, 0, 0.5)
    elif color == "blue":
        return (0, 0, 1)
    else:
        return (0, 0, 0)  # Default to black if color not recognized



class Gene:
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence

    def draw(self, context, y, standard_length):
        # Set up drawing parameters
        context.set_line_width(1)
        context.set_font_size(10)
      

        # Calculate scaling factors
        scale_x = standard_length / len(self.sequence)

        # Draw gene name slightly above the line
        context.move_to(10, y + 5)  # Move slightly above the line
        context.show_text(self.name)

        # Base pair line settings
        context.set_source_rgb(0, 0, 0)  # Black color for the base pair lines
        basepair_height = 10  # Base pair line height

        # Exon line settings
        context.set_source_rgb(0, 0.5, 0)  # Green color for the exon lines
        exon_height = 30  # Exon line height

        # Draw sequence lines
        context.move_to(10, y + 20)
        for i in range(len(self.sequence)):
            if self.sequence[i].isupper():
                # Draw exon lines in green
                context.set_source_rgb(0, 0.5, 0)  # Green color for exon lines
                context.move_to(10 + i * scale_x, y + 20 - exon_height / 2)
                context.line_to(10 + i * scale_x, y + 20 + exon_height / 2)
                context.stroke()
            else:
                # Draw base pair lines in black
                context.set_source_rgb(0, 0, 0)  # Black color for base pair lines
                context.move_to(10 + i * scale_x, y + 20 - basepair_height / 2)
                context.line_to(10 + i * scale_x, y + 20 + basepair_height / 2)
                context.stroke()

class Motif:
    def __init__(self, motif, color):
        self.motif = motif
        self.color = color
    #HELP ME
    #Need this to take the gene.sequence, and capitilize the whole seuqence then proceed 
    def draw(self, context, sequence, x, y, standard_length):
        #Capitlize sequence to find matches 
        sequence = sequence.upper()
        motif_matches = re.finditer(self.motif, sequence)
        context.set_source_rgb(*self.color)  # Set color for drawing the motif
        context.set_line_width(2)  # Set line width for drawing rectangles

        for match in motif_matches:
            start = match.start()
            end = match.end()
            motif_width = end - start
            motif_x = x + start * standard_length / len(sequence)
            motif_y = y + 20 - 15
            context.rectangle(motif_x, motif_y, motif_width * standard_length / len(sequence), 30)
            context.fill()
# make the motifs different colors 
motifs = [
    Motif(r'[CTU]GC[CTU]', (1, 0, 1)),   # pink
    Motif(r'GCAUG', (0.5, 0, 0.5)),  # purple
    Motif(r'CATAG', (0, 0, 1)),  # blue
    Motif(r'[CTU][CTU][CTU][CTU][CTU][CTU][CTU][CTU][CTU][CTU]', (0, 0, 0))  # black
]

# Now call the process_fasta function and create Gene objects
fasta_data = process_fasta(f)
genes = [Gene(name, sequence) for name, sequence in fasta_data.items()]

# Create a Cairo surface and context
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
context = cairo.Context(surface)
context.translate(0,50)


# Set background color to white 
context.set_source_rgb(1, 1, 1)  # White color
context.paint()

# Draw each gene
y_offset = 10
gene_height = 100
for gene in genes:
    gene.draw(context, y_offset, standard_length=400)
    for motif in motifs:
        motif_instance = Motif(motif.motif, motif.color)
        motif_instance.draw(context, sequence=gene.sequence, x=10, y=y_offset, standard_length=400)

    y_offset += gene_height # Adjust the y_offset for the next gene drawing

# Draw legend
legend_x = 375
legend_y= gene_height*len(genes)+20
draw_legend(context,legend_x, legend_y)


# Add header
context.move_to(10, 20)  # Move to the top-left corner for the header
context.set_font_size(12)
context.set_source_rgb(0, 0, 0)  # Black color for the text
context.show_text("Motif Mark - Kyra Lindley")
# Save to PNG
surface.write_to_png(f"{o}.png")

