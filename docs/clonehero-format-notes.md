# Clone Hero format notes

Research date: 2026-09-10. No exporter or in-game scan has been run.

The official [custom-song guide](https://wiki.clonehero.net/books/clone-hero-manual/page/adding-custom-songs)
requires a per-song folder with notes.mid or notes.chart, audio and song.ini,
followed by an in-game song scan.

## MIDI conventions

The community [drum format reference](https://thenathannator.github.io/GuitarGame_ChartFormats/Chart-File-Formats/mid-format/Tracks/Drums/)
documents PART DRUMS, Expert notes 96 kick, 97 red, 98 yellow, 99 blue, 100 green.
In Pro mode yellow/blue/green are cymbals unless tom markers 110/111/112 overlap.
Red is a pad. Same-color simultaneous pad and cymbal cannot be represented.
Set pro_drums=true and five_lane_drums=false in song.ini for explicit intent.
Note 95 is optional Expert+ kick. PART DRUMS_2X is a separate RBN convention.
Dynamics require ENABLE_CHART_DYNAMICS text and velocities 1 (ghost), 127 (accent).
Roll markers 126/127 describe one-/two-lane roll phrases; kicks are excluded.
These are format conventions; support of advanced mechanics in the user's Clone
Hero version must be validated in later phases.

For Pro reference interpretation, resolve Expert mix events as well as tom
markers. The flag `d` in `[mix 3 drums2d]` swaps stored red into yellow cymbal
and stored yellow (including tom) into red. The next Expert mix resets this
state; `dnoflip` does not swap notes. Other difficulties have separate state.
The same mix commands can appear as local .chart events, with spaces/underscores
and optional brackets. Keep stored note numbers separate from resolved Pro groups.
Crawling exposed this case; see [linkin-park-hihat.md](linkin-park-hihat.md).

## Timing and serialization decision

Use a type-1 MIDI with a separate tempo track, PART DRUMS and end-of-track events.
The [technical reference](https://thenathannator.github.io/GuitarGame_ChartFormats/Chart-File-Formats/mid-format/Technical-Details/)
describes tick division, delta times, MIDI tracks and meta events.
Choose PPQN=480 initially, explicit tempo and time signature at tick zero. Encode
tempo in microseconds per quarter note, meter denominator as its power of two.
For a constant segment: ticks = seconds * PPQN * 1,000,000 / tempo_us.
For tempo changes, integrate each segment and accumulate absolute ticks before
forming nonnegative delta times. Preserve original seconds outside the serializer.
At 120 BPM/480 PPQN, nearest-tick error is at most about 0.521 ms. This reference
tempo is a serialization choice, not a detected musical tempo. Do not use song.ini
delay for primary synchronization. Future tests must cover changing tempo/meter.

## .chart comparison

The [.chart reference](https://thenathannator.github.io/GuitarGame_ChartFormats/Chart-File-Formats/chart-format/Tracks/Drums/)
uses ExpertDrums, kick 0 and colored lanes 1–4; cymbals use flags 66–68. Its
readable text helps review but must not be confused with MIDI tom markers.
MIDI is the planned first output; .chart stays a reference/debug alternative.

The [midi2clonehero reference](https://github.com/apvilkko/midi2clonehero)
converts GM percussion to .chart. Its hi-hat mapping and configurable blue/green
cymbal policy are useful references; its type-0 MIDI input expectation and opinionated
transformations make it unsuitable as the canonical internal representation.
