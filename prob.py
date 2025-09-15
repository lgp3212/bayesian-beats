import time
import numpy as np
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 57120)  # Note: 57120 for SuperCollider

def send_probability(prob_value):
    """Send a probability value to SuperCollider"""
    client.send_message("/probability", [prob_value])

print("Test 1: Single probability")
send_probability(0.7)
time.sleep(2)

print("\nTest 2: Probability sequence")
test_probs = [0.1, 0.3, 0.5, 0.7, 0.9]

for prob in test_probs:
    send_probability(prob)
    time.sleep(1.5)

print("\nTest 3: Random probability stream")
for i in range(5):
    prob = np.random.random()
    send_probability(prob)
    time.sleep(1)

print("Test complete")