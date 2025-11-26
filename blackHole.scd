// STEP 1: Clean slate
s.freeAll;
OSCdef.freeAll;

// STEP 2: Load TWO samples
(
~backgroundBuffer = Buffer.read(s, "/Users/lindseypietrewicz/Projects/bayesian-beats/StuyTown_72.wav");  // Always playing
~personBuffer = Buffer.read(s, "/Users/lindseypietrewicz/Projects/bayesian-beats/6 11 25 just a lil sumn.mp3");  // Person trigger
)

// STEP 3: Define synths (same as before)
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

SynthDef(\sustainedTone, { |freq=440, amp=0.3|
    var sig;
    sig = SinOsc.ar(freq) * amp;
    Out.ar(0, sig ! 2);
}).add;

SynthDef(\sampleLoop, { |buf, rate=1, amp=0.5|
    var sig;
    sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf) * rate, loop: 1);
    sig = sig * amp;
    Out.ar(0, sig);
}).add;
)

// STEP 4: Start background sample immediately
(
~backgroundSample = Synth(\sampleLoop, [\buf, ~backgroundBuffer, \rate, 1, \amp, 0.3]);
"🎵 Background sample playing continuously".postln;
)

// STEP 5: OSC receivers
(
~personDetected = false;

OSCdef(\heightReceiver, { |msg|
    var height = msg[1];
    var freq = msg[2];

    if(~personDetected, {
        // LOCKED MODE: update sustained tone
        if(~toneSynth.notNil, {
            ~toneSynth.set(\freq, freq);
        });
    }, {
        // RANDOM MODE: play blips
        Synth(\aphexClick, [\freq, freq, \amp, 0.3]);
    });
}, '/height');

// Start sustained tone + PERSON sample when detected
OSCdef(\sampleStart, { |msg|
    var height = msg[1];
    var freq = msg[2];

    ("🎵 PERSON DETECTED: Starting sustained tone + person sample").postln;
    ~personDetected = true;

    // Start sustained tone
    ~toneSynth = Synth(\sustainedTone, [\freq, freq, \amp, 0.3]);

    // Start PERSON sample (background keeps playing)
    ~personSample = Synth(\sampleLoop, [\buf, ~personBuffer, \rate, 1, \amp, 0.5]);
}, '/sample/start');

// Stop sustained tone + person sample when person leaves
OSCdef(\sampleStop, { |msg|
    ("🔄 PERSON LEFT: Stopping tone + person sample, background continues").postln;
    ~personDetected = false;

    // Stop sustained tone
    if(~toneSynth.notNil, {
        ~toneSynth.free;
        ~toneSynth = nil;
    });

    // Stop person sample (background keeps playing!)
    if(~personSample.notNil, {
        ~personSample.free;
        ~personSample = nil;
    });
}, '/sample/stop');

"Ready! Background sample looping + blips. Person detection adds tone + second sample.".postln;
)