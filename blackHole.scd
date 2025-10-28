s.boot;

OSCdef.freeAll;

// Define the height synth
(
SynthDef(\heightTone, { |freq=220, amp=0.3, gate=1|
    var sig, env;
    env = EnvGen.kr(Env.asr(0.01, 1, 0.1), gate, doneAction: 2);
    sig = SinOsc.ar(freq);
    sig = sig * env * amp;
    Out.ar(0, sig ! 2);
}).add;
)

(
SynthDef(\heightGlitch6, { |freq=440, amp=0.3|
    var sig, env, mod;
    env = EnvGen.kr(Env.perc(0.001, 0.1), doneAction: 2);

    // FM synthesis with high modulation index
    mod = SinOsc.ar(freq * 2.3) * freq * 3;
    sig = SinOsc.ar(freq + mod);

    // Harsh distortion
    sig = (sig * 5).tanh;

    sig = sig * env * amp * 0.3;
    Out.ar(0, sig ! 2);
}).add;
)

(
SynthDef(\aphexBleep, { |freq=440, amp=0.3|
    var sig, env, click;

    // Super fast attack for that digital click
    env = EnvGen.kr(Env.perc(0.001, 0.05, curve: -8), doneAction: 2);

    // Layered oscillators with slight FM
    sig = Mix([
        SinOsc.ar(freq),
        SinOsc.ar(freq * 2.01) * 0.4,  // Detuned harmonic
        Pulse.ar(freq, 0.3) * 0.3,      // Add some edge
    ]);

    // Add click at the start
    click = Decay.ar(Impulse.ar(0), 0.001) * PinkNoise.ar(0.4);
    sig = sig + click;

    // Tight bandpass for that focused bleep quality
    sig = BPF.ar(sig, freq * 2, 0.5);

    sig = sig * env * amp * 0.6;
    Out.ar(0, sig ! 2);
}).add;
)

(
SynthDef(\aphexCrystal, { |freq=440, amp=0.3|
    var sig, env;

    env = EnvGen.kr(Env.perc(0.001, 0.4, curve: -2), doneAction: 2);

    // Multiple slightly detuned sines for shimmer
    sig = Mix.fill(5, { |i|
        SinOsc.ar(freq * (1 + (i * 0.003)), Rand(0, 2pi)) * 0.2
    });

    // Add inharmonic partials for bell-like quality
    sig = sig + Mix([
        SinOsc.ar(freq * 2.13, 0, 0.3),
        SinOsc.ar(freq * 3.71, 0, 0.2),
        SinOsc.ar(freq * 5.44, 0, 0.1)
    ]);

    // Gentle filtering
    sig = LPF.ar(sig, freq * 6);

    sig = sig * env * amp * 0.3;
    Out.ar(0, sig ! 2);
}).add;
)

(
OSCdef(\heightListener, { |msg|
    var height, freq;
    height = msg[1];
    freq = msg[2];

    ("Height: " ++ height.round(0.1) ++ " cm → Freq: " ++ freq.round(0.1) ++ " Hz").postln;

    Synth(\aphexClick, [\freq, freq, \amp, 0.3]);  // Using glitch synth!

}, '/height');
"Glitch listener active!".postln;
)

Synth(\heightGlitch1, [\freq, 440, \amp, 0.3]);

OSCFunc.trace(true);

n = NetAddr("127.0.0.1", 57120);
n.sendMsg('/height', 150.0, 600.0);