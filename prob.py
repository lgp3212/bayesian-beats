import time
import numpy as np
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 57120)

class BayesianCoin:
    """Bayesian estimation of coin bias using Beta-Binomial conjugate prior"""
    
    def __init__(self, prior_heads=1, prior_tails=1):
        # Beta distribution parameters (start with uniform prior)
        self.alpha = prior_heads  # pseudo-count of heads
        self.beta = prior_tails   # pseudo-count of tails
    
    def update(self, flip_result):
        """Update belief after observing a coin flip"""
        if flip_result == 'H':
            self.alpha += 1
        else:
            self.beta += 1
    
    def get_belief(self):
        """Get current belief about coin bias (probability of heads)"""
        return self.alpha / (self.alpha + self.beta)
    
    def get_confidence(self):
        """Get confidence (inverse of variance)"""
        # Higher alpha + beta = more data = more confidence
        total = self.alpha + self.beta
        # Normalize to 0-1 range
        return min(total / 100, 1.0)
    
    def get_uncertainty(self):
        """Get uncertainty (standard deviation of Beta distribution)"""
        a, b = self.alpha, self.beta
        variance = (a * b) / ((a + b)**2 * (a + b + 1))
        return np.sqrt(variance)

def send_bayesian_state(belief, confidence, uncertainty):
    """Send Bayesian parameters to SuperCollider"""
    client.send_message("/bayesian", [belief, confidence, uncertainty])
    print(f"Belief: {belief:.3f} | Confidence: {confidence:.3f} | Uncertainty: {uncertainty:.3f}")

def simulate_coin_flips(true_bias=0.7, n_flips=100, speed=0.2):
    """
    Simulate learning a coin's bias through Bayesian updating
    
    Args:
        true_bias: actual probability of heads (0-1)
        n_flips: number of flips to observe
        speed: seconds between flips
    """
    coin = BayesianCoin()
    
    print(f"\n=== Simulating coin with TRUE bias = {true_bias} ===")
    print("Watch as our belief converges to the truth!\n")
    
    for i in range(n_flips):
        # Flip the biased coin
        flip = 'H' if np.random.random() < true_bias else 'T'
        
        # Update Bayesian belief
        coin.update(flip)
        
        # Get current state
        belief = coin.get_belief()
        confidence = coin.get_confidence()
        uncertainty = coin.get_uncertainty()
        
        # Send to SuperCollider
        send_bayesian_state(belief, confidence, uncertainty)
        
        # Show flip result
        print(f"Flip {i+1}: {flip}")
        
        time.sleep(speed)
    
    print(f"\n=== Final Estimate: {coin.get_belief():.3f} (True: {true_bias}) ===")

# Example scenarios
if __name__ == "__main__":
    print("\n🎲 BAYESIAN COIN FLIP LEARNING 🎲\n")
    
    # Scenario 1: Fair coin
    print("\n--- SCENARIO 1: Fair Coin ---")
    simulate_coin_flips(true_bias=0.5, n_flips=50, speed=0.15)
    
    time.sleep(2)
    
    # Scenario 2: Biased coin
    print("\n--- SCENARIO 2: Heavily Biased Coin ---")
    simulate_coin_flips(true_bias=0.8, n_flips=50, speed=0.15)
    
    time.sleep(2)
    
    # Scenario 3: Slightly biased (harder to detect)
    print("\n--- SCENARIO 3: Subtly Biased Coin ---")
    simulate_coin_flips(true_bias=0.6, n_flips=100, speed=0.1)