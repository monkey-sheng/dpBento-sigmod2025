import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Read the CSV file
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    return df

# Plot latency distributions for different request distributions
def plot_latency(df):
    latencies = ['latency(us)', '95latency(us)', '99latency(us)']
    for latency in latencies:
        plt.figure(figsize=(10, 6))
        sns.barplot(x='requestdistribution', y=latency, hue='operationcount', data=df)
        plt.title(f'{latency} for Different Request Distributions')
        plt.ylabel(latency)
        plt.xlabel('Request Distribution')
        plt.legend(title='Operation Count')
        # plt.tight_layout()
        plt.show()

# Plot throughput comparison
def plot_throughput(df):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='requestdistribution', y='throughput(ops/sec)', hue='operationcount', data=df)
    plt.title('Throughput (ops/sec) Comparison for Different Request Distributions')
    plt.ylabel('Throughput (ops/sec)')
    plt.xlabel('Request Distribution')
    plt.legend(title='Operation Count')
    plt.tight_layout()
    plt.show()

# Plot average latencies for different operations
def plot_avg_latency(df):
    operations = ['READ', 'UPDATE', 'INSERT', 'SCAN']
    
    for operation in operations:
        plt.figure(figsize=(10, 6))
        df['avg_' + operation] = df['latency(us)'].apply(lambda x: eval(x).get(operation, None))
        sns.lineplot(x='operationcount', y='avg_' + operation, hue='requestdistribution', data=df)
        plt.title(f'Average {operation} Latency vs Operation Count')
        plt.ylabel(f'Average {operation} Latency (us)')
        plt.xlabel('Operation Count')
        plt.legend(title='Request Distribution')
        plt.tight_layout()
        plt.show()

def main():
    print(os.getcwd())
    csv_file = 'report.csv'  # Replace with your CSV file path
    df = load_data(csv_file)
    
    plot_latency(df)  # Plot latency distribution
    plot_throughput(df)  # Plot throughput comparison
    plot_avg_latency(df)  # Plot average latency for READ, UPDATE, INSERT, SCAN operations

if __name__ == "__main__":
    main()
