#!/usr/bin/env python3

import numpy as np
import argparse as ap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
from PIL import Image
from sklearn.decomposition import PCA


def rgb_to_hex(color):
    return ("#%02x%02x%02x" % (color[0], color[1], color[2])).upper()


def find_longest_color_axis(colors):
    # Find the color axis with the greatest range
    # Returns two values: an integer specifying the axis (0 for Red, 1 for Green and 2 for Blue),
    # and the median for that axis

    ranges = [np.ptp(colors[:, i]) for i in range(3)]
    best_axis = np.argsort(ranges)[-1]
    return best_axis, np.median(colors[:, best_axis])


def median_cut(colors, num_colors=8):
    # Returns the average colors of (the divisions of) the current region and the number of pixels in each region,
    # if num_colors != 1 then divide the region using median cut
    if num_colors == 1:
        return np.mean(colors, axis=0, dtype=int).reshape(1, 3), [len(colors)]
    best_axis, median = find_longest_color_axis(colors)
    part_1 = colors[colors[:, best_axis] <= median]
    part_2 = colors[colors[:, best_axis] > median]
    mean_1, num_1 = median_cut(part_1, num_colors / 2)
    mean_2, num_2 = median_cut(part_2, num_colors / 2)

    return np.append(mean_1, mean_2, axis=0), num_1 + num_2


def plot_colors(colors):
    figure = plt.figure(figsize=(10, 5))
    ax = figure.add_axes([0, 0, 1, 1])
    for i in range(len(colors)):
        color_hex = rgb_to_hex(colors[i])
        box = mpatch.Rectangle((i, 1), 1, 1, color=color_hex)
        text = ax.text(i + 0.5, 0.5, color_hex, ha='center', fontsize=15)
        ax.add_patch(box)

    plt.xlim(0, len(colors))
    plt.ylim(0, 2)
    ax.axis('off')
    plt.show()


def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input_path', help="Input image file path", nargs='?')
    parser.add_argument('-c', '--color_num', help="Number of colors in the palette, default 8", nargs='?',
                        type=int, default=8, const=8)

    args = parser.parse_args()
    image = Image.open(args.input_path).convert('RGB')
    colors_list = image.getcolors(image.size[0] * image.size[1])
    colors = np.asarray([item[1] for item in colors_list])
    # Use the median cut algorithm to extract a number of candidate colors from an image
    candidates, counts = median_cut(colors, 2 ** np.ceil(np.log2(args.color_num)))
    # Sort the candidate colors by counts and get the top c most popular colors
    counts_sorted = np.argsort(counts)
    palette = candidates[counts_sorted[-1 * args.color_num:]]
    # Apply PCA to the palette
    model = PCA(n_components=1)
    pca_sorted = np.argsort(model.fit_transform(palette).flatten())
    plot_colors(palette[pca_sorted])

if __name__ == "__main__":
    main()
