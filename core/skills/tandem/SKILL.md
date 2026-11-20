---
name: tandem
description: Edit Mike's videos in Tandem, his Mac video editor, through the `tandem` command. Use when a video folder has a .tandem project, or when asked to cut, trim, tighten, place B-roll, add titles, section cards, transitions, captions, stickers, music or sound effects, look at frames, render a review clip, check an edit, do Mike's comments on the timeline, or export a video in Tandem.
---

# Tandem

Tandem is Mike's video editor, built for working in turns with an agent:
you edit the project through the `tandem` command, Mike reviews in the
app, and the timeline shows him exactly what you changed. The guide's
entry point is `docs/AGENTS.md` in the Tandem repo
(`~/dev/me/tandem/docs/AGENTS.md` on Mike's Mac): how editing works, the
command index, and a table of recipes and topics in `docs/agents/` (B-roll,
titles, cards, shorts, captions, sound, review and more). `tandem help
<command>` gives a command's options, and `tandem help <edit command>`
(like `tandem help addTransition`) an edit command's arguments and example.
Read the parts you need before editing.

## Setup

- Run commands from the video folder, or pass `--project <file.tandem>`
  when it holds more than one project.
- `export TANDEM_AUTHOR=claude` (or `--author claude`) so your edits are
  credited to you in the app.

## The loop

Before you change anything, run `tandem status`. If it shows "waiting for
Mike's review: N", stop there, change nothing, and ask him: "There are
still N unreviewed changes in Tandem. Are you sure you want me to
continue?" Carry on only once he says yes. He reviews a round before
asking for the next, and new edits on top of unreviewed ones mix the two
rounds up.

1. **Read.** `tandem status`, `tandem timeline --summary`, then
   `tandem timeline --from 1:20 --to 1:40` for detail. `tandem transcript`
   and `tandem search "<phrase>"` find what's said where. `tandem clips
   --track B-roll --from 1:20 --to 1:40` (or `--media <file>`, `--ids`)
   gives clip IDs; don't dump `timeline --json` to look them up. Tandem
   transcribes camera takes and the voice by itself; for anything else with
   sound (generated B-roll checked for made-up speech, a sound effect or
   music take), `tandem transcribe <id or path>` makes one on-device and,
   with the app closed, waits and prints the word count ("no speech" is an
   answer). Then `tandem transcript <id>`. Background work (transcripts,
   mattes, proxies) is waited for with `tandem wait transcript` (or
   `matte`, `proxy`, plain `tandem wait` for every job), which makes it
   itself when the app is closed. Never start `tandem serve` just to get a
   transcript, and never poll `tandem media` or `tandem status` in a sleep
   loop. Only if Tandem's transcript can't do it (a language its
   engines don't support), local Whisper runs offline:
   `mlx_whisper --model mlx-community/whisper-large-v3-turbo --language en --word-timestamps True -o "$TMPDIR" <file>`
   (one file per call; on long recordings with silences add
   `--condition-on-previous-text False`, or it loops one phrase through
   the quiet).
2. **Edit in labelled batches.** `tandem apply '{"label": "B-roll over the
   config file", "commands": [...]}'` makes one undo step, which Mike reads
   by its label. Pass `--expect <revision>` from the read you based the
   edit on (`tandem status --revision` prints just the number), not one
   taken right before applying, so you never edit over his changes. Tandem
   finding new media doesn't make it stale. On a stale revision, read
   again. Try big batches with `--dry-run` first. Name tracks by name
   (`"trackID": "Music"`) rather than looking up IDs, and give one
   `updateClip` patch to many clips with `clipIDs`. The `--json` shapes are
   in docs/agents/json-output.md.
   For a job that touches many things at once (every caption, every push),
   write a short script against the SDK in the Tandem repo's
   `sdk/` folder instead of hand-building JSON or throwaway Python:
   `~/.bun/bin/bun ~/dev/me/tandem/sdk/run.ts "<name>.tandem" script.ts`
   (or `-e '<code>'`). `t.project()` finds clips, transitions and captions,
   `t.edit(label, commands)` dry-runs then applies one labelled batch against
   the revision you read, and it prints only what the script returns.
   `sdk/README.md` has the API and `sdk/examples/` the caption fix, swooshes
   on pushes and music swells. Small edits are still quicker with
   `tandem apply`.
3. **Look.** `tandem frame <time> -o frame.png` for a still,
   `tandem frames <t1> <t2> ...` (or `--every 5 --from T --to T`) for
   several on one labelled contact sheet, never `frame` in a loop stitched
   with ffmpeg,
   `tandem clip <start> <end>` for a 720p review MP4. Look at what you
   changed instead of trusting the numbers.
   For sound, measure with Tandem, not ffmpeg on a review clip:
   `tandem loudness --from T --to T` prints the mix's momentary and
   short-term loudness every step (`--tracks Music` for one track,
   `--step 0.2` for finer rows), `tandem clip T T --tracks Music
   --audio-only` renders a stem to listen to, and `tandem assets show
   <id>` gives an asset's prompt, licence, loudness and file instead of
   its `meta.json`. If Mike says a gain change plays late or not at all,
   believe him and run `tandem loudness --from T --to T --gains`: it
   checks the render against the gain lanes and says by how much a change
   lands late.
4. **Check.** `tandem check --changed` before you hand back. It renders
   what you changed and finds black frames, flickers, green screen that
   didn't key, white blocks and double jumps (B-roll a few frames off a
   camera cut). A flicker it can fix (a frame jumping in a screen
   recording) comes with a `holdFrame`, and a double jump with the
   `updateClip` that runs the shot out to the cut, in the `tandem apply` on
   its last line. Fix every problem it reports. If you cut the take, also
   run `tandem check --changed --cuts` and the listen check for words
   clipped at the cuts, and judge its cut findings by ear rather than
   applying them blind (see "How Mike likes a take cut"). Its notes are
   judgement calls, but go through each one:
   - soft zooms;
   - dead air: 0.8 s or more of a still picture with nothing said and no
     sound effect or music swell. Cut it, or keep it only if the pause
     earns it (see "Longer gaps where they earn it");
   - page changes with no transition: the screen recording turns to a new
     page and nothing covers it. Push it if it's a page in an explainer or
     slides (see "Page changes in an explainer or slides"); a demo button
     that redraws the page can show up too;
   - low frame rates: the screen recording moving at a few frames a second
     (macOS recorded it slowly). Cover it with the camera full screen, as
     Mike did in the Tandem video, or B-roll, or cut it.
5. **Hand back.** Open the project in the app for Mike with
   `open "<video folder>/<name>.tandem"` (skip it if `tandem status` says
   the app already has it open), rather than asking him to open it. Then
   `tandem handback` with the two to five places he should look at first:
   a stretch of a sweeping change that stands for the rest (one angle pass
   on the Nipunn interview touched 118 clips), the new shot, the thing you
   weren't sure about, each with a few words on what's there (40
   characters at most) and one short line of `note` for the trade-off or
   what to listen for (80 at most; he reads the card at a glance while the
   stretch plays, so the command refuses longer); `question: true` when
   you want his answer, which he leaves as a comment there. Tandem walks him through
   them before the rest of your highlighted changes, so he doesn't read
   times out of the chat. Then tell him in a few lines what you changed
   and why, and that Tandem will walk him through the things to check,
   keeping the chat for what needs a decision. Your edits stay highlighted
   on his timeline until he plays through them or marks them reviewed;
   that's his to do. Next round, `tandem handback` alone says which he
   didn't get to, with any comment he left beside one.

## Mike's comments

While he reviews, Mike leaves comments at moments on the timeline ("cut
the umm here"). When he asks you to look at them, `tandem comments` lists
each one's ID, time and words, with what's said and playing there. Do
each, label the edit with what you did, and put
`{"removeMarker": {"markerID": "<id>"}}` in the same batch so the comment
goes with the fix (or `tandem comments resolve <id>` after). Comments move
with ripple edits, so list them again after one. Leave any you couldn't
do, and say why when you hand back.

Plan the rounds so his watches count: the first hand-back has everything
in, the cut plus B-roll, sound effects and music, never a dialogue-only cut
first. Mike, 2 Nov 2026: "I've gotten more confidence with this tandem
process so we can kind of like get to a later stage quicker." That replaces
the two-stage cut-then-everything plan; Build Your Own Convex took three
comment rounds plus separate listens for the sound effects and the music.

## What Mike changed

Note the revision you hand back at (`tandem status --revision`). Next
round, `tandem diff --since <that revision>` lists what changed since,
clip by clip, grouped by edit with who made it (Mike's edits are by
`user`) and the times and tracks of each. `tandem history` says where
each edit was too, and both last across app restarts. `--since` also
takes an export (`exports/v3.mp4`, read from the `.mp4.tandem` snapshot
beside it) or a backup in `.tandem/backups`. Never diff `timeline --json`
against snapshots in Python.

To bring back clips Mike took out or an earlier round he wants again,
`tandem restore --from <revision or export> --clips <ids>` (or
`--from-time 2:00 --to-time 3:30 --track B-roll`). It's a dry run until
`--apply`, then one labelled undo step. It restores clips only, not
transitions, media or markers.

## How Mike likes a take cut

- **Tighten with `tandem tighten --mike`,** not a script of your own. It
  does the rules below by what each pause follows (0.4 s after a sentence,
  0.12 s after a comma, 0.08 s for a thinking pause mid-sentence, only
  pauses of 0.5 s or more; a join never keeps under 0.03 s after a word or
  0.08 s before one, so mid-sentence comes out at 0.11 s). Keep his
  deliberate beats with
  `--protect <time,...>`, and add `--widen` to open joins a cut left too
  tight back out from the take's own silence (listen to those). Dry run
  first, then `--apply`. It places each cut in the sound of every track
  that plays there, never through sound the transcript doesn't know about
  (someone off mic, an app, a breath, an "um"), cutting the quiet either
  side of it, and lists the pauses it left alone for that, with where the
  sound is: listen to them, and cut a stray "um" with `tandem cut --range`
  if it should go. Bark writes most "um"s as words, so they split pauses
  and stay until they're cut: run `tandem cut --fillers` before tightening.
- **Never place an edge from transcript times,** with or without a margin.
  Mike heard Ian "cut off" 10 times over 4 review rounds on the whiteboard
  interview: "it's quite a common problem that we seem to get wrong,
  correctly placing the cut points" (2026-10-22). Word times are 30 to
  200 ms off the sound, sometimes more: "processed" started 0.2 s early, so
  an edge on it cut off "pro". Don't snap to the quietest point near a
  word's end either: the closure before a final "t" or "k" is a silence
  inside the word, so "extract" became "extrac" and "takes" became "ta".
  A final "s" hardly registers below 4 kHz, so look above it too. And a
  clean-sounding cut in the short gap before a sentence's last word drops
  that word whole: "a couple lies about [time.]" on the Ian cold open.
  A filler taken out of running speech ("do that [because of] to keep")
  leaves no pause at all, so the kept word is chopped mid-sound.
- **Cut with `tandem cut`,** not `cutRanges` built from `search` times.
  `tandem cut "<phrase>"` (or `--range <start>-<end>` for a rough cut,
  `--at` for a phrase said twice) puts both edges of each cut in a real
  pause found in the audio and leaves in a filler with no pause round it,
  which is what sounded right on the Ian video. `--fillers` does that for
  every "um" and "uh" in the transcript (`--from`/`--to`, `--protect`).
  Long false starts are cut
  pause to pause anyway. Dry run first, then `--apply`; it's one undo step.
  Keep `cutRanges` for exact cuts you've checked yourself.
- **Then check every join three ways,** after every batch and across the
  whole timeline, not just the joins you touched. In round 3 Mike still
  found two cut-offs, both at edges placed from transcript times and never
  re-checked. No one check is enough alone.
  - `tandem check --cuts` (with `--changed` or `--from`/`--to`) reads the
    take's own sound either side of every cut. Use it rather than an
    energy script of your own (agents wrote one about 15 times).
  - `tandem check --cuts --listen` renders the voice across each join,
    transcribes it, and flags a kept word at the join that isn't heard or
    is cut short, or a piece of a cut word left in. It replaces the
    hand-rolled Whisper listen, which caught the "pro" cut off "processed"
    that every level check passed.
  - Then read every join's take/heard pair in its output, not just the
    problems, for a sentence that no longer says what he said, and
    `tandem clip` around anything that reads wrong. "a little bit [okay]
    that" passes both the levels and the listen: only reading catches it.
    After Mike signed off the Ian video, reading the joins found six more
    cut-offs ("in the recent | point" for "recent past", a lost "It's", a
    stray "do", "the", "this" and "okay"), and the listen found a seventh
    ("about the re- |" for "requests").
- **When Whisper drops an edge word, the edge is wrong.** Whisper fills in
  a partly cut word, so a word missing entirely is mostly gone. On the Ian
  cold open it dropped "time." from "a couple lies about time."; the agent
  overruled it from the waveform, and Mike: "again its cut off here, Ian
  doesnt say what there are a couple of lies about" (2026-10-22). The cut
  sat in the 55 ms gap just before "time", so all of it went. Move the
  edge until the word comes back.
- **Still confirm `check --cuts` with a listen.** Since 22 Oct 2026 it
  uses the transcript's word times to tell a short gap between words from
  a dip inside one (9 of the Ian video's 290 approved joins flagged, down
  from 25). Its fixes move outward first and never drop a kept word, and
  it flags a dropped first or last word, a fragment of a cut word, and a
  word cut with the filler it runs into ("you have [this, like]"). Its word
  times can still be off (Bark put a 45 ms gap between "problem." and
  "There's" inside "There"), so run `check --cuts --listen`, read every
  join's take/heard pair as above, and `tandem clip` around anything it
  flags or that reads wrong before you act on it.
- **Fixes, in order:** move the edge into a real pause nearby (70 ms or
  more, found in the audio), or into the gap between words just before the
  next cut word, even under 70 ms; put back a removed filler of 2 s or less,
  since a natural "um" beats a chopped word; cut a long false start pause
  to pause, even if a word of the restart comes back; a 50 to 80 ms fade
  only as a last resort.
- **Restored words must finish the thought.** "but it does, you know..."
  put back on its own sounded like Ian being cut off.
- **The raw-mic floor rule is a minimum, not proof.** On the raw mic (not
  the voice-isolated mix, whose near-digital silence breaks it), the kept
  audio must sit within about 9 dB of the room's quiet level (the 8th
  percentile over ±3 s) for 40 ms before each out-point and 40 ms after
  each in-point, and no in-point may open on a 15 to 20 ms blip of the cut
  word's tail. The "time." cut passed it: it sat in the gap before the
  word, and the word went missing whole.
