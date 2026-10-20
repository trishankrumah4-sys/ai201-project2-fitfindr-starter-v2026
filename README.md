# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does
  A user describes a thrift find, like "vintage 
graphic tee under $30, size M". FitFindr searches a listings file for matches, suggests outfits using the user's wardrobe, and writes a short shareable caption for the find. If nothing matches, it stops and tells the user what to change instead of calling the later tools.
<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory
A list of listing dicts (id, title, description, category, style_tags, size, condition, price, colors, brand, platform), ranked by how many words of the description appear in the title, description, or style tags (best first), limited to config.SEARCH_RESULT_LIMIT. A size matches when every token of the requested size appears in the listing's size, so "M" matches "S/M".
<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

- **Returns:** A list of listing dicts (id, title, description, category, style_tags, size, condition, price, colors, brand, platform), ranked by how many words of the description appear in the title, description, or style tags (best first), limited to config.SEARCH_RESULT_LIMIT. A size matches when every token of the requested size appears in the listing's size, so "M" matches "S/M".

- **What it does:** Searches data/listings.json for items matching a text description, a size, and a price ceiling.
- **Inputs:** `description` (str), `size` (str), `max_price` (float)
- **Returns:** A list of listing dicts, each with id, title, description, category, style_tags, size, condition, price, colors, brand, platform.
- **When it has nothing:** Returns an empty list `[]` (not None, not an error).
- **Inputs:** `new_item` (dict, a listing from search_listings), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts; `items` may be empty)
- **Returns:** A string with one or two outfit ideas, each naming the new item and the wardrobe pieces it goes with.

- **What it does:** Takes one listing and the user's wardrobe and suggests outfits that combine them.
- **Inputs:** `new_item` (dict, a listing from search_listings), `wardrobe` (list of dicts, the wardrobe items; may be empty)
- **Returns:** A string of 2-3 outfit ideas, each naming the new item and the wardrobe pieces it goes with.
- **When it has nothing:** If `wardrobe` is empty, returns a string of general styling advice for the item instead of failing.

- **Returns:** A two-to-four sentence caption (a string) that mentions the item, its price, and its platform.
- **When it has nothing:** If `outfit` is empty, returns a message saying there is no fit card to write yet.

- **What it does:** Writes a short social-media-style caption for an outfit.
- **Inputs:** `outfit` (str, the text from suggest_outfit), `new_item` (dict, the listing)
- **Returns:** A string of 1-3 sentences that someone would actually post, mentioning the item.
- **When it has nothing:** If `outfit` is empty, returns a caption based on `new_item` alone.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
        "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent
        
     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings returns an empty list, put a message naming what to change (loosen the price, size, or description) in the session and stop. Otherwise take the first result and go to suggest_outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** regex, in `agent.py::_parse_query`. It pulls a price after "under" or a `$` sign, a size after the word "size", and treats the rest as the description.

**What moves through the session:** `query` → `parsed` → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`. Each tool's result is stored in the session, and the next call reads its input back out of it.
---

## Sample Run

 **One full query**

```
$ python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit One: Pair the Y2K Baby Tee with your Baggy straight-leg jeans, dark wash for that classic 2000s contrast. Add the Black combat boots and the Black crossbody bag to ground the pastel butterfly print with some edge.

Outfit Two: Tuck the Y2K Baby Tee into your Wide-leg khaki trousers. Layer the Vintage black denim jacket on top, and finish the look with your Chunky white sneakers for a casual, effortless daytime vibe.

  Fit card: Finally scored this pastel butterfly Y2K baby tee on depop for just $18 and I am obsessed. Gives off total 2000s mall-goth-meets-sweetheart energy, especially styled with baggy dark wash denim and chunky boots. Can’t wait to live in this all spring. #depopfinds #y2kstyle

0 model calls this session, 2 served from cache
```

(This output was served from the starter's cache.)

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'size': 'S/M', 'price': 18.0, 'platform': 'depop', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'size': 'L', 'price': 24.0, 'platform': 'depop', ...}, ... 6 listings in total, all $30 or under]
```

```
$ python -c "from tools import search_listings; print(search_listings('zzzz'))"
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Grab those Vintage Levi's 501 Jeans and tuck in your White ribbed tank top. Cinch it all together with the Brown leather belt for some classic definition, then step into your Chunky white sneakers for an effortless, everyday look. Throw the Black cropped zip hoodie over your shoulders if you need an extra layer.

For a cool streetwear edge, pair the Levi's with your Oversized grey crewneck sweatshirt. Layer your Vintage black denim jacket on top, and finish the outfit with your Black combat boots and the Black crossbody bag for a sharp, textured monochrome contrast.
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
Vintage Levi's 501s are the ultimate wardrobe building block. Since they have that perfect mid-rise and straight-leg fit, you can easily dress them up or down.

For an effortless daytime look, pair them with a slightly oversized white cotton button-down, tucked in casually at the front. Add a classic brown leather belt, retro sneakers, and a canvas tote bag for an easy, timeless vibe.

To shift into evening or edgy streetwear, swap the button-down for a fitted black ribbed tank top or a vintage band tee. Layer on an oversized leather biker jacket, chunky black boots, and silver hoop earrings. The contrast between the rugged denim and sleek accessories always hits the mark.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Found these vintage Levi's 501 jeans on Depop for just $38 and I am never taking them off. The medium wash has that 90s slouchy, effortless vibe I’ve been hunting for forever. Can't wait to style them with my favorite white sneakers for an easy weekend look. #thriftfind #vintagelevis
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('', load_listings()[0]))"
No outfit was provided, so there is no fit card to write yet.
```

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Code to add to tools.py for suggest_outfit.
- *What came back:* A script that put the search code into suggest_outfit instead of the right function, so it crashed with NameError: name 'description' is not defined.
- *What I changed:* I used grep to see which lines belonged to which function, then had the code replaced so each tool had its own.


