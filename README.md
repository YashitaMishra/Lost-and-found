## Ashoka Lost and Found with Map

This is a web app that helps people at Ashoka University find lost things. You report a lost or found item, drop a pin on the campus map, and the app suggests likely matches. If you lost something, you can also add the places you went that day.

Built for CS-3810 Design Practices in Computer Science.

| Tests | What they check 
| --- | --- 
| Logic (white-box) | Status rules, match score, visited-place rules, who can see what, permissions 
| Requirements (black-box) | At least one test for each error case
| Browser | Creating a report, map pins, the visited-places editor, chat 
| End to end | Lost report, found report, match, accept, chat, recovered

Tests also run automatically on every pull request through GitHub Actions.

---

## How the code is organised

The pages only show data and collect input. That way the algorithms and basic functionality of the app can be tested without opening a browser.

---

## Use of AI

We used Claude to help plan, design and review this project. Every prompt, what we kept and what we changed is recorded in [`AI_log.md`](AI_log.md). The app itself uses no AI when it runs.

---

## Known limits

- Built for one campus. Map searches use a simple box around the area on screen, which is fast enough at this size but would need a proper map index for a much bigger area.
- New chat messages can take up to 15 seconds to appear, because the page checks for them every 10 to 15 seconds instead of keeping a live connection.

---

## Team

| Name | Main work |
| --- | --- |
| Yashita Mishra | Repo setup, database tables, all pages and forms, the map and visited-places editor, black-box and browser tests, README |
| Megha Mudakkayil | Feature logic (reports, matching, statuses, chat, privacy), photo storage, putting the app on AWS, logic tests |
