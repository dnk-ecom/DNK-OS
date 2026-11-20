### A hot-takes cold open

The best moments cut together before the first line, to draw people in.
Plain bites butted together "isn't very exciting": "The whole point of the
montage open is supposed to have like text on the screen and you know it
kind of cuts quickly with sound effects and music and all that kind of
stuff" (Ian video, 2026-10-21). The full build is in
`convex-videos/ian-whiteboard-sept-2026/cold-open.md`.

- **Build it last,** once the rest of the video is right: "leave that
  montage until the end... focus on just getting the video right first".
- **About 30 s, six to eight bites,** alternating speakers and angles.
  The model is the editor-made open of the earlier Ian video, "What is the
  Convex WorkPool?" (youtube.com/watch?v=DQZCQ-Y1ZBM): "picked out the
  really spicy, interesting parts... quick cuts and added text over the
  top". The Ian open ran 36 s with seven bites, and he kept them all.
- **Pick the spicy bites, each a finished thought.** Place and
  listen-check every bite edge as in "How Mike likes a take cut": the last
  cut-off Mike heard on the Ian video was the end of a bite.
- **Room between bites:** 0.3 to 0.5 s of real room tone at every join.
  Butting bites about 0.1 s apart made the lines run together. Widen each
  bite into its own pauses, and where a take has none, run the picture on
  silently for 0.2 to 0.3 s.
- **A reaction beat after each punchline:** 0.5 to 0.8 s of the listener
  reacting silently (taken from while they listen), so the text can be
  read before the next bite.
- **A push with a swoosh between bites,** 0.5 s, so they read as separate
  moments: "you have like a sound effect or a swipe... to indicate that
  it's a different topic... Otherwise, you're kind of almost faking what
  the video is about" (2026-10-22). Not a coloured swipe graphic: "just do
  like a push and the kind of swipe sound". Where the shots either side
  sit on different video tracks (close-up over wide), change one angle so
  the push stays on one track.
- **Kinetic text of each punchline, in their exact words,** in Convex
  colours with the highlighter look: white bold text with a soft shadow,
  the punchline on a rough yellow felt-tip swipe (red for the "wrong"
  lines). No solid boxes behind it: he disliked dark boxes and the VS Code
  palette ("use the convex colours"). Show him a few looks as stills over
  real frames. The text has no exit fade: a matching push on Graphics
  carries it off with the picture. `motion-graphics` has the build.
- **Dramatic music:** "dramatic is best for an opening montage like this
  to make it sound exciting". Generate three or four beds and show each as
  a preview MP4 with the montage, fitted so its big moments land on cuts
  (a start offset, or whole bars repeated, with the loop length found by
  self-similarity) and its final hit on the cut into the first line. His
  pick, a dark electronic cue, sat about 8 LU under the voices, far above a
  chapter bed, with a riser into an impact on the last cut.

### A second voice: the Let's Build It announcement (with his son Josh)

A personal video for X and YouTube (October 2026): no Convex branding,
transitions or swipes. Export `youtube1080` for X and `youtube4k` for
YouTube.

- **Lift the quieter voice, not Mike.** Each of Josh's lines gets one gain
  that brings it up to Mike's level (up to +24 dB), ramping in over about
  0.35 s before and out over 0.5 s after, and stopping short of anything
  that isn't Josh (a breath, Mike's next word). Mike stays at one steady
  level: levelling his words up and down was "quite distracting". Where he
  turns from the mic to talk to Josh, lift that whole stretch by one amount
  (+6 dB), and give a phrase that trails off a further 10 dB its own extra
  lift. Keep dips on his loud words small: he took a -9 dB dip on a shouted
  "Cool!" back to about -3.
- **Check each word, not just the line.** A child's word can fade at its
  end inside a lift: the "-tion" of Josh's "question" sat 10 dB under its
  start, so Mike only heard the "Q". Pitch alone mistakes who's talking (a
  120 Hz "Yeah?" was Mike, and Josh's "Dad?" came a second before the line
  it belonged to), so check the picture and where Mike put his comment.
- **Their lines pop up as text, word by word as they say them.** One text
  clip per step holding the words so far, with the left edge fixed so the
  line grows to the right: measure each prefix's width with `tandem frame`
  in a scratch project and set each clip's x. The first step lasts the
  0.25 s pop and later ones at least 0.12 s, so merge words said faster.
  The `words` field only highlights the spoken word, so it can't do this.
  No full word captions on an announcement video: "I don't think people do
  them in announcement videos".
- **iPad recordings show whole,** over a blurred, darkened copy of
  themselves on the track below (scale 1.3, blur 60, exposure -1). Filling
  16:9 crops the app's edges, and he called that cut off.
- **Keep his mic in the corner cutout.** The cutout can drop the desk mic,
  so the screen shows through it. An include repair mask over the mic
  (`video.cutout.repairMasks`, a rounded rectangle in fractions of the
  source frame) fixes every corner clip of the take; check frames across
  them for holes. Slide the corner off when he turns back to stare at the
  camera mid-demo: "a bit weird".
