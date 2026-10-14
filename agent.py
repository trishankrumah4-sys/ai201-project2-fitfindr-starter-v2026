"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
import config
from mcp_client import call_tool
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


def _parse_query(query: str) -> dict:
    """Pull description, size, and max_price out of a plain-language query (regex)."""
    text = query
    max_price = None
    m = re.search(r"(?:under|below|less than|max|up to)\s*\$?\s*(\d+(?:\.\d+)?)", text, re.I)
    if not m:
        m = re.search(r"\$\s*(\d+(?:\.\d+)?)", text)
    if m:
        max_price = float(m.group(1))
        text = text.replace(m.group(0), " ")
    size = None
    m = re.search(r"\bsize\s+([A-Za-z0-9/]+)", text, re.I)
    if m:
        size = m.group(1)
        text = text.replace(m.group(0), " ")
    description = re.sub(r"[^A-Za-z0-9\s]", " ", text)
    description = re.sub(r"\b(looking for|i want|i need|find me|a|an|the)\b", " ", description, flags=re.I)
    description = " ".join(description.split())
    return {"description": description, "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    iterations = 0
    trace.start_trace()

    # Step 1: parse the query
    iterations += 1
    trace.check_iterations(iterations)
    session["parsed"] = _parse_query(query)
    parsed = session["parsed"]
    trace.step("parse_query (regex)", inputs=query, returned=parsed)

    # Step 2: search
    iterations += 1
    trace.check_iterations(iterations)
    args = {"description": parsed["description"]}
    if parsed["size"] is not None:
        args["size"] = parsed["size"]
    if parsed["max_price"] is not None:
        args["max_price"] = parsed["max_price"]
    session["search_results"] = call_tool("search_listings", args)
    trace.step("search_listings (via MCP)", inputs=args,
               returned=session["search_results"])

    # THE BRANCH: nothing came back, so stop before the second tool
    if not session["search_results"]:
        session["error"] = (
            "No listings matched. Try a broader description, a higher price "
            "ceiling, or a different size."
        )
        trace.step("branch: no results", note="empty search, stopping before suggest_outfit")
        return session

    # Step 3: choose the first result, read it back out of the session
    session["selected_item"] = session["search_results"][0]
    trace.step("select first result", returned=session["selected_item"])

    # Step 4: outfit suggestion, reading the item from the session
    iterations += 1
    trace.check_iterations(iterations)
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )
    trace.step("suggest_outfit", inputs=session["selected_item"],
               returned=session["outfit_suggestion"])

    # Step 5: fit card, reading both values from the session
    iterations += 1
    trace.check_iterations(iterations)
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )
    trace.step("create_fit_card", inputs="outfit + selected item",
               returned=session["fit_card"])

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