- **Pauses between sentences: 0.4 s.** It's the feel of his old Filmora
  silence detection (0.4 s softening buffer, 0.5 s minimum, 25% volume
  threshold). 0.2 s sounds rushed, as if the sentences are jammed together.
  A cut that removes a retake or a stumble should leave about 0.4 s of real
  silence across the join too, not trim right up to the words.
- **Longer gaps where they earn it:** the end of a paragraph, letting a
  point land, or while something animates on screen (a build finishing, a
  result appearing, a diagram moving). Never cut a pause while a demo
  animation plays, even if he isn't talking. But cut silent holds where
  nothing meaningful happens: clicking around, flicking between pages, the
  Dock popping up, him looking blank before the next section. He flagged
  about 15 of those 1 to 3 s holds as "awkward silence" in Build Your Own
  Convex. Look at the frames: a mean frame difference can't tell an
  animation from a click or a page flick. `tandem check` notes the still,
  silent ones as dead air: Mike only caught one at 3:56 on his final watch,
  and it cost a 13.7 GB re-export. One exception: a celebration line
  ("Congratulations, party time") cuts straight on, even over confetti; he
  doesn't want to sit there silently smiling.
- **No clips under 2 s,** where all it takes is putting back a pause of a
  second or less between sentences. Never bring back a thinking pause or a
  long silence to do it.
