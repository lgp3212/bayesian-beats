s.boot;

(
SynthDef(\probTone, { |freq=440, amp=0.3, dur=0.5|
    var sig, env;
    env = EnvGen.kr(Env.perc(0.01, dur), doneAction: 2);
    sig = SinOsc.ar(freq) * env * amp;
    Out.ar(0, sig ! 2);  // stereo output
}).add;
)

Synth(\probTone, [\freq, 440, \amp, 0.3, \dur, 1]);

(
OSCdef(\pythonProb, { |msg|
    var prob, freq, amp, dur;

    prob = msg[1];  // First argument from Python

    // Map probability to audio parameters
    freq = 200 + (prob * 800);      // 200-1000 Hz
    amp = 0.2 + (prob * 0.5);       // 0.2-0.7 amplitude
    dur = 0.3 + (prob * 0.7);       // 0.3-1.0 seconds

    // Print what we received
    ("Received prob: " ++ prob ++ " -> freq: " ++ freq ++ "Hz").postln;

    // Play the synth
    Synth(\probTone, [\freq, freq, \amp, amp, \dur, dur]);

}, '/probability');  // Listen for messages to '/probability'
)