import pandas as pd
import matplotlib.pyplot as plt
import sys

# Function to load data from a CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to plot the data
def plot_data(cpu_data, dpu_data, output_file='comparison_plot.png'):
    # Create a new figure
    plt.figure(figsize=(10, 6))

    # Set the width of the bars
    bar_width = 0.35

    # Set positions of the bars on the x-axis
    r1 = range(len(cpu_data))
    r2 = [x + bar_width for x in r1]

    # Plot the bars
    plt.bar(r1, cpu_data['Run Time (s)'], color='b', width=bar_width, edgecolor='grey', label='CPU')
    plt.bar(r2, dpu_data['Run Time (s)'], color='r', width=bar_width, edgecolor='grey', label='DPU')

    # Add labels
    plt.xlabel('Query', fontweight='bold')
    plt.ylabel('Run Time (s)', fontweight='bold')
    plt.title('TPC-H Query Run Time Comparison: CPU vs DPU')
    plt.xticks([r + bar_width/2 for r in range(len(cpu_data))], cpu_data['Query'], rotation=45)

    # Add a legend
    plt.legend()

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()

# Main function
def main(cpu_file, dpu_file):
    # Load the data
    cpu_data = load_data(cpu_file)
    dpu_data = load_data(dpu_file)

    # Plot the data
    plot_data(cpu_data, dpu_data)

# Entry point of the script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_comparison.py <cpu_file> <dpu_file>")
        sys.exit(1)
    
    cpu_file = sys.argv[1]
    dpu_file = sys.argv[2]

    main(cpu_file, dpu_file)
