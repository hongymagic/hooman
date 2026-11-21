# Fidelity

`compare.py` lists what an edit changed in its source, or what a draft added to
its list of facts. An audit of eleven commercial humanising tools found a
number, date, name or quotation altered or dropped in 35 to 65 per cent of the
documents that contained one. An edit that reads better and says something
else has failed.

## Comparison

Commands run from the skill directory. Python 3.12 or newer, no third-party
dependencies, no network calls, and neither file is modified.

```sh
python3 scripts/compare.py original.md revised.md
python3 scripts/compare.py facts.txt draft.md --brief
python3 scripts/compare.py original.md revised.md --json
```

Use `-` for one file on stdin. `--format` applies to both files; without it each
format follows its extension.

| Kind | What is compared | A difference is |
| --- | --- | --- |
| `numbers` | Figures, amounts, percentages, times and versions, with their sign, currency and unit | an error |
| `dates` | Month and weekday names | an error |
| `links` | URLs of any scheme, `www.` addresses, email addresses, link destinations, reference links, HTML `href` and `src` | an error |
| `code` | Inline code, fenced and indented blocks, front matter and HTML `code` or `pre` | an error |
| `quotes` | Two or more words inside double quotation marks; block quotations in Markdown and HTML | an error |
| `names` | Capitalised words and words shaped like identifiers | to review |
| `mentions` | A protected token stated more or fewer times than before | to review |
| `negation` | Each negative with the two words after it | to review |
| `modality` | Counts of words such as `may`, `must`, `if`, `only`, `until` | to review |
| `headings` | Markdown headings | to review |
| `typography` | Counts of curly quotation marks, em dashes and en dashes | to review |
| `sentences` | Original sentences with under half their content words left anywhere in the revision | to review |
| `vocabulary` | The share of content words that disappeared, when over a quarter | to review |
| `length` | Word count, when it falls below 60% or passes 125% | to review |

Exit 0 means no error-level difference, 1 means at least one, and 2 means an
input error. `--strict` also fails on differences to review, and the summary
line then reads `review before use`. The text report shows up to 60 characters
of a long token, starting near where it departs from its counterpart; `--json`
carries every token in full.

The comparison reads everything a reader sees. Block quotations, nested list
items and footnotes are compared here although the checker skips them, because
an edit can change a figure in any of them. A block quotation is compared twice:
its facts as prose and its wording as a quotation. In HTML, what a reader sees
includes the page title, image `alt` text, text inside an SVG and anything
marked only `aria-hidden`. Scripts, styles, templates, comments and elements
hidden with `hidden` or an inline style are left out, in HTML and in the tags a
Markdown file carries. Line endings, trailing spaces and the way a paragraph is
wrapped make no difference.

Forms that say the same thing match. Numbers up to ninety-nine written as
words equal their digits, so `three` equals `3` and `twenty-one` equals `21`.
`1,900` equals `1900`, `09:30` equals `9:30`, `5 ms` equals `5ms`, `5 per cent`
equals `5%`, `14th` equals `14` and `+5%` equals `5%`. `1 server` and `one
server` match when the same word stands beside both; `no one` never stands in
for a figure. An inline link, a reference link and an HTML anchor to one target
are the same link. A changed figure appears once as dropped and once as added.
A token counts as dropped only when it is gone entirely; a fact stated twice
and now once shows under `mentions`.

A minus sign, a currency such as `US$`, `am` or `pm` and the short units `k`,
`m`, `bn`, `x`, `ms`, `s` and `h` belong to their figure, so `-5%` against
`5%` or `5 ms` against `5 s` is a changed number. Code spans are compared with
their spacing collapsed and code blocks line by line; a block that differs only
in spacing says so.

Some tokens are ambiguous, and the comparison leans towards not blocking an
unchanged text:

- `May` and `March` count as dates beside a number or after a preposition, as
  in `in May` or `5th March`. Elsewhere they are read as words, so `May was
  slow` rewritten as `March was slow` shows under `names` and `modality` for
  review. Short forms such as `Jan` and `Thu` need a number beside them.
- A unit written as a word, or outside the short list above, is not part of
  the figure. `5 days` rewritten as `5 weeks` changes no token.
- A numbered line straight after paragraph text is read as that paragraph
  going on, unless it starts a list at 1 or follows a list item. Re-wrapping a
  list item can therefore leave a figure at the start of a line, where it is
  read as a marker and reported as dropped.
- A capitalised word that opens a sentence counts as a name unless it is a
  common opener such as `However`, or appears in lower case somewhere in the
  document. A name spelt like an ordinary word, opening every sentence it
  appears in, can be missed.
- A quotation of one word is not compared, because quotation marks around a
  single word usually mark a term. Single quotation marks are not read as
  quotations at all; they cannot be told from apostrophes.
- Four-space indented lines are code after a blank line, except under a list
  item, where they continue the item and are compared as prose.
- Of an element's attributes, only `href`, `src` and `alt` are compared. A
  link definition that nothing refers to is not compared.

The last three kinds measure how much was rewritten. A `sentences` line names
an original sentence that left little trace: find where its claim went, or
confirm it asserted nothing. A `vocabulary` line means the edit replaced much
of the wording, which is where claims go missing unnoticed. A `length` line
means the text shrank or grew past the limits in the table: check a large cut
for lost claims and a large gain for added ones.

Removing a contrast frame removes a negative, so a `negation` line is a prompt
to confirm that what went was staging and that any true half of the contrast
is still stated.

`--brief` treats the first file as the supplied facts: a brief, or the list
written before drafting. A draft may leave facts out or repeat them, so only
additions are reported: a figure, link, quotation or name the brief never
contained needs a source or has to go. A fact the brief gives in a code span, a
code block or front matter counts as supplied when the draft states it in prose.
The brief's own words count as supplied when the draft sets them as code or
quotes them.

## Differences

For each error line, either restore the original or be able to say why the
change is right: the user asked for it, the original was wrong and the user
confirmed the correction, or the claim is still stated in other words. Review
lines are for reading: a retitled heading or a removed contrast will appear
there, and so will an author's dashes or curly quotes that an edit flattened by
accident. Then read both versions, because the script compares tokens and cannot
see any of these:

- A possibility is not a commitment. `We may ship on Friday if Security
  approves` must not become `We will ship on Friday`.
- A proposal is not an approval. A proposed decision stays proposed.
- Scope holds. `In staging` must not widen to production, and `five customers
  said` must not become `customers say`.
- A report is not a measurement. People reporting easier searches is not
  evidence of faster searches.
- Sequence is not cause. `After the change, errors fell` is not `the change
  reduced errors`.
- Each action keeps its owner, its deadline and its condition. Business days,
  time zones and upper bounds survive.
- A procedure keeps its order and its approval boundary.

An example. The source:

> It is important to note that we may be able to ship on Friday, subject to
> Security approving the review. We have not approved the wider rollout.

A sound edit:

> We may be able to ship on Friday if Security approves the review. The wider
> rollout has not been approved.

The possibility, the dependency and the missing approval all survive. The
comparison would report one modality shift for the added `if`, which is the
kind of line to read and accept.

## Gaps in the source

A vague sentence often wants a specific that the source does not hold. Use a
detail only if it was supplied or you can point to where it is established.
Otherwise write the plainer sentence, or tell the user what is missing:

> The export handles large files well.

can become `The export handles large files` or a question about the size limit.
It cannot become a figure you guessed.