- **The ending:** run on about 4 s after the sign-off, with a 3 s fade to
  black that starts about a second after it, and fade the music out with
  it. A 2 s fade at the end of a 5 s run-on "can probably start to fade
  out a bit sooner" (Muse Wonder, 2026-10-13). Run on with the real
  footage: a freeze of his last frame "looks weird" (What I Need video,
  2026-10-09).
- **Mid-sentence pauses:** close his thinking pauses, 0.5 s or longer,
  right up (to about 0.08 s, `--mid 0.08 --mid-min 0.5`, part of `--mike`),
  so a sentence sounds like one thought. Leave
  shorter ones (a breath, a natural pause) as he said them: closing every
  gap of 0.2 s or more made 818 cuts in a 38-minute video, one every 2.8 s,
  and the picture jumped around (Mike, 2026-10-05). The 0.4 s is for
  between sentences. Leave live demo reactions alone.
  On an unscripted screen demo, though, he wants the shorter mid-sentence
  pauses gone too: "There's a heap of these like little micro pauses here
  when I'm mid sentence. Can you get rid of them please?", applied to the
  whole video (Threadbear launch, 2026-11-03, a screen demo with him in the
  corner most of the time). What closed them: quiet gaps of about 0.25 s or
  more mid-sentence down to about 0.13 s, and commas over 0.3 s to 0.15 s,
  leaving breaths under that alone. Bark's full stops and capitals can't be
  trusted in his fast runs ("some of the other really nice little. |
  Productivity features" was the pause he flagged, and a 0.4 s sentence
  keep had left it in), so read each long kept pause in context and decide
  sentence or not yourself. Then let `check --cuts` move any edge that
  clipped a word: edges from a level threshold cut soft word ends.
  That still wasn't enough: on his next full watch he made dozens of 0.2 to
  0.5 s mid-sentence trims himself and wrote "I've had to make lots of
  little minor mid-sentence tightenings. I thought you had all these
  fixed." Measure each gap from the take's own level, speech end to speech
  start at about -42 dB, so a breath counts as part of the pause rather than
  splitting it into two short quiet runs, then cut mid-sentence gaps over
  0.2 s to about 0.1 s, gaps before but/and/so/because over 0.3 s to 0.18 s,
  and sentence gaps over 0.5 s to 0.35 s (his own trims landed there).
  Leave his own joins, the card gaps, the prompter-read cold open and his
  sign-off beat alone, and never plan across a word a cut has half removed.
  `check --cuts` then flags many of the new joins: apply its trim-to-pause
  fixes, but its put-back fixes undo the cut, so only take those where the
  clip's edge sits under 15 dB below speech and let `--listen` judge the
  rest (two cuts came back unnoticed when the whole fix line was applied).
- **Live demos: keep the playback.** When Mike plays the timeline back to
  show the viewer ("let's have a look", "let's listen"), keep that stretch
  even though he's silent: "When I'm explicitly telling the user I'm
  playing something back, don't cut it out just because I'm silent"
  (Tandem video, 2026-10-16; he flagged eight of them). The screen
  recording's system audio track shows it: a cut stretch with Tandem's
  sound in it was playback. Put that audio on its own track under him.