- **A website he names shows as its live homepage,** scrolling slowly in a
  plain browser window (traffic lights, an address bar with the domain)
  over a blurred copy of the page. Playwright captures one frame per scroll
  position and then composes the window at 4K; the recipe is in
  `~/dev/convex/convex-videos/lets-build-it-announcement/.work/screen-build/`.
- **Music goes in before his big watch, on a personal video too.** Let's
  Build It went to export with none, and he noticed afterwards: "we
  haven't got any music in the background". Three ElevenLabs beds by
  section (playful for the intro and demo, warm and curious in the middle,
  heartfelt for the sign-off), all ukulele, acoustic guitar, soft piano,
  brushed drums and warm bass at 95 to 100 BPM, with no bells, glockenspiel
  or marimba under the game's sounds, at -45 LUFS. He passed them first
  time: "musics good".

### Shorts cut from a conference talk: James's Abstract keynote

Two 9:16 shorts from a filmmaker's 1080p multi-camera edit of James Cowling's
talk (October 2026), for the team to see in Slack first. The project,
scripts and the speaker tracker are in
`~/dev/convex/convex-videos/abstract-clips/` (`.work/`).

- **Full-bleed, not framed.** Mike compared a framed layout (hook title
  above a square window of the talk over a blurred copy, captions below)
  with a 9:16 crop on the speaker, and picked full-bleed: "the full bleed is
  probably better". Use `tandem new --portrait` and crop each camera angle
  separately (blade at the filmmaker's cuts). Where the speaker walks, follow
  him with `video.transform.position` keyframes every 0.5 s from a smoothed
  track. Track the upper body only: on the front shot the light wood floor
  pulled a whole-frame track off him. A 1080p wide shot cropped to 9:16 goes
  soft past about 1.35x; the raw camera files would crop better.
- **A film clip or slide inside the talk stays whole,** in a square window
  over a blurred copy. Cropping it to 9:16 split the two actors.
- **The hook title only over the opening shot,** sliding off at the cut to
  the close-up: on full-bleed close-ups it covered the speaker's face. The
  speaker's name ("James Cowling, Convex CTO, at Abstract") stays up longer,
  until the first jump cut (about 7 s), moved up above his head on the
  close-up: Mike asked for it longer. Captions at `--y 0.70`.
- **A pro-filmed edit has no webcam lag.** `tandem new` leaves the 80 ms
  picture delay off takes a camera made (a timecode track, or a make and
  model); if a take still has it, clear it with `tandem sync 0 --media <id>`.
- **A second camera or a separate mic: `tandem sync <files>`,** not a
  script of your own. It lines them up with the camera take by sound, puts
  them in its take and places them in one undo step: the angle on "Angle
  2", off, and the mic on Voice with the camera's own sound muted. Show the
  angle where it helps with `showAngle`; never untick its clips, unlink or
  slip anything by hand. Read the lip-sync report it ends with.
- **Cutting a speaker's "right?"s:** only where there's a gap after it.
  Where it runs straight into the next word ("economy, right? And..."),
  leave it. The transcript's word times ran about 0.2 s early on this
  footage, so find the edges on a spectrogram, and don't trust the
  transcript view after the cut: it hid "You're" and "That's" that were
  still in the audio. Copy fixed captions across rather than running
  `tandem captions` again, which drops those words.
- **More talks the same way (Seth and the Fireside Chat, 12 Shorts, 4 Nov
  2026):** `~/dev/convex/convex-videos/abstract-talk-clips/.work/tools/build.py`
  does it in four steps: `new` (talk as camera, picture delay 0; an exported
  master has no timecode, so `tandem new` gives it 80 ms and picks the wrong
  file as camera), `place` (a source stretch), `frame` (blades at the
  filmmaker's angle changes and crops each shot to 9:16 on the face Apple
  Vision finds, following it, ignoring audience heads in the bottom of the
  frame; shots with nobody in them stay whole over a blurred copy), then
  `captions` and `titles`. Per-stretch fixes go in `.work/framing/<project>.json`:
  `who` left/right picks the talker in a two-shot, `x`/`z` pin a crop,
  `window` keeps a shot whole (an on-screen graphic, a wide from the back
  where he's tiny). Its `edit-plan.md` has the rest.
- **Open a Q&A Short on the question.** Every Fireside Short first went out
  starting on the answer ("The biggest one that I think is unsolved..."), and
  Mike: "We don't know what the question is when it starts. So can you
  interweave the question in there at the start?" (4 Nov 2026). Put the
  host's question first, even from a minute earlier or after the answer (Luke's
  "do we buy Salesforce or HubSpot, or build our own CRM?" opened its Short),
  start on the question itself rather than its lead-in ("Shifting gears...",
  "last ninety seconds"), and give a talk's running gag or number its setup
  (Seth's camp story before "the spreadsheet that became...", a hook saying the
  audience made the number). `tandem check` quotes the first 12 s of a
  Q&A Short (fireside, interview, podcast, Q&A or AMA in its name or
  files) with no question in them, and of any Short starting on a
  back-reference (see "Every Short stands alone"). It can't tell a running gag is missing its setup, so read the opening as a
  stranger anyway. Once the question is asked on camera, no hook title
  repeating it: "we don't need to
  show the question on the screen... because it should get asked at the start
  of the video anyway" (Mike, 4 Nov 2026). Keep the small name line.
- **The filmmaker's own insets are crops too.** Seth's master cut to a tall
  "audience cam" phone inset on the left while people typed on calculators:
  it's nearly 9:16 already, so crop straight onto it, and back to the speaker
  when he's the joke.
- **Titles over the chest on seated close-ups.** A fireside close-up puts the
  face at the top of the 9:16 frame, so the names (y 0.61) go just above
  the captions, not at the top. One name per person, only while they first
  talk: the host's as he asks, then the guest's from her first word, each
  for about 4.5 s, then neither (Mike, 4 Nov 2026: "only put the names on
  the screen for each person when they're talking"). `.work/tools/names.py`
  in abstract-talk-clips does it.
- **Fix captions by whole caption, not by word.** A word map (`fixCaptionWords`
  with `"you": "you."`) hit every caption with that word and the SDK run can't
  be undone; replace exact captions instead (`.work/tools/setcaps.ts` in that
  folder, which also deletes filler-only ones).
- **Black first frames after cuts are fixed.** At 29.97 fps a cut could load
  back one 48 kHz sample either side of its frame, so nothing covered that
  frame and it rendered black, and with captions over it `tandem check`
  missed one. Tandem now puts clip edges within a millisecond of a frame on
  it, and check counts a frame black under captions, so the
  `.work/tools/fixblack.py` workaround isn't needed any more.
- **B-roll never freezes.** Holding a 6 s cartoon's last frame for 2.85 s to
  cover a line read as a freeze frame to Mike. Pick a span the clip fits,
  or slow it a touch (0.93x was invisible).

### Shorts cut from his own long video: Muse Wonder (October 2026)

Three 40 to 50 s Shorts of the spiciest moments, to push the long video
while its topic was news. The project is `muse-wonder/Muse Wonder
Shorts.tandem`; `muse-wonder/upload/shorts/` has the exports, the crop spec
and the upload batch.

- **Make them with `tandem short --copy --apply`.** It writes "<Name>
  Short.tandem" beside the long video, laid out and made 1080x1920, so the
  app shows it portrait: "YouTube shorts are always portrait" (Convex 1.47,
  2026-10-16, when a Short made with plain `tandem short` opened landscape).
  The long video's project never changes. Cut the Short down in the copy.
  For a project already laid out with plain `tandem short`, `--copy` keeps
  its placements, and the `adoptFormat` command does the same conversion in
  place.
- **A whole release video as a Short (Convex 1.47):** cut the copy to under
  3:00 by dropping whole sections, not by trimming every item. Re-render each
  screen shot for the phone window (`broll/short/`, 2160x1680, about 36 px
  type, terminal lines wrapped at 47 columns), because a crop of a full-width
  terminal or docs page can't be read. Where the take has a gap (a voice dub),
  fill the camera behind it with a blurred, darkened copy of the shot so the
  top of the frame isn't black.
- **An old Short shown inside a new one goes in the window, small** (Convex
  1.48, 2026-10-26). Full frame, its burned-in captions sat right under the
  new ones: "you have the transcription on the screen showing both of them
  at the same time, which is confusing". Put it in the top window as a card
  (scale 0.42 at y 0.21875 over a blurred copy cropped to the window), with
  the camera in the bottom half, so it reads as the old video playing.
- **A question he asks the viewer types out on screen as he says it**, in
  his exact words with the typing sound, below his face, sliding off as he
  moves on (1.48: "pop up the question on the screen here as I say it").
  In the Short, turn the captions off under it so the words aren't shown
  twice.
- **Check the music is audible before exporting.** Beds added with
  `tandem assets use` and then `normalizeTo: -45` came back with `gain -31 dB`
  as well (1.48), so the first export had no music. `tandem loudness --tracks
  Music` over a stretch should read about -45 LUFS.
- **Pick moments that stand on their own:** a strong claim with its number,
  a rant, a "this broke" moment. Start about 0.1 s before the first word and
  end in the pause after a finished thought, checked with `tandem pauses`.
- **Every Short stands alone.** Mike turned down a 43 s tip from the Tandem
  video: "it's missing a lot of context around what tandem is. Also, it
  kind of refers back to the video, but people have not watched... you've
  got to really think about them as standalone things... or you've got to
  insert the extra context" (2026-10-20). Read every line as a stranger:
  cut or fix anything that points at the long video ("as you're seeing
  here", "the process I go through", "like I said", "so yeah, that's X",
  "can you get hold of it") or assumes they know the product, and put the
  missing context in the hook title or an on-screen line. A "what is X"
  Short is often the obvious first one to make. `tandem check` (and
  `--changed` once the opening changes) quotes a Short's first 12 s when
  they start on a back-reference ("And...", "So yeah...", "The other
  area...", "Like I said..."): read it, and fix it or say why it stands.
- **Keep the caveats.** Cutting "S tier or Haiku tier" straight after
  "Haiku costs like 40 times less" left out "it's kind of an unfair test"
  and "we weren't running the full model". Mike asked for them back so the
  clip stays fair to what it's knocking.
- **It's watched on a phone held in a hand.** The first cut put each 16:9
  shot whole in the top half and his chest below: "it's quite difficult to
  see the very small text... think about the viewer holding the mobile
  phone". What worked: his face full-frame on top (scripted takes are
  full-frame camera in portrait), word captions just under his chin
  (`tandem captions --y 0.505`), and each shot in a window below, cropped to
  only what he's talking about at that moment. Use
  `~/dev/convex/convex-videos/tools/shorts/portrait_crops.py`: give it each
  clip's region of interest and it writes the portrait crops. Code is
  re-rendered for the Short (a 1000 px window at 36 px, soft-wrapped,
  cropped to the window), and a table keeps only the columns he names, cut
  side by side. Look at every shot at about 540 px wide before showing him.
- **Re-render web B-roll for the window, don't crop it.** Cropping the 16:9
  page captures into the window cut lines off mid-sentence: "the B-roll is
  clipped, it gets cut off" (Tandem Shorts, 2026-10-20). Re-capture each
  page at 2160x1680 in a narrow browser window (380 to 640 CSS px wide, so
  body text lands at about 37 px on the phone), keeping the same pens at the
  same times, and place it full width at y 0.74, scale 1. The renderer is
  `tandem/.work/screen-build/short5.mjs`; `portrait_crops.py` is only for
  footage that can't be re-captured.
- **Platform UI owns the bottom, so B-roll goes on top (Tandem Shorts,
  2026-10-20).** Mike: "on platforms like TikTok or YouTube Shorts, they
  have all the UI down the bottom... the thing that you should be focusing
  on at any time [should be] at the top." This replaces the face-on-top,
  window-below layout above. With no B-roll he's full-frame; while a shot
  shows, it sits in a 2160x1680 window flush with the top (position y
  0.21875, scale 1) and the camera under it drops to the bottom half (scale
  2.4, y 0.80, blade the camera at each B-roll edge). Captions at y 0.47,
  between the window and his cap; hook titles and on-screen tips at y 0.62,
  never in the bottom quarter, where the title, channel and buttons sit.
- **Never the same person twice in the stacked layout.** A crop of the
  board from the same camera up top, over that camera's shot of the person
  below, shows them twice: on the Nipunn Shorts it was Nipunn's arm drawing
  up top over his face below, and Mike pointing at the board up top over
  Mike talking below. Mike: "there's awkward moments where you can see both
  my arm and my face talking at the same time. It seems a bit odd" (30 Oct
  2026). Put a graphic up top while the person is below, or go full frame on
  one shot. `tandem check` flags it as "Same shot twice" (one file on two
  tracks at the same moment), so run it after laying a Short out.
- **Give a Short the context the long video gave.** A viewer arriving at a
  Short hasn't seen the setup: on the Nipunn Shorts nobody had explained
  pages, the cursor, the documents log, snapshots or the tombstone. Mike:
  "Given that when a short, you have much less context from the previous
  parts of the video, I think it's important to help with that lack of
  context by using motion graphics or whatever" (30 Oct 2026). Read the
  Short's words as a stranger and build a graphic for each thing that leans
  on earlier context, in the long video's style and its drawn pieces, timed
  to the Short's own words and rendered for the 2160x1680 top window. The
  worked example is `nipunn-whiteboard-sept-2026/motion-graphics/src/shorts/`
  (seven graphics, `useShort` cues in Short seconds). A long video's own
  16:9 graphics can go in the window too, letterboxed at scale 1, where they
  already explain the moment.
- **A Short that explains a problem ends on the fix.** The first cut of
  the Nipunn backups Short stopped at "a backup of data that never
  existed", and Mike: "It's okay, but it hasn't really got a conclusion
  about how to fix it or what the solution is." A story didn't need one:
  "It is good because it's kind of like an anecdote. It doesn't necessarily
  need a conclusion. It's like a fun anecdote" (30 Oct 2026). So when a
  Short sets up a problem, trim the setup and bring in the speaker's answer
  from later in the long video (Short 1 v3 cut the setup by 6 s, added
  Mike's "what is the better algorithm to do this then?" and Nipunn's
  dance, and stayed at 62 s). An anecdote, a joke or a war story can end
  where it ends. Mike on v3: "what you did with short one is perfect. It
  sets up the problem and then explains how we solve it all within the same
  short", and "each short is designed to be self-contained" (30 Oct 2026).
  Plan every Short that way from the first cut.
- **Centre his face, not the frame.** He sits left of centre in the 16:9
  shot (nose about 39.5% across in the studio camera, 41% in Record It
  takes), and the 9:16 full-frame crop shows only a third of the width, so
  `tandem short` left his face at the left edge ("why is my face not centre
  on these shorts?"). Set each full-frame camera clip's position x to
  0.5 + (0.5 - faceX) x scale: 0.832 and 0.784 at scale 3.16.
- **Lay one music bed under each Short.** The long video's music track is
  locked, so it doesn't follow the cuts that stitch a Short together, and a
  section card's +14 dB swell landed mid-Short: "The music gets turned up
  loud in the middle of it for some reason" (What is Tandem, 2026-10-20).
  Unlock, remove the beds under the Short, place one bed for its length at
  -45 LUFS with a 0.8 s fade in and 2 s fade out and no keyframes, lock it
  again.
- **Fix the captions' words.** They come from the transcript, so they carry
  its mishearings: "comics" for Convex, "messages" for Meta's, "evils" for
  evals, "roots" for routes, "sinking" for thinking, "news models" for Muse
  models, "M dashes". Patch each caption's `text` and `words` before export.
- **A hook title over the first 2 to 4 s,** in his words ("S tier or Haiku
  tier?"), scaled to about 0.72 so it fits across, sitting over his chest or
  under the window, never over his face.
- **Bringing a project back from Bruce:** the archive there kept each
  file's second but not its milliseconds, so every stored fingerprint
  missed, analyses failed as "file changed" and renders quietly used the raw
  mic ("No isolated voice ... yet"). Tandem from 30 Oct 2026 treats a time
  that only lost its milliseconds as the same file; with an older build, set
  each source file's mtime back to the millisecond in its stored
  fingerprint (`tandem timeline --json`, `media[].fingerprint`, the middle
  number), then `tandem wait jobs`.
- **Export to `exports/`.** `tandem media --refresh` registers every file in
  the folder as media, and Tandem won't overwrite a file that's project
  media.
- **Schedule them apart:** one public straight away, then one a day at the
  long video's slot, each linking the full video in its description. Upload
  with yt-channel-manager's Shorts batch (plan, preflight, his approval,
  run). Pointing each Short's "Related video" at the long video is a Studio
  step for Mike.

### A model shoot-out with a live demo: Muse Wonder (October 2026)

Scripted intro, test and grading, with a YOLO walkthrough of three
agent-built apps in the middle (camera in the corner over his screen).
His first review round, 16 comments, became these:

- **Name it, show it.** When he names the contenders, a logo tile for each
  appears as he says it ("one with Opus, one with Wonder..."). The same for
  a model he brings in later ("can you put the logo... to show what Sol
  is?"). Logos come from `tandem assets search "<name>" --online --kind logo`.
- **"People are saying" needs more than one person.** Show two or three
  different people's posts, not the same one again: "Don't just keep
  relying on Theo so much. Not on the same tweet." Capture X posts with X's
  own embed, logged out, like the other shots.
- **Small text gets zoomed.** A leaderboard row he talks about is zoomed
  into as its highlight appears (`zoomToRegion` with `at`), not left as a
  full-page still.
- **Stills move.** A 13 s still of a prompt "rather than just being so
  static... scroll this a little bit": a gentle scale (1.1) and slow pan
  down over the shot.
- **Don't show the answer before he gets to it.** Two panes side by side
  gave away Opus's `.take(200)` while he was still on Muse's `.collect()`:
  show only what he's talking about, then cut to the full picture.
- **Show what he means.** "What I'd have preferred is a 200 plus or
  pagination": a mock-up on the real app's page, labelled as a mock-up.
- **A clip that doesn't fill 16:9** (a 1.44:1 game capture) gets a backdrop
  behind it: "you can see the sides of the video behind". Black was his
  ask; iPad recordings keep the blurred copy.
- **The real thing, labelled.** While he describes how the real product
  should work, show the real product briefly with a small "The real Let's
  Build It" label.
- **A divider before the conclusion.** A section card ("The verdict")
  before "so should I be using it day to day?", not just the music change.
- **A slip he notices gets a light on-screen nod** rather than a re-record:
  he said "Wonderful" for Muse Wonder and asked for a "(Wonder Full?)"
  callout.
- **A "Mike from the future" pickup** goes where its topic is on screen, as
  full-screen camera (no corner) with a "Mike from the future" title in the
  lower third, B-roll of each thing as he names it, and the demo's music
  bed paused under it (a calmer bed plays, then the demo bed resumes where
  it left off). Shots of the apps came from the running apps with made-up
  test accounts, so no real email is on screen.
- **Blur password-manager popups.** 1Password's "Save login?" showed other
  people's saved logins in his screen recording. Find them by scanning the
  recording's frames for the popup's region (mean brightness catches the
  fade in and out; a dark-pixel count missed about 0.1 s each side) and put
  a cropped, blurred copy of the screen on B-roll over each stretch.
  Add the screen file's `start_time` to every ffmpeg frame time first: a
  Record It screen file can start 0.77 s in, and a blur placed without it
  lands that much early (docs/agents/reading.md, "Source times and ffmpeg").

### A long screen demo with phone footage: the Threadbear launch (November 2026)

A 63-minute unscripted take of Mike showing his own app, cut to about 26
minutes over three rounds. What his comments asked for:

- **Full screen only when he turns to the camera at the start of a
  section,** then back to the corner: "while I'm facing the camera directly
  here, just at the start of this section, can you make me full screen";
  "from this clip onwards back to picture in picture". Never switch to full
  screen mid-flow: "leave me picture in picture as I'm talking here because
  the jump is a bit weird".
- **Move the corner when it covers what he's showing:** `pipLeft` while he
  shows patches on the right ("I'll be covering up a lot of the patch stuff
  on the right hand side"). A phone recording shown over the desktop
  shrinks to the top right while he points at the desktop ("I can't see
  the desktop"), with position and scale keyframes on the phone clip, its
  frame and any redaction copies alike.
- **Show the thing as he names it,** everywhere: the project pickers of the
  apps he compares, the previous video he mentions, the rule he describes
  (B-roll from that earlier video, fetched from the archive on Bruce), the
  menu he opens (a zoom), the setting he describes (a look-alike), and
  evidence for any number he gives ("back this up with evidence visually":
  a terminal look-alike of the real `du -sh` of his agent logs). Where he
  explains how something works, a motion graphic: "what the kind of
  architecture is", "how the data moves around and why".
- **Old messages read as old.** His real past messages in a look-alike
  confused him as an "early version"; zoom them out on a dark backing with
  a date caption underneath.
- **Zooms on a screen recording stay at about 1.6x** or less: 1.8 to 2.2x
  turned small UI text soft ("this text is a little bit blurry when it's
  zoomed in"). Text-aware upscaling is being looked at separately.
- **Gags he asked for:** a Windows logo with a crying emoji popping up on
  "sorry Windows users"; a cartoon of his Mac mini Bruce as an Aussie bloke
  in a cork hat (Codex image tool); the pairing QR code replaced with a
  Rickroll QR rather than blurred ("it'd be funny to see if anybody actually
  tries scanning that QR code").
- **The outro, as usual:** a title-less `Convex wipe` segment before the
  sign-off section (give it room: a beat of silence either side of the
  cut), his closing question handwritten (Caveat) beside him as he asks
  it, the `Comment below` segment on "let me know in the comments" and
  `Like and subscribe` on "drop me a like and sub".
- **Music under every chapter,** not just test beds: "for some reason
  there's no music in the middle of it". A bed per chapter in one family
  (Rhodes, soft guitar, round bass, brushed drums, 85 to 95 BPM), each
  swelling under its section card; a chapter longer than its bed carries on
  with a second copy of the same bed from further in, crossfaded over 3 s
  on a second music track.

### A quick personal live demo for X: the pool model (October 2026)

A 3-minute one-take demo of his 3D pool model in the browser
(`convex-videos/pool-project/`), cut, B-rolled and exported in one sitting.
What he changed, in the order he asked:

- **Corner for the whole thing.** Opening on his face full screen and going
  to the corner for the demo wasn't what he wanted: "make it picture in
  picture for the entire thing". When the screen is the subject from the
  first line, he's in the corner throughout.
- **Bottom-right, but out of the way of the UI he clicks.** He tried
  bottom-left (mirrored; `pipLeft` now flips the camera itself) and went back to the right:
  "when I click stuff on the right hand sidebar can you just hide me for a
  second or move me out of the way". Find the clicks from the recording
  (frame differences in the sidebar's region), not the transcript; skip
  plain mouse travel. Slide him off to the right over 0.45 s
  (`video.transform.position` keyframes on every camera clip in the
  stretch, easeIn out, easeOut back) and merge stretches less than about 2 s
  apart so he doesn't pop in and out.
- **No corner over B-roll.** Him in the corner over full-screen B-roll "just
  looks weird". Slide him off for B-roll the same way, and move the Camera
  track above B-roll (`moveTrack`) so the slide shows.
- **Phone footage goes in a phone, not full screen.** "Put the footage in a
  mobile phone, have it sliding in from the side... not complete takeover
  the screen". A landscape phone frame PNG (transparent screen, dynamic
  island, soft shadow) on Graphics over the clip on B-roll, the clip scaled
  and cropped to the screen hole, both sliding in from the right with the
  same position keyframes and out to the left, over the screen recording.
- **Show each source as he lists it.** "Phone video... satellite... drone
  photos... surveying... 2D drawing" got a shot each, from his project
  archive (`~/dev/me/the-pool`). Crop plans and surveys to the drawing:
  their title blocks carry his address and the designer's phone and email.

### A phone app demo as a portrait Short: Walkies (October 2026)

A webcam take of Mike talking through his iPhone app, plus the phone's own
screen recording, made into a sub-3:00 YouTube Short
(`convex-videos/walkies/`). He asked for portrait himself ("should we do
this as a portrait video?... under the 3 mins").

- **Sync by eye when the phone has no voice.** An iOS screen recording
  carries only app sounds, so `tandem sync` scored 14 and refused. The
  file names (Record It's camera start and iOS's
  `ScreenRecording_<date> <time>`) gave the offset to the second, and a
  named moment confirmed it (the Woodhenge pin zoomed in as he said
  "Woodhenge"). Put the phone file in the camera's take with
  `updateMedia` (`takeID`, `takeOffset` = seconds into the take it
  started), then `placeMedia` both. With an explicit `sourceStart`,
  placeMedia gave both files the same media time and ignored the phone's
  offset (mikecann/tandem#63): check the screen clip's source range after.
- **Layout he passed:** the phone recording full height with a blurred,
  darkened copy behind it filling the sides; Mike in a rounded face-cam
  box (cutout off, cropped to his face, white border, shadow) bottom-left
  above YouTube's title area. The cutout corner looked like a floating
  torso in portrait. Slide the box off over pages it would cover (the shop
  list) and back after. Where the phone just sits on a still map while he
  talks, go full-frame on his face.
- **Cut talk before features.** To get under 3:00 I cut the shell shop,
  and Mike stopped the upload: "you didn't actually show the shop... cut
  down a little bit of the talk at the end of the chef stuff... so we can
  get some of the other features that the app has got in there". In a
  demo Short, what the app can do on screen beats him talking over a
  still screen.
- **Hide notification banners** (Gmail and X pop-ups mid-recording) with
  a `freezeFrame` copy of a clean frame, cropped to the top strip, on
  B-roll, where the picture under the banner is still. `tandem check`
  used to hang on these; it doesn't now (mikecann/tandem#62).

### A two-person whiteboard interview: Ian Macartney on time in Convex (October 2026)

Mike interviews Ian, a Convex engineer, at a whiteboard (37:45, about 10
review rounds, `convex-videos/ian-whiteboard-sept-2026/`): a wide camera of
both, a close-up of Ian, and a mic on Ian that picks up both voices. Its
cut-offs are in "How Mike likes a take cut", its cold open above. The
Nipunn interview from the same shoot (40:45,
`convex-videos/nipunn-whiteboard-sept-2026/`) used everything here and
needed two review rounds plus the cold open; its `edit-plan.md` is the
quicker model to copy.

- **Name the angles,** and change angle on a cut: C, Ian's close-up (the
  close-up track on over the wide); W, the wide; W2, a slightly tighter
  wide (`zoomToRegion` {x 0.065, y 0.04, w 0.87, h 0.87}); P, Ian's
  punch-in from the wide ({0, 0, 0.714, 0.714}); M, Mike's single from the
  wide ({0.375, 0.17, 0.625, 0.625}). Change angle at a jump cut that
  isn't under B-roll, but only once the framing has held about 4 s, and
  never flash the close-up or P for under 3 s. Changing at every jump cut
  on the Nipunn interview (same shoot) zoomed between W and W2 every 1 to
  2 s in quick stretches: "a few too many zoom in and zoom out cuts here
  and in other places" (2026-10-27). W2 is only 1.14x on W, so cut
  straight between them it reads as a zoom, not a new angle. Holding 4 s
  took 302 visible changes down to 175 and he passed it; the tool is
  `nipunn-whiteboard-sept-2026/.work/angles/fewer.py`.
- **No slow zooms.** "Is it you that's moving the camera around here?
  Because it's kind of disorientating a little bit", and "I don't think
  it's appropriate necessarily for this video" (2026-10-21). All 77
  animated close-up pushes came out. Steady framings only.
- **Show whoever's talking:** "While I'm talking you should show me on
  screen, or at least zoom out to the wide angle." On one shared mic
  neither level nor pitch tells them apart, so label the turns from the
  transcript and check the uncertain ones against frames. M for Mike's
  short turns; for long ones alternate W and W2, because he often points
  at the board, or Ian is writing on it.
- **Hide the camera operator's moves** (reframes, focus pulls) with the
  other angle.
- **Fill a mic dropout from a camera's mic.** Ian's mic dropped out for
  11.6 s. The wide camera's sound covered it, EQ'd with ffmpeg's
  `firequalizer` to the mic's long-term spectrum and raised 36 dB. Check
  the gap's loudness after: it first went in at -60 LUFS.
- **People mentioned get a photo and a lower third,** found from their
  company's pages (Emma from the Convex About page). A nickname earns a
  gag: Ian as "the GOAT" got a cartoon goat in a circle above his lower
  third, with a bleat.
- **Handwritten section titles,** writing on like a marker on the
  whiteboard over the camera dimmed behind, as sentence-case questions
  ("Is time a lie in Convex?") with no "08 / 10" counter. Mike picked them
  from four looks. `motion-graphics` has the build and the timing. Each
  asks the question on screen at that moment and leaves the answer to the
  section: "I like these questions but they do give the game away a little
  bit" (Nipunn interview, 2026-10-27). His model was "What's next for
  backups?"; six reworded titles followed it, like "How does the log
  help?". Use the speaker's own question where there is one.
- **Voice isolation on the interview mic in the first cut.** Ian's Voice
  clips had Apple voice isolation at 1; Nipunn's went into round 2 at 0
  and Mike heard the aircon: "have you applied the same sort of sound
  treatment that we did on the Ian video?" (2026-10-26). Set it on every
  Voice clip when you first cut the take (it took the hum under 150 Hz
  down 15 to 60 dB and speech about 1 dB).
- **Back up the jargon with the real reference.** When they name a term
  and its history (OLTP and OLAP, "nineteen seventy something"), Mike
  asked for the Wikipedia page "just to confirm that we got this right".
  Pick the article whose first paragraph says it plainly and has no
  fundraising banner or warning boxes over the lead.
- **Graphics never cover Ian drawing or pointing at the board,** and draw
  things the way he drew them (also in `motion-graphics`).
- **A review copy for the guest,** once Mike has reviewed every agent edit: `tandem export --preset youtube1080`
  (5.7 GB for 37 minutes, about 10 minutes), put in the Convex Dropbox
  with rclone on Bruce, since the laptop has no Dropbox app. scp it to
  `bruce:/Volumes/CannMedia/ConvexFootage/exports/`, `rclone copyto` it
  into `dropbox:/Convex Workspace/Video/Sept-office-interviews/3. Exports/`
  under a name that says it's an edit (the raw interview exports live
  there too), check the size with `rclone lsf --format sp`, make the link
  with `rclone link "<path>"`, and delete the staging copy on Bruce.

### A seated rapid-fire Q&A: James Cowling's "Spicy Questions" (November 2026)

Mike asks about 34 questions, James answers, two RED cameras and one lav
on James (`convex-videos/james-spicy-questions/`). His first watch, 17
comments, changed these rules for a conversation like this:

- **Loose pacing, not the whiteboard tightening.** `tighten --mike` and a
  dead-air pass made "janky silence cutouts... it cuts out some of the
  nuance, it's okay to have a bit of silence in this video". In a seated
  conversation, keep natural silences: only shorten a pause over about
  3 s (to about 1.2 s), and cut only content (false starts, retakes,
  off-camera chat) and clean fillers.
- **His asides to the edit are editor's notes even without the words.**
  "I'm not sure about this question, but I'll ask anyway", "Only got four
  questions left", "Yep. Yep. This is interesting." before a question:
  cut them and keep the question. Also trim the wait after an answer ends
  before his next question to a natural beat.
- **Question titles stay up long enough to read.** Handwritten on the wall
  as he asks (no "N of 33" counter, which he dropped), held about words x
  0.25 s + 1.5 s after they're written; stay on his shot longer rather
  than cutting the title short. Every question gets one, including a
  follow-up asked mid-answer.
- **Name tags over each person,** a two-line title above their own head,
  his too ("Mad Scientist at Convex"), not one centred card. No avatar
  circle when the person is on screen ("we can see our face"), and no
  drop shadow under the yellow line (it only looks right under white).
- **Shorts from it (layout A):** full-bleed on whoever's talking, the
  question handwritten big as he asks it, then parked small at the top
  only long enough to read, then off: "I don't think we need to show the
  question on the screen the whole time." Name tag at the bottom under
  the captions, not above the head. No music: he turned down chill
  lounge, seven dramatic beds and eight lighter styles (boom-bap, funk,
  pizzicato, house, synthwave, swing, surf, chiptune), then "maybe we just
  don't put music on the shorts" (3 Nov 2026).
- **A cartoon of someone not in the room gets their name on it** ("JAMIE"
  on his jumper) so viewers know who it is. Once per beat: Mike deleted
  the copy that switched sides on the cut and the second smug pop, keeping
  one questioning Jamie and one smug one.
- **Show who and what they mention:** a cartoon of a colleague named in a
  story (Jamie sliding in, eyebrow raised; popping up smug on "Jamie's
  always right"), and pop-ups of the real thing named (a product's site,
  the event video).
- **Sound on a single far lav:** voice isolation on audio someone already
  cleaned sounded "too much AI audio compression". He compared Adobe
  Podcast (best, but he won't depend on uploading), SAM and self-hosted
  models, and picked RoFormer dereverb then DeepFilterNet 3 capped at
  12 dB (`convex-videos/tools/voice-enhance/`, run it on RunPod). It
  softens quiet word edges, so re-run `check --cuts --listen` over every
  join after swapping a voice file in; DeepFilterNet's digital silence
  can drop whole quiet words, so find and fix dropouts too. In the end he
  used Adobe Enhance for that one-off, blended 0.8 Adobe + 0.2 original
  ("too clean" alone; check Adobe's words, it changed 7).
- **Hum in the blended-back original:** a mains buzz on one take was odd
  harmonics of 60 Hz from 420 Hz to 11 kHz, and notching only the first
  six and four near 3.8 kHz left it audible ("I'm hearing that background
  buzz", on a Short, 4 Nov). Before shipping a blend, list every harmonic
  over the pause floor (`tools/voice-enhance/src/blend/` has the
  measuring and `dehum2.py`, which notches only the original's share:
  blend minus 0.8 x Adobe), not just the low ones.

