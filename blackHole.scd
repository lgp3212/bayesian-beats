s.reboot;
s.boot;

// Drone synth with evolving parameters
(
SynthDef(\bayesianDrone, { |freq=440, amp=0.3, brightness=1000, uncertainty=0.5, gate=1|
    var sig, env, filter_freq;

    env = EnvGen.kr(Env.asr(0.3, 1, 1), gate, doneAction: 2);

    // Multiple oscillators for richness
    sig = Mix([
        SinOsc.ar(freq),
        SinOsc.ar(freq * 1.005),      // Slight detune
        SinOsc.ar(freq * 0.5) * 0.5,   // Sub-octave
        Saw.ar(freq * 2) * 0.2         // Harmonic
    ]);

    // Filter brightness based on confidence
    filter_freq = Lag.kr(brightness, 0.5);  // Smooth transitions
    sig = LPF.ar(sig, filter_freq);

    // Add uncertainty as noise/vibrato
    sig = sig + (PinkNoise.ar(uncertainty * 0.1));
    sig = sig * (1 + (SinOsc.kr(uncertainty * 8) * uncertainty * 0.1));  // Vibrato

    sig = sig * env * amp * 0.2;
    Out.ar(0, sig ! 2);
}).add;
)

// Test the synth
Synth(\bayesianDrone, [\freq, 440, \brightness, 2000, \uncertainty, 0.3]);

(
var drone;

OSCdef(\bayesianUpdate, { |msg|
    var belief, confidence, uncertainty;
    var freq, brightness, noise_amt;

    // Parse message from Python
    belief = msg[1];        // 0-1: estimated probability of heads
    confidence = msg[2];    // 0-1: how confident we are
    uncertainty = msg[3];   // 0-1: standard deviation

    // Map to sonic parameters
    // Belief -> Pitch (200 Hz for tails-biased, 800 Hz for heads-biased)
    freq = 200 + (belief * 600);

    // Confidence -> Filter brightness (dull when uncertain, bright when confident)
    brightness = 500 + (confidence * 3000);

    // Uncertainty -> amount of noise/wobble
    noise_amt = uncertainty * 2;

    ("Belief: " ++ belief.round(0.001) ++
     " | Confidence: " ++ confidence.round(0.001) ++
     " | Uncertainty: " ++ uncertainty.round(0.001)).postln;

    if(drone.isNil, {
        drone = Synth(\bayesianDrone, [
            \freq, freq,
            \brightness, brightness,
            \uncertainty, noise_amt
        ]);
    }, {
        drone.set(
            \freq, freq,
            \brightness, brightness,
            \uncertainty, noise_amt
        );
    });

}, '/bayesian');

"Bayesian listener active! Press Cmd+. to stop".postln;
)