- **Live demos: cut the mistakes, not the material.** Remove silences,
  retakes, false starts and off-camera chat, but keep every point he makes,
  asides and pontificating included, even if it runs long. He trims for
  length himself: "you cut too much stuff out... If there's any section
  that I think that we should cut out, maybe I'll cut it out myself"
  (2026-10-16). When he asks you not to drop anything and to mark possible
  cuts on screen instead, that's about the material too: still cut the
  silences, retakes, false starts and asides to himself ("let me just stop
  that"), and mark only points he makes (a line said twice, a tangent). On
  the Threadbear launch video the first round labelled 47 retakes and false
  starts as possible cuts, and he said: "You should definitely cut out false
  starts and silences and things like that... I meant it's like content"
  (2026-11-03).
- **Live demos: when he leaves the desk,** go full screen on his camera
  from when he says he's going ("Cup of tea time") until he's back at the
  screen, and cover the time away with a time card meme, with its sound,
  rather than a sped-up fast-forward with a "100x" badge: "I don't think we
  need to do the 100x here... can you download that 'some time later'
  meme?" (Tandem video, 2026-10-17). SpongeBob's card says "A Few Moments
  Later"; its sting sat well about 2 dB above his voice. Full screen also
  hides the screen recording while he's away, where macOS only captures on
  change and it dropped to 4 to 7 fps ("why does this part... go like a
  really low frame rate?").
- **Editor's notes:** Mike says them out loud in the take ("editor's note:
  cut that bit"). Read the transcript for them before cutting, and remove
  both the note and what it points at.

## How Mike likes the rest of the edit

From his review comments on the Daytona and Build Your Own Convex videos
(October 2026). The reasons matter more than the numbers.

- **Sync first.** His webcam picture lags his USB mic, so lips and voice
  drift apart (it spoiled the first Daytona upload and the ESLint video). A
  clap test on 2026-10-02 measured about 75 ms (±20 ms). Tandem fixes it
  per file: a camera take's `pictureDelay` makes every clip of it show its
  picture that much later, everywhere, while the sound and cuts stay put.
  Record It takes the lag out as it records (from 2026-10-03; Tandem shows
  those takes "in sync as recorded" and leaves them alone), and older camera
  takes get Tandem's default (0.08 s on his Mac). `tandem sync` shows each
  file's delay; `tandem sync 0.08` sets it on a project made before the
  default. Never slip clips by hand as well, or the delay
  doubles: undo old hand slips (Daytona's +0.09 s) before using it. Don't
  chase exact: the webcam only gives about 22.5 real frames a second (it
  repeats 3 of every 12), so sync wobbles by up to 30 ms whatever you pick.
  Delays land on whole frames of a file with a steady frame rate, and
  `tandem sync` says where.
- **Measure it, on anything filmed: `tandem sync --check`.** Mike spotted the
  James interview's RED wide 55-59 ms out after `tandem sync` had matched its
  sound at confidence 54-59: sound-matching can't see a far camera mic or a
  camera's own offset. The check reads mouths against the voice on a sample of
  each camera file and gives the `tandem sync <delay> --media <id>` fix for any
  clearly a frame or more out; "unclear" means give it a stretch where one
  person talks with `--from` and `--to`. Trust it for that, not for milliseconds. Run the fix it
  prints rather than typing the measured lag. Run it once at the start of an edit;
  `tandem sync <files>` already runs it on the take afterwards.
- **Edits can break sync too.** On the Ian video one `placeMedia` with
  `mode: overwrite` trimmed 60 ms off the next voice clip's head and put
  Ian's voice 60 ms early for 20 minutes. Place or insert instead, and check
  voice-to-picture sync across the whole timeline after every batch.
- **Open on his face.** The first thing on screen is Mike talking to camera,
  and B-roll comes in after his first line. Build Your Own Convex opened on
  24 s of kinetic text, a cartoon and a terminal before his face appeared,
  and a viewer with a TV and stage background said he couldn't tell whether
  the whole video would be voiceover. Mike: "next time ill make sure that I
  show my face early and not launch immediately into broll stuff" (X,
  2026-10-11). Through the first 30 seconds, when people decide whether to
  stay, cut back to him between inserts rather than chaining B-roll.
- **B-roll moves at his pace.** Whip transitions, quick cuts of his words
  and a terminal typing "blazing fast" under his calm voice felt mismatched
  on the same open. Typing in built B-roll goes at a speed you could read
  along to, and transitions stay as calm as his delivery. (Demos where speed
  is the point still play in real time, below.)
- **B-roll starts and ends on sentence boundaries:** the take's cuts, or a
  real pause between words. Never 0.2 s off a cut or mid-word. If less than
  about 1.5 s of camera would show between two B-roll shots, join them. A
  quick flash back to the camera looks like a glitch. Use `holdEdges` when a
  shot runs short. The same goes for a camera cut under B-roll: a shot that
  starts just after one, or ends just before one, shows a few frames and
  jumps again, "a double jump... it's kind of a bit disorientating" (Ian
  video). Within about 0.75 s, extend the B-roll to the cut, holding its
  edge frame. Check every edge against the take's cuts after placing, not
  only against word pauses: placing by pauses alone left 11 shots 1 to 17
  frames off a cut on the batching video, and Mike caught the first 5 s in,
  "it cuts and then like a few frames later it shows the b-roll... quite
  distracting" (2026-10-27). `tandem check` (`--quick` too) now flags both
  as problems, double jumps and camera flashes, each with the `updateClip`
  that runs the shot out to the cut, in the `tandem apply` on its last line.
- **Show what he says.** When he names a thing (a dashboard table, a docs
  page, a claim someone made, a price), put the real thing on screen while
  he says it. A highlight (the $200 free credit) appears when he says it,
  not before. When he mentions a person (Jamie Turner, Convex's CEO), put
  their photo above their name's lower third. A colleague who already has a
  cartoon from an earlier video can pop in as it instead: on the component
  tree Short he asked for Nicolas from the ESLint video "in the corner...
  pop in from the side or something, And make him say hello like he did in
  the other one" (2026-10-26). Reuse the archived green-screen clips and
  voice, keyed to HEVC with alpha (`avconvert --preset
  PresetHEVCHighestQualityWithAlpha`; Tandem couldn't read ffmpeg's
  hevc_videotoolbox file), and land the hello in a pause in his speech. The
  build is in `component-tree-switcher/notes.md`.
- **Show what he says in a live demo too.** In his last review of the
  Tandem video, 9 comments were B-roll asks for things he named, live or on
  camera: Filmora when he first names it, then Filmora itself in use (the
  features, cutting pauses by hand), Voice Type, the YouTube comment and the
  X poll he mentions, his What I Need video, ArtCraft's own app pages, and
  the real mash-up videos: "show actually video of this, not just
  screenshots". A news article is the fallback, not the first pick. Web
  pages go in a browser window with the address showing: "make it look like
  this is actually inside a web browser... so people don't think this is
  actually Windows XP". When he says "I'll put some B-roll on after this",
  put it there. His own past demos count: the Voice Type clip came from his
  February X post.
- **One thing at a time.** A card with the wrong and the right example side
  by side was "a bit too much to read at the same time as listen to what
  I'm saying": put each up on its own as he says it (What I Need video,
  2026-10-09). Text he points at must be readable on a phone; if a real
  page's line is too small ("Mad Scientist @ convex.dev" in his X bio),
  mock that bit up bigger rather than shrinking the page.
- **Section cards: about 3.2 s.** 4 to 4.8 s felt a touch long, 2 s far too
  short. "A touch shorter" means a modest change, not the number he floats.
  To lengthen or shorten a card, open or close time only in the take's gap
  under it (`insertTime` or `rippleDeleteRange`). The cards wipe over the
  edges of speech. On an unlocked Music track, a bed spanning the inserted
  point stretches with it on its own (unlock it first if he's locked it,
  and check it did: one near the end of its file warns), but
  other clips that span it don't grow, so lengthen the card itself. Titles and subtitles have
  to make sense on their own: he swapped "Adding it" for "Setup", and
  "VIBES FIRST, THEN DATA" "doesn't really make any sense".
- **A Convex wipe without a card.** For a section change that doesn't
  need a title (into the outro on the James interview, Mike: "that kind of
  convex colours wipe that goes across"), use the library segment
  `tandem segments insert "Convex wipe" --at <cut - 0.47>`: the card's
  yellow, red and plum bands, each a frame wide, 0.93 s with the card's
  in swish (-5.4 dB). They cover the whole frame from 0.38 to 0.55 s, so
  the cut underneath goes about 0.47 s in, and the frame is clear again
  by 0.85 s: keep that clear of the next word. Source:
  `james-spicy-questions/motion-graphics/src/wipe/ConvexWipe.tsx` (60 fps,
  4K, alpha).
- **Music around cards.** The track plays through the whole card and never
  cuts out under it. A new track starts right after a card ends, at chapter
  breaks only. Swell about +14 dB in the card's speech-free middle with
  `audio.gainDB` keyframes (they set the gain outright, times are
  clip-relative), and back down before he speaks. The whimsical underscore
  is for the intro only. Give the outro its own track.
- **Music beds: one per chapter** (he loved them on Build Your Own Convex).
  Generate a test batch of three first (the cold open, a middle chapter and
  the outro) and get his OK before making the rest. Each bed starts on the
  push or cut into its chapter and fades out over 2 s at the next. Ask the
  generator for the chapter's length plus about 10%: ElevenLabs once came
  back 27 s short, fixed with a beat-matched 10-bar repeat and a 1 s
  dissolve. Level every bed to -45 LUFS, about 25 LU under his voice. Swell
  +6 dB only in pauses of 1.6 s or more with no demo sound effects, and
  +8 dB after the sign-off. Check a swell landed with
  `tandem loudness --from T --to T --tracks Music`. A chill lounge kit sat under demo sound effects
  without fighting them: Rhodes, soft pads, round bass and brushed drums at
  about 85 BPM, with no hi-hats, bells, glockenspiel or marimba.
- **Show options in the chat.** When he's picking between looks, beds or
  layouts, send the stills or preview MP4s as files in the conversation,
  not paths: "How do I view those? Can you just show me them in here?"
  (Ian video).
- **Re-check the music after his own edit pass.** He locks the music track
  so his cuts can't slice it, but a locked track never moves, so his ripple
  cuts leave it behind: on the Tandem video the music ran 2.5 minutes past
  the picture and card 4's swell played 2.5 minutes after the card ("why
  does the music suddenly get loud at the end here?"). After any edits that
  change timing (his or yours, with music locked), check that each card's
  swell sits under its card and the outro ends with the picture. Fix by
  unlocking, laying the beds again or moving them, and locking it again
  (mikecann/tandem#33). On an unlocked music track a ripple cut inside a
  bed now moves its gain keyframes after the cut with the timeline, so
  those swells stay on their cards (a swell inside the cut goes with it),
  and time opened inside a bed stretches it so it still ends with its card;
  `tandem check` notes any swell that's off its card all the same (Threadbear launch video: his deletes left two swells 0.44 s and
  1.4 s late before Tandem did this).
- **Linked sounds:** a card's whooshes are linked to it, so trim either with
  `"includeLinked": false` or you drag the other along.
- **On-screen text moves in and out,** in his words. A question or callout
  slides in and slides off (position keyframes), rather than popping in and
  vanishing. He liked the typewriter reveal with a typing sound. Use his
  exact words, a word or phrase at a time as he says them: "WHAT, NOT HOW"
  over "what to do next, not how to do it" "doesn't align with what I
  actually say". A cliché he's sending up gets a gag: "one weird trick"
  went up word by word with WEIRD wobbling to a wobble sound, and "game
  changer" flashed and shook to the meme DJ air horn (What I Need video,
  2026-10-09). A stadium air horn there was "really annoying": he meant the
  tongue-in-cheek hype horn. ElevenLabs only made that one when the prompt
  named it ("reggae dancehall sound system DJ airhorn sample, the famous
  MLG meme air horn") and spelled out its "ba-da-BAAAAH" rhythm and reverb
  tail; check takes with an audio model before placing one.
- **Typing gets a keyboard sound.** A message typed in an app mock-up gets
  keyboard typing from the first character to the send ("I've done that in
  the past on Filmora projects and it worked quite well"), about 13 LU
  under his voice, near the typewriter callouts' level.
- **Demos where speed is the point** play in real time, with no cuts, so
  viewers can see how fast it really is.
- **Demo sound effects land on the picture.** Snap each sound to the first
  frame its element visibly changes, within 80 ms either way. Steps replayed
  from a script's `setTimeout` drift about 6% against the recording, so time
  them from the frames, not the script. Drop duplicates under 34 ms apart
  (the same frame). A reusable tool for this is being packaged at
  `~/dev/convex/convex-videos/tools/explainer-sfx/`: use it once it's there
  rather than writing your own.
- **Page changes in an explainer or slides** push: a 0.7 s push in its
  default direction on the Screen track only, with the light swoosh
  (`"sound": {"gainDB": -23.3, "offset": -0.39}`), so he stays put in his
  corner ("don't slide me, just slide the screen"). Pushes, not slides:
  "pushes are better than slides" (BYOC v2). It breaks the sections up
  visually. Check the page flip isn't within half the push's length of the
  cut, or a borrowed frame shows the wrong page. For a flip inside a clip,
  freeze 0.35 s either side of it (`freezeFrame` clips) and push between
  them. Find every page change from the screen recording itself, not from
  your cue list: one built from cues missed 10 on Build Your Own Convex,
  and Mike pushed them by hand. `tandem check` lists the ones with no
  transition as page change notes.
- **Picture-in-picture only when he's driving the screen.** When Mike clicks
  and moves the mouse on a recording, he sits in the corner (pipRight) over
  it. When he's reading a script to camera, B-roll goes full screen on the
  B-roll track above him and the edit cuts back to him every so often: no
  corner ("What I need from you" video, 2026-10-09: "this is not a picture
  in picture video"). Give long runs of B-roll a 2 s+ cut-back to him on a
  reaction or bridging line, and tell the B-roll builder which layout it's
  for before it renders, since a corner-safe layout looks off-centre full
  screen. In the left corner (`pipLeft`) he's flipped so he faces the app,
  not off the edge: "when you move me over to the left hand side, can you
  flip me horizontally" (Batching Component, 2026-10-27). `pipLeft` does it;
  if you place him on the left by hand, set `"flipped": true` too.
  Cut back for an aside he acts out, too: "Bruce being one of the
  Mac minis in my house here" wanted his face ("it's the important things
  to focus on my face when I'm saying something like that").
- **Break up long talking-head stretches.** A 10 s opening line in the cold
  open and a 14 s run mid-video both got "break up this big long talking
  head section". Reach for a real screen that carries the example on first.
  A cartoon (`mike-cartoon-broll`) only when it adds a joke or reaction the
  words don't, like the paper avalanche on "so frustrated... so much text".
  Viewers pushed back on generic AI people and on cartoons that just fill a
  gap (October 2026); that skill has the details.
- **Screen recordings fill the frame,** for people watching on a phone:
  one static `zoomToRegion` per page, fitted to the content with a small
  margin, at most 1.5x, and no zoom changes within a page.
- **Split overlays before a ripple edit under them.** B-roll and graphics
  are follow tracks: a ripple cut under one shortens it at its tail, so
  the graphic runs late and loses its ending ("you seem to have cut off the
  end of the motion graphic", Ian video). Blade the overlay at both ends of
  the cut range first. To add time under one, blade it at the join and
  insert a freeze-frame clip (`freezeFrame: true, holdEdges: true`) for
  the added time: extending the left piece replays frames, so the graphic
  jumps back.
- **Sweep for leftovers after any batch of cuts or a rebuild.** Restoring
  cut stretches left 88 clips of 1 to 10 ms (one flickered) and some
  microsecond overlaps that made every later `apply` fail with "Clips X and
  Y overlap". List clips shorter than a frame and adjacent clips that
  overlap at all, and close them up (remove the sliver, pull the next
  clip's start back to it; mikecann/tandem#48 and #49). Fill tiny picture
  gaps, and drop fades on joins that became continuous: they dip mid-word.
- **Sweep for private text before every export.** Run `tandem check
  --privacy` over the whole video, as the last edit before exporting, and
  again with `--format <id>` for each format the project exports (its
  warning names them). It
  reads a frame every half second as export renders it (blurs in place,
  so text scrolling past a fixed blur shows up) and flags emails, phone
  numbers, addresses, booking references, ID, money, crypto, travel, keys,
  "before they go public" notes, lists of names and QR codes, each with a
  `redact` to look at, widen to everything private round it, and apply on
  its own. Then look through every readableText note too, with `tandem
  frames` across it: the rules can't know a plan is internal or a quote is
  someone else's. Don't treat an earlier "leave the blurs off for now" or
  "unblur everything" as a sign-off on what shows, and don't sweep from
  your own markers alone: on the Threadbear launch video four spots from
  earlier markers missed a thread's answer listing Mike's personal and
  work projects, readable at three places, and he caught it himself ("We show the
  projects that I'm working on as well, don't we?"). Re-run it after
  blurring, until it's clean or every flag left is a false alarm you've
  looked at.
- **Before uploading,** watch the start of the export, where sync problems
  show first. The limiter takes about 8 dB off his voice's peaks to reach
  -14 LUFS, and he hears that as artificial, so he asked for -16 after
  Daytona: `updateSettings {"patch": {"loudnessTarget": -16}}`. Set it when
  the edit starts, not at the end: Let's Build It sat at -14 until the
  last round, where the limiter squashed 18 s of it (up to 10 dB off his
  loudest words), and -16 left 4 s. Every export preset masters to the
  project's target and says what it used.

### Editing Case Studies and Reference Examples

Detailed editing blueprints, examples, and production case studies for specific formats (hot-takes cold open, dual voice announcement, Shorts from talks, screen demos, two-person interviews, rapid-fire Q&A) are catalogued in [references/case_studies.md](references/case_studies.md).

## Rules

- Insert at a cut's exact time, read from the clips (`start + duration`),
  not added up from file lengths. Tandem puts an insert within half a frame
  of a cut on the cut, but further in it splits the clip: a take placed as
  long as its camera file (282.045 s), not its screen file (282.1 s), so an
  insert at the sum left a 55 ms sliver of the next clip (the Tandem
  video). Read the warnings: placing a take says which file set its
  length, and an insert that leaves a piece under a quarter second says
  where the clip really starts.
- Build ffmpeg input lists explicitly. In zsh an unquoted `$LIST` isn't
  split, so `-i $f` swallowed the whole list and ffmpeg took the other
  names as outputs and overwrote five B-roll stills with `-y`.
- Tandem's media times are the file's own timestamps, but `ffmpeg -ss`
  counts from the file's start. Add the stream's `start_time` (ffprobe)
  when you analyse a source with ffmpeg: Record It's camera files start at
  0.1 s and its screen files anywhere from 0.33 s to 0.77 s, with the
  sound a little earlier than the picture, enough to clip a word or put a
  redaction on before the QR code shows. Read each stream's own.
- Change the project only through `tandem` (apply, undo, and tools run
  with `--apply`). Never edit `.tandem` files or anything in a `.tandem/`
  folder by hand or with scripts.
- When Apple's voice isolation isn't enough, or you need to pull out or
  keep something else (crowd chatter, room music, one speaker), use SAM
  Audio: `tandem separate <file> "<prompt>"...` (all prompts in one
  command: each run rents a GPU, about US$0.30 to US$0.50), then
  `audio.separation` on the clips with levels chosen for the video. For a
  street interview keep some room under the voice (residual 0.15 to 0.5);
  the voice alone sounds unnatural there. docs/agents/sound.md has it.
- To use a voice cleaned up outside Tandem (a de-reverb, DeepFilterNet),
  swap the file under the clips with `tandem media replace <media id>
  <file>`, not by placing it again. It checks the length matches within
  a frame and makes the loudness and transcript again from the new file;
  the James interview's swap through a bare `updateMedia` path kept the
  old file's loudness, 3 dB out, before Tandem dropped the fingerprint
  itself (30 Oct 2026). Don't `tandem media --refresh` in between.
- Rename a project with `tandem rename [<project>] <new name>`, never `mv`:
  it takes the undo history, journal, review, backups and list icon in
  `.tandem/` with it and keeps its place on the app's project list (Mike
  numbering the Abstract Shorts 01 to 04). It refuses while the project is
  open in the app, so ask Mike to close it first.
- Never run `open tandem://...` or `tandem url`, and never install, quit
  or restart the Tandem app, or launch it for anything except opening the
  project at hand-back. While it restarts, commands wait for it (up to 90 s).
- Mike may be editing at the same time: keep batches small, label them, and
  always pass `--expect`.
- Undo only your own edits: `tandem undo --expect <revision>`, and
  `--count N` to undo several in one go (each undo is a new revision).
- Use what Tandem does natively instead of workarounds:
  - `holdEdges` on a clip to hold its first or last frame, never a still
    exported from it (stills go stale and flicker);
  - `addTransition` for transitions (push, slide, cut slide and wipe bring
    their swoosh);
  - `tandem cards` for section cards;
  - `zoomToRegion` for zooms, keeping 1080p shots at or under 150% on a 4K
    frame;
  - `redact` to hide a QR code, an email or a phone's notifications over a
    stretch, never copies of the clip cropped and linked by hand, and
    `tandem check --privacy` to find what needs it;
  - `placeMedia` with `anchor` (or `tandem assets use --anchor`) for
    stickers;
  - `tandem segments` for Mike's saved intro, outro and like-and-subscribe
    pieces;
  - `tandem join` (a dry run, then `--apply`) to make clips that play the
    file straight through one clip again, after putting a cut back, never a
    lift and trim by hand.
- New files you make (B-roll, sound effects, stills) go in the video
  folder, then `tandem media --refresh` adds them. Temporary files
  (ProRes masters before converting to HEVC with alpha, test renders) go
  in `$TMPDIR` or the scratchpad, never the video folder: Tandem adds
  anything that appears there. A file no clip uses leaves the project
  quietly when it's deleted, but it churns the media list meanwhile. A
  subfolder with a `package.json` (`motion-graphics/`) only counts its
  `out/`, so a Remotion project's `public/` and `src/` are safe to write.
- Find music, sound effects, stickers and icons with `tandem assets search`
  and add them with `tandem assets use <id> --at <time>`. Mike's shared
  library is `~/Movies/Tandem Library`.
- To export, `tandem export` writes the finished video (4K for a 4K frame)
  into `exports/`, once Mike has reviewed every agent edit. While any wait
  for him (`tandem status` lists them), it refuses and names the latest: on the
  Threadbear launch video an agent exported four times while its privacy
  blurs still waited, and Mike said "I didn't actually verify the blur
  looks good. I need to verify all that before you export it." Hand back
  and let him review in Tandem, then export. `--preset review` still
  exports, with a warning, for a copy to watch; `--unreviewed` makes a
  check export of a final preset (a 4K look at a zoom, say), never one to
  publish or send.
