import time
import numpy as np
from pythonosc import udp_client

# Initialize OSC client
client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
np.random.seed(42)

print("🎵 Probability Sonification System Ready!")
print("=" * 50)

def sonify_probability(prob_value, duration=0.8, verbose=True): 
    freq = 200 + (prob_value * 1200)  # 200Hz to 1400Hz range
    amp = 0.3 + (prob_value * 0.5)    # 0.3 to 0.8 amplitude
    tone_duration = 0.2 + (prob_value * 0.6)  # 0.2 to 0.8 seconds
    
    if verbose:
        print(f"Prob: {prob_value:.3f} → Freq: {freq:.0f}Hz, Amp: {amp:.2f}, Dur: {tone_duration:.1f}s")

    synth_id = int(time.time() * 1000) % 10000

    client.send_message("/s_new", ["default", synth_id, 0, 0, "freq", freq, "amp", amp])
    time.sleep(tone_duration)
    client.send_message("/n_free", [synth_id])
    time.sleep(0.1)
    
    return freq, amp, tone_duration

def test_probability_range():
    test_values = [0.1, 0.25, 0.5, 0.75, 0.9]
    
    for prob in test_values:
        sonify_probability(prob)
        time.sleep(0.3)  # pause between tests


def stream_probabilities(n_samples=10, delay=0.8):
    
    try:
        for i in range(n_samples):
            if i < 3:
                prob = np.random.beta(2, 8)
            elif i < 7:
                prob = np.random.beta(6, 3)
            else:
                prob = np.random.random()
            
            print(f"Sample {i+1:2d}: ", end="")
            sonify_probability(prob, verbose=True)
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n⏹️  Streaming stopped by user")

# advanced sonification with multiple parameters
def advanced_sonify(prob_value, certainty=None, category=None):
    base_freq = 200 + (prob_value * 800)

    if certainty is not None:
        if certainty > 0.7:
            freq = base_freq  
        else:
            freq = base_freq * (1 + (1 - certainty) * 0.2) 
    else:
        freq = base_freq
        certainty = prob_value 
    
    amp = 0.2 + (prob_value * 0.6)

    duration = 0.3 + (certainty * 0.5)
    
    synth_id = int(time.time() * 1000) % 10000
    client.send_message("/s_new", ["default", synth_id, 0, 0, "freq", freq, "amp", amp])
    time.sleep(duration)
    client.send_message("/n_free", [synth_id])
    time.sleep(0.1)

def probability_monitor(duration=30):
    
    start_time = time.time()
    sample_count = 0
    
    try:
        while (time.time() - start_time) < duration:
            t = time.time() - start_time
            
            # create a probability that varies over time
            base_prob = 0.5 + 0.3 * np.sin(t * 0.5)  # slow oscillation
            noise = np.random.normal(0, 0.1)         # add some noise
            prob = np.clip(base_prob + noise, 0, 1)  
            
            sample_count += 1
            print(f"T+{t:5.1f}s: ", end="")
            sonify_probability(prob, duration=0.3, verbose=True)
            
            time.sleep(0.5)  
            
    except KeyboardInterrupt:
        print(f"Monitor stopped. Processed {sample_count} samples.")


probability_monitor(30)