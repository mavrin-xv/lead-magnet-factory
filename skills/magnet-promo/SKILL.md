---
name: magnet-promo
description: Writes the posts that promote a lead magnet - a give-away post per platform (X, Threads, LinkedIn, Instagram caption and carousel outline, short video script, Telegram channel, newsletter) that hands over one real piece of the magnet and ends with a single keyword or link ask - plus a pinned comment and a launch plan, then checks length limits, keyword placement, one call to action and links that do not work on the platform. Use when the user says "promote my lead magnet", "post for the freebie", "write the launch posts", "comment KEYWORD caption", "how do I announce the guide", or after keyword-delivery has a flow.
---

# Magnet promo

People comment for a magnet when the post already gave them something and the magnet clearly holds more of the same. "Comment GUIDE for my free guide" with nothing else is an ad, and gets ad numbers. This skill writes posts that give one real piece away first.

## Inputs

- `magnets/<slug>/magnet.md` (the magnet) and `concept.md` (reader, pain, title).
- The keyword from `flow.json`, or the link if the channel delivers by link (newsletter, email).
- The platforms the user posts on.

## Procedure

1. **Pick the give-away**: one item from the magnet that works on its own. The best one is usually from `## Start here`: one check, one step, one script. Write it out in full in the post.
2. **Write one post per platform** with the shapes in [references/post-shapes.md](references/post-shapes.md). Each one rethinks the angle for the format (a thread lists, a video shows, a newsletter explains); never paste the same text everywhere.
3. **End each post with one ask.** Keyword channels: "Comment DIALIN and I will send you the other 21 checks." Link channels: one link. The ask names what they get and how much more there is.
4. **Add a pinned comment** for keyword posts: the keyword again in one line, for people who skip captions.
5. **Write the file** to `magnets/<slug>/promo.md` with one `## <platform>: <label>` section per post (the template is `templates/promo.md`). Notes to yourself go in code fences; the checker ignores them.
6. **Check:**
   ```
   python3 scripts/promo_check.py magnets/<slug>/promo.md --keyword DIALIN
   ```
   Fix every FAIL: over the character limit, keyword missing, a link and a keyword in one post, a link in an Instagram or TikTok caption (not clickable there).
7. **Plan the launch** with `templates/launch-checklist.md`: test the flow first, post on the main channel, then the others over 3 to 7 days, re-share the best-performing post after 2 weeks with a new give-away item.

## Hard rules

- Give before asking. Every post contains a usable piece of the magnet, in full.
- One call to action per post. Not "comment, follow and share".
- The keyword is spelled the same in every post, caption, image and video.
- No fake scarcity ("only 24 hours") on an evergreen magnet. No invented numbers or testimonials.
- Use the reader's plain words, taken from the survey or the concept card.
- This skill writes drafts. It never posts. The user publishes.

## Output

```
PASS [x: post] 262 chars
PASS [threads: post] 431 chars
PASS [instagram: carousel caption] 690 chars
PASS [newsletter: section] 1108 chars
OK: 0 fail(s)
```

Worked example: `examples/acme-coffee/promo.md`.
