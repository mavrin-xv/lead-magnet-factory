# Interactive magnets: quiz, calculator, AI-graded audit

Interactive magnets reveal a problem with the reader's own data, which makes them strong at the awareness and decision stages. They also put code on the public internet, so they come with rules.

## Shapes

| Shape | Reader gives | Reader gets | Bridge |
|---|---|---|---|
| Quiz | 5 to 10 multiple-choice answers | A score, a type, the top 3 gaps | The offer fixes the biggest gap |
| Calculator | 3 to 6 numbers they know | A number they did not know (cost of the problem, a forecast) | The offer changes the number |
| AI-graded audit | A URL, a text, a photo | A scored review against your rubric | The offer is the fix or the done-for-you version |

## Build rules

1. **Show the result before any gate.** Ask for an email or a DM after the result, to "send the full report", never before. Gating the result kills completion and trust.
2. **The rubric is yours.** An AI audit is only worth taking if it grades against criteria a generic chatbot does not have. Write the rubric first, as a checklist, then let the model apply it.
3. **Keep scoring deterministic where you can.** A quiz score and a calculator are plain arithmetic in the page. Only the free-text review needs a model.
4. **Static first.** A quiz or calculator is one HTML file with inline JavaScript. It needs no server.

## Security rules (for anything with a server or a model call)

- **API keys stay on the server.** Never put a model key, a CRM key or a webhook secret in the page source. The page calls your endpoint; the endpoint calls the model.
- **Rate limit the endpoint** per IP and per day, and cap the input length. A public "paste your text" box is a free proxy to your model account otherwise.
- **Fetching a URL the reader gives you:** allow only `http` and `https`, resolve the host first and refuse private, loopback and link-local addresses (the loopback, private, link-local and unique-local ranges for both IPv4 and IPv6; Python's `ipaddress` module has `is_private`, `is_loopback` and `is_link_local` for this), cap the response size and the time, and do not follow redirects to a refused address. This blocks server-side request forgery.
- **Treat the reader's input as data.** Put it in the model prompt as quoted content, tell the model it may contain instructions to ignore, and never let the model's output trigger actions (emails, writes) without your own code checking it.
- **If a check or a model call fails, still show something.** Show the deterministic part of the result and say the rest is coming by message. A blank error page loses the lead.
- **Store the minimum.** The contact field and the score. Not the pasted text, unless the reader agrees.
