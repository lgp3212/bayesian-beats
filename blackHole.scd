// Clean slate
s.freeAll;
OSCdef.freeAll;

s.reboot;

// Load background (always playing)
(
~backgroundBuffer = Buffer.read(s, "/Users/lindseypietrewicz/Projects/bayesian-beats/StuyTown_72.wav");
)

// Load folder of samples for person detection
(
// Load all samples 1-40 in randomized order
~sampleOrder = (1..46).scramble;  // Randomize order
~personSamples = ~sampleOrder.collect({ |num|
    Buffer.read(s, "/Users/lindseypietrewicz/Projects/bayesian-beats/" ++ num ++ ".wav");
});

"loaded" + ~personSamples.size + "person samples in randomized order".postln;
)

// Define synths
(
SynthDef(\aphexClick, { |freq=440, amp=0.3|
    var sig, env;
    env = EnvGen.kr(Env.perc(0.001, 0.4, curve: -2), doneAction: 2);
    sig = Mix.fill(5, { |i|
        SinOsc.ar(freq * (1 + (i * 0.003)), Rand(0, 2pi)) * 0.2
    });
    sig = sig + Mix([
        SinOsc.ar(freq * 2.13, 0, 0.3),
        SinOsc.ar(freq * 3.71, 0, 0.2),
        SinOsc.ar(freq * 5.44, 0, 0.1)
    ]);
    sig = LPF.ar(sig, freq * 6);
    sig = sig * env * amp * 0.3;
    Out.ar(0, sig ! 2);
}).add;

SynthDef(\sampleLoop, { |buf, amp=0.5, gate=1|
    var sig, env;
    env = EnvGen.kr(Env.asr(0.1, 1, 0.5), gate, doneAction: 2);
    sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf), loop: 1);
    sig = sig * env * amp;
    Out.ar(0, sig);
}).add;
)

// Start background (always playing)
(
~backgroundSample = Synth(\sampleLoop, [\buf, ~backgroundBuffer, \amp, 0.5]);
"background playing continuously".postln;
)

// OSC receivers
(
~currentPersonSample = nil;

// Height blips - ALWAYS PLAYING
OSCdef(\heightReceiver, { |msg|
    var height = msg[1];
    var freq = msg[2];
    Synth(\aphexClick, [\freq, freq, \amp, 0.4]);
}, '/height');
//
// Switch person sample based on position
OSCdef(\sampleSelect, { |msg|
    var sampleIndex = msg[1].asInteger;
    var newBuffer = ~personSamples[sampleIndex];
    ("switching to person sample" + sampleIndex).postln;

    // Fade out old person sample
    if(~currentPersonSample.notNil, {
        ~currentPersonSample.set(\gate, 0);
    });

    // Start new person sample
    ~currentPersonSample = Synth(\sampleLoop, [\buf, newBuffer, \amp, 0.7]);
}, '/sample/select');

// Person enters - reshuffle samples
OSCdef(\personEnter, {
    "person entered - reshuffling samples!".postln;

    // Reshuffle on each new person
    ~sampleOrder = (1..46).scramble;
    ~personSamples = ~sampleOrder.collect({ |num|
        Buffer.read(s, "/Users/lindseypietrewicz/Projects/bayesian-beats/" ++ num ++ ".wav");
    });
}, '/person/enter');

// Person exits - stop person sample
OSCdef(\personExit, {
    "person left - stopping person sample".postln;

    if(~currentPersonSample.notNil, {
        ~currentPersonSample.set(\gate, 0);
        ~currentPersonSample = nil;
    });
}, '/person/exit');

"ready! background + blips always playing, person samples trigger on detection.".postln;
)