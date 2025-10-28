import time
import numpy as np
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 57120)

class BayesianCoin:
    """Bayesian estimation of coin bias using Beta-Binomial conjugate prior"""
    
    def __init__(self, prior_heads=1, prior_tails=1):
        # beta distribution parameters (start with uniform prior)
        self.alpha = prior_heads  # pseudo-count of heads
        self.beta = prior_tails   # pseudo-count of tails
    
    def update(self, flip_result):
        if flip_result == 'H':
            self.alpha += 1
        else:
            self.beta += 1
    
    def get_belief(self):
        return self.alpha / (self.alpha + self.beta)
    
    def get_confidence(self):
        # higher alpha + beta = more data = more confidence
        total = self.alpha + self.beta
        # normalize
        return min(total / 100, 1.0)
    
    def get_uncertainty(self):
        a, b = self.alpha, self.beta
        variance = (a * b) / ((a + b)**2 * (a + b + 1))
        return np.sqrt(variance)

def send_bayesian_state(belief, confidence, uncertainty):
    client.send_message("/bayesian", [belief, confidence, uncertainty])
    print(f"Belief: {belief:.3f} | Confidence: {confidence:.3f} | Uncertainty: {uncertainty:.3f}")

def simulate_coin_flips(true_bias=0.7, n_flips=100, speed=0.2):
    coin = BayesianCoin()
    
    print(f"\nsimulating coin with true bias = {true_bias}")
    
    for i in range(n_flips):
        # flip coin
        flip = 'H' if np.random.random() < true_bias else 'T'
        
        # update bayesian belief
        coin.update(flip)
        
        # get current state
        belief = coin.get_belief()
        confidence = coin.get_confidence()
        uncertainty = coin.get_uncertainty()
        
        # send to sc
        send_bayesian_state(belief, confidence, uncertainty)
        
        # show flip result
        print(f"Flip {i+1}: {flip}")
        
        time.sleep(speed)
    
    print(f"\n=== Final Estimate: {coin.get_belief():.3f} (True: {true_bias}) ===")

# examples
if __name__ == "__main__":
    print("\nbayesian coin flip learning\n")
    
    # fair coin
    print("\n--- scenario 1: Fair Coin ---")
    simulate_coin_flips(true_bias=0.5, n_flips=50, speed=0.15)
    
    time.sleep(2)
    
    # biased coin
    print("\n--- scenario 2: Heavily Biased Coin ---")
    simulate_coin_flips(true_bias=0.8, n_flips=50, speed=0.15)
    
    time.sleep(2)
    
    # slightly biased (harder to detect)
    print("\n--- scenario 3: Subtly Biased Coin ---")
    simulate_coin_flips(true_bias=0.6, n_flips=100, speed=0.1)