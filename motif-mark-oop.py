#!/usr/bin/env python
import argparse
import re
import cairo 
import os


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fasta", help="Input fasta", required=True)
    
    parser.add_argument("-m",'--motifs',help="Input motif file", required=True)
    return parser.parse_args()

args = get_args()
f = args.fasta

m = args.motifs
################
# File handing #
################

def read_motifs_from_file(m):
    '''This function takes the given list of motifs, then uses REGEX for ambiguity {Y; any pyrimidine}, then stores the given motif as a key;regex translation as the value'''
    motifs = {}
    with open(m,'r') as file:
        for line in file:
            line = line.strip()
            # Create regex pattern with 'Y' replaced by character sets for 'C', 'T', and 'U'
            regex_pattern = re.sub(r'Y', '[CTU]', line)
            motifs[line] = regex_pattern
    return motifs

def process_fasta(file:str):
    '''This function process a FASTA. First turning the FASTA into oneline so header and sequence are on same line, one line per gene. Finally, it uses regex to grab the gene name and its seuqence. The gene is the key and the sequence is the value in the gene_dict. This is used for further analysis'''
    gene_dict = {}  
    with open(file, "r") as fh:
        current_gene = None
        sequence = ''
        for line in fh:
            line = line.strip()
            if line.startswith('>'):  # If it's a header line
                if current_gene is not None:  # If we have already processed a gene
                    gene_dict[current_gene] = sequence  # Store the sequence in the dictionary
                    sequence = ''  # Reset sequence for the next gene
                match = re.match(r'^>(\S+)', line)  # Extract gene name using regex
                if match:
                    current_gene = match.group(1)
            else:
                sequence += line  # Concatenate sequence lines
        if current_gene is not None:  # Store the last gene sequence
            gene_dict[current_gene] = sequence
    return gene_dict

####################
# Legened Functions#
####################

def draw_legend(ctx, x, y):
    ''' This function draws a legend box with specified items and colors onto a Cairo context. The parameters for this function are the context of the Cairo surface, the x coordinated and y coordinate. '''
    # Define legend items and their corresponding colors
    legend_items = ["gene", "exon", "ygcy", "GUATG", "catag", "YYYYYYYYYY"]
    legend_colors = ["black", "green", "pink", "purple", "blue", "orange"]
    
    # Set font properties
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    
    # Calculate the total height of the legend box
    total_legend_height = len(legend_items) * 15 + 10
    
    # Draw legend box
    ctx.set_source_rgb(0, 0, 0)  # Black color for box outline
    ctx.rectangle(x, y, 100, total_legend_height)  # Adjust width as needed
    ctx.stroke()
    
    # Draw legend items
    for i, item in enumerate(legend_items):
        ctx.set_source_rgb(*cairo_color(legend_colors[i]))  # Set color
        ctx.rectangle(x + 5, y + 5 + i * 15, 10, 10)  # Draw colored rectangle
        ctx.fill()
        ctx.set_source_rgb(0, 0, 0)  # Black color for text
        ctx.move_to(x + 20, y + 10 + i * 15)  # Position text
        ctx.show_text(item)  # Draw text

def cairo_color(color):
    '''Function to convert color name to RGB values'''
    if color == "orange":
        return (1, 0.5, 0)
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

###############
# OOP Classes #
###############
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

        # Draw gene name at the bottom of the gene drawing
        context.move_to(10, y + 40)  # Move to the bottom of the gene drawing
        context.show_text(self.name)

class Motif:
    def __init__(self, motif, color):
        self.motif = motif
        self.color = color
    
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
    Motif(r'GCATG', (0.5, 0, 0.5)),  # purple
    Motif(r'CATAG', (0, 0, 1)),  # blue
    Motif(r'[CTU][CTU][CTU][CTU][CTU][CTU][CTU][CTU][CTU][CTU]', (1, 0.5, 0))  # orange
    ]

#############
# Main code #
#############
def main():
    '''This is the main code of the motif-mark-oop.py'''
    file_prefix = os.path.splitext(os.path.basename(f))[0]
    fasta_data = process_fasta(f)
    genes = [Gene(name, sequence) for name, sequence in fasta_data.items()]

    total_gene_height = len(genes) * 100

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, total_gene_height + 500)
    context = cairo.Context(surface)
    context.translate(0, 50)

    context.set_source_rgb(1, 1, 1)  # White color
    context.paint()

    y_offset = 40
    gene_height = 100
    for gene in genes:
        gene.draw(context, y_offset, standard_length=400)
        for motif in motifs:
            motif_instance = Motif(motif.motif, motif.color)
            motif_instance.draw(context, sequence=gene.sequence, x=10, y=y_offset, standard_length=400)

        y_offset += gene_height

    legend_x = 375
    legend_y = gene_height * len(genes) + 20
    draw_legend(context, legend_x, legend_y)

    context.move_to(5, 5)
    context.set_font_size(10)
    context.set_source_rgb(0, 0, 0)  # Black color for the text
    context.show_text("Motif Mark - Kyra Lindley")

    surface.write_to_png(f"{file_prefix}.png")

if __name__ == "__main__":
    main()