**Moment 2**

- *What I asked for:* Why the search picked the Y2K Baby Tee instead of the graphic tee.
- *What came back:* A guess that listings were tying on score. I printed the scores and three listings did tie at 3.
- *What I changed:* I made words in the title count extra, so ties break toward title matches.


<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. state: selected item reaches suggest_outfit | 3 of 3 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card mentions the item | 3 of 3 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. fit card length | 3 of 3 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET | All 5 tries ran search, outfit suggestion, and fit card without stopping. 5 passes against a target of 4. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | All 5 tries stopped after the empty search, before suggest_outfit, with zero model calls. The message told the user to try a broader description, a higher price ceiling, or a different size. |
| 3 | The item the search found is the item passed to suggest_outfit | 3 of 3 | MET | In all 5 tries the selected item in the session matched the item suggest_outfit received (same title, price, and platform in the trace). The trace does not print the id, so this is a weaker check than my criterion says. |
| 4 | The fit card mentions the item | 3 of 3 | MET | I counted a caption as mentioning the item if it used a distinctive word from the listing title, such as "mesh" or "butterfly". All 5 captions for the mesh top did. |
| 5 | The fit card stays within the length limit | 3 of 3 | MET | I read the limit as two to four sentences, from my own create_fit_card spec, with hashtags not counted. Every caption I checked had two or three sentences. |

**Diagnoses**
Nothing missed, so there is no failure to diagnose. That says as much about my targets as about the agent.

My targets were easy. Criterion 1 asked for 4 of 5 on a query that clearly matches listings, which is hard to miss. Criteria 4 and 5 were also loose. The prompt hands the model the item, so mentioning it is close to guaranteed, and two to four sentences is a wide range. I scored criteria 3 to 5 as every try has to pass, since the test ran five tries but those criteria said 3 of 3. The state check is also weak, because the trace shows the title, price and platform but not the id.

One real problem got past all five of my criteria. For "vintage graphic tee under $30", the agent picked the Y2K Baby Tee in all five tries, ahead of "Graphic Tee — 2003 Tour Bootleg Style", which is the closer match. For "vintage band tee under $30", it picked the Graphic Tee rather than "Vintage Band Tee — Faded Grey". Because it was the same pick every time, this comes from the search ranking in tools.py::search_listings, not from the model. My likely explanation is that listings tie on matching words and ties are broken by their order in the data file. I have not yet confirmed that by printing the scores. None of my five criteria measure which result gets picked, so this is a gap in my criteria.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** 
I registered search_listings in mcp_server.py with a description and typed inputs, and run_agent() now calls it through mcp_client.call_tool. The results matched the direct call. Each call starts and stops the server, so it is slower.



---

## The Improvement
| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | FAIL | FAIL | FAIL | FAIL | PASS | MISSED (1/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. state: selected item reaches suggest_outfit | 3 of 3 | PASS | FAIL | FAIL | PASS | PASS | MISSED (3/5) |
| 4. fit card mentions the item | 3 of 3 | PASS | FAIL | FAIL | PASS | PASS | MISSED (3/5) |
| 5. fit card length | 3 of 3 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
**What I changed:** In tools.py::search_listings, words that appear in a listing's title now add 0.5 to its score, so ties break toward title matches.

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:** The search ranked the Y2K Baby Tee ahead of the actual graphic tee because listings tied at 3 and ties went in file order.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

**Did it help, and how do I know:** It fixed the ranking: "vintage graphic tee" now picks the Graphic Tee, and "vintage band tee" now picks the Vintage Band Tee. The criteria numbers got worse, but the after run had many 503 UNAVAILABLE errors from the model service, so the comparison is not clean.



---

## What's Still Broken
- The model service returned 503 UNAVAILABLE errors in my after run, and the test harness recorded those tries as CRASHED. My agent's handler only gave a clean message when I forced a bad key, so I would add handling for temporary 503s, such as one retry and a message saying the service is busy. I stopped because it needs a retry design I did not have time to test.
- My five criteria do not measure which listing the search picks. The ranking bug got past all of them. I would add a criterion about the top result matching the title words.
- Criterion 1 had an easy target (4 of 5), and criteria 3 to 5 said "3 of 3" while the test ran five tries. I would rewrite them with real counts.
- The state check only compares title, price and platform, because the trace does not print the id.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
