import pandas as pd
import numpy as np
import time
from pythonosc import udp_client

# Initialize OSC client (same port as your blackHole.scd)
client = udp_client.SimpleUDPClient("127.0.0.1", 57120)

# Load the height data
df = pd.read_csv("NCD_RisC_Lancet_2020_height_child_adolescent_global.csv")

print("Height Data Sonification")
print()
print(f"Dataset loaded: {len(df)} records")
print(f"Columns: {df.columns.tolist()}\n")

def height_to_frequency(height_cm, min_height=100, max_height=200):
    """
    map height (cm) to frequency (Hz)
    taller = higher frequency
    """
    # normalize height
    normalized = (height_cm - min_height) / (max_height - min_height)
    normalized = np.clip(normalized, 0, 1)  # Keep in bounds
    
    freq = 200 * (2 ** (normalized * 4)) 
    return freq

def sample_and_sonify(n_samples=1, delay=1.0):
    height_column = 'Mean height' 
    se_col = 'Mean height standard error'

    heights = df[height_column].sample(n_samples).values 
    sample_height = np.mean(heights) # random sample from dataset 
    ses = df[se_col].sample(n_samples).values 
    sample_se = np.mean(ses)
    freq = height_to_frequency(sample_height)

    print(f"Sample {i+1}: Height = {sample_height:.1f} cm → Frequency = {freq:.1f} Hz")
    
    client.send_message("/height", [float(sample_height), float(freq)])
    time.sleep(sample_se)  # let note play, also want to parameterize this?
    
    if i < n_samples - 1:
        time.sleep(delay - 0.5)

if __name__ == "__main__":
    # checking
    print("first few rows of data:")
    print(df.head())
    print("\ncolumn names:")
    print(df.columns.tolist())
    print()
    
    print("\naampling random heights...\n")
    for i in range(0,75):
        sample_and_sonify(n_samples=1)
    for i in range(0,75):
        sample_and_sonify(n_samples=1)
        sample_and_sonify(n_samples=2)
    for i in range (2, 1000, 5):
        print(f"sample size: {i}")
        for k in range(0,5):
            sample_and_sonify(n_samples=i)