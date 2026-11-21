#!/usr/bin/env python3
"""Check English prose for patterns worth editing. Standard library only; never edits input."""

from __future__ import annotations

import argparse
import bisect
import html
import json
import re
import statistics
import sys
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path

PROFILES = ("prose", "interface")


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    pattern: str
    advice: str
    cased: bool = False
    profiles: tuple[str, ...] = ("prose",)

    @property
    def category(self) -> str:
        return self.id.split(".", 1)[0]


EVERYWHERE = ("prose", "interface")
INTERFACE = ("interface",)

# Sentence-initial position, for patterns that are ordinary English mid-sentence.
# A line may open with a heading, list, quotation or table marker, and a
# sentence with a quotation mark, a bracket or emphasis.
LINE_LEAD = r"[ \t]*(?:(?:#{1,6}|[-*+>|]|\d{1,3}[.)])[ \t]+(?:\[[ xX]\][ \t]+)?)?"
WRAPPER = r"[\"'(\[]{0,2}(?:\*{1,3}|_{1,3})?"
OPENING = (
    rf"(?:^{LINE_LEAD}"
    r"|(?<=[.!?:;]\s)|(?<=[.!?:;][\"')\]*_]\s)|(?<=[.!?][\"')\]*_]{2}\s)|(?<=\|\s))"
    + WRAPPER
)
LEAD = re.compile(LINE_LEAD + WRAPPER)
# Parameters that chat tools append to the links they hand out.
TRACKING = r"utm_source=(?:chatgpt\.com|openai|copilot\.com|claude\.ai|perplexity)"
PLACEHOLDER = (
    r"(?:needs? (?:proof|source|number|citation)|citation needed|tbd|todo"
    r"|(?:insert|your|enter)[ :][^\]\n]{1,60})"
)

# Explicit inflections avoid matching unrelated words through guessed stems.
# Stock words are reported one by one. Word habits date within a model
# generation, so review this list whenever the calibration corpus changes.
STOCK = (
    r"delv(?:e|es|ed|ing)",
    r"tapestr(?:y|ies)",
    r"testaments?",
    r"realms?",
    r"beacons?",
    r"embark(?:s|ed|ing)?",
    r"pivotal",
    r"intricate(?:ly)?",
    r"intricac(?:y|ies)",
    r"meticulous(?:ly)?",
    r"underscor(?:e|es|ed|ing)",
    r"showcas(?:e|es|ed|ing)",
    r"foster(?:s|ed|ing)?",
    r"bolster(?:s|ed|ing)?",
    r"garner(?:s|ed|ing)?",
    r"multifaceted",
    r"nuanced",
    r"holistic(?:ally)?",
    r"myriad",
    r"plethora",
    r"paramount",
    r"interplay",
    r"underpin(?:s|ned|ning)?",
    r"cornerstones?",
    r"burgeoning",
    r"quintessential",
    r"overarching",
    r"commendable",
    r"noteworthy",
    r"indispensable",
    r"profound(?:ly)?",
    r"paradigms?",
    r"synerg(?:y|ies)",
    r"transformative",
    r"vibrant",
    r"bustling",
    r"nestled",
    r"renowned",
    r"daunting",
    r"landscapes?",
    r"journeys?",
    r"align(?:s|ed|ing)? with",
    r"utili[sz](?:e|es|ed|ing)",
    r"learnings",
    r"actionable",
    r"impactful",
    r"thought leaders?(?:hip)?",
    r"deep dives?",
    r"north star",
    r"load-bearing",
    r"earn(?:s|ed|ing)? (?:its|their|your) keep",
    r"mov(?:e|es|ed|ing) the needle",
    r"double(?:s|d)? down",
    r"doubling down",
    r"lean(?:s|ed|ing)? into",
    r"additionally",
    r"furthermore",
    r"moreover",
)
# Ordinary words that models overuse. One alone says nothing, so these are
# never reported singly; they only count towards a cluster.
COMMON = (
    r"crucial(?:ly)?",
    r"comprehensive(?:ly)?",
    r"enhanc(?:e|es|ed|ing|ement|ements)",
    r"vital",
    r"facilitat(?:e|es|ed|ing)",
    r"invaluable",
    r"valuable",
    r"insights?",
    r"emphasi[sz](?:e|es|ed|ing)",
    r"highlight(?:s|ed|ing)?",
    r"essential",
    r"ensur(?:e|es|ed|ing)",
    r"significant(?:ly)?",
)
PROMOTION = (
    r"seamless(?:ly)?",
    r"effortless(?:ly)?",
    r"empower(?:s|ed|ing)?",
    r"unlock(?:s|ed|ing)?",
    r"unleash(?:es|ed|ing)?",
    r"leverag(?:e|es|ed|ing)",
    r"harness(?:es|ed|ing)",
    r"streamlin(?:e|es|ed|ing)",
    r"elevat(?:e|es|ed|ing)",
    r"reimagin(?:e|es|ed|ing)",
    r"revolutioni[sz](?:e|es|ed|ing)",
    r"(?:super|turbo)charg(?:e|es|ed|ing)",
    r"game[ -]chang(?:er|ers|ing)",
    r"unparalleled",
    r"robust",
    r"bespoke",
    r"world[ -]class",
    r"cutting[ -]edge",
    r"state[ -]of[ -]the[ -]art",
    r"best[ -]in[ -]class",
    r"industry[ -]leading",
    r"groundbreaking",
    r"stunning",
    r"breathtaking",
    r"lightning[ -]fast",
    r"blazing(?:ly)?[ -]fast",
    r"powerful",
    r"intuitive",
    r"user[ -]friendly",
    r"easy[ -]to[ -]use",
    r"feature[ -]rich",
    r"battle[ -]tested",
    r"rock[ -]solid",
    r"enterprise[ -]grade",
    r"next[ -]gen(?:eration)?",
    r"frictionless",
    r"delightful",
    r"turnkey",
)
INTENSIFIERS = (
    r"genuinely",
    r"truly",
    r"quietly",
    r"undoubtedly",
    r"unquestionably",
    r"quite frankly",
    r"to be honest",
    r"deeply (?:committed|rooted|integrated|embedded|passionate|grateful|human|personal)",
    r"simply (?:press|click|run|add|open|type|enter|select|choose|install)",
)
# A trailing participle clause: comma, an -ing verb, then a function word, so
# "existing work" and "manufacturing sectors" are left alone. The excluded
# openers are prepositions in practice.
TAIL = (
    r",\s+(?:\w+ly\s+)?(?!including|according|regarding|depending|following|during"
    r"|excluding|considering|assuming|using|starting|beginning|something|anything"
    r"|nothing|everything|morning|evening)\w{4,}ing\s+"
    r"(?:a|an|the|its|their|his|her|my|our|your|that|how|what|in|to|on|for|from"
    r"|with|into|it|them|us|me|him|both|each|all|any|some|more|new|\w+ly)\b"
    r"[^.!?\n,;:]{0,80}[.!?]"
)


def words(alternatives: tuple[str, ...]) -> str:
    return r"\b(?:" + "|".join(alternatives) + r")\b"


RULES = (
    # Staging: the sentence signals importance instead of adding information.
    Rule(
        "staging.scene",
        "error",
        r"\bin today's (?:fast[ -]paced|ever[ -](?:evolving|changing)|rapidly (?:evolving|changing)|digital|modern|competitive|interconnected)(?: \w+)? (?:world|landscape|age|era|environment|economy|market)\b"
        r"|\bin (?:the|an|our) (?:ever[ -]|rapidly |constantly |fast[ -])(?:evolving|changing|paced) (?:world|landscape|field|age|era)\b"
        r"|\bin a world where\b|\b(?:imagine|picture|envision) a (?:world|future) (?:where|in which)\b"
        r"|\bnow more than ever\b",
        "Open with the subject and what this reader needs from it.",
    ),
    Rule(
        "staging.announcement",
        "error",
        r"\bit(?:'s| is) (?:important|worth|worthwhile|essential|crucial) (?:to (?:note|mention|remember|point out|highlight|emphasi[sz]e|keep in mind)|noting|mentioning|pointing out|highlighting|emphasi[sz]ing)\b"
        r"|\bit (?:should|must) be (?:noted|mentioned|emphasi[sz]ed)\b"
        r"|\b(?:needless to say|it goes without saying|without further ado)\b"
        r"|\bi just wanted to (?:take a moment to |quickly )?(?:reach out|let you know|touch base)\b"
        r"|\bwe(?:'re| are) (?:thrilled|excited|delighted|proud|humbled|pleased) to (?:announce|share|introduce|roll out|unveil|launch)\b",
        "Cut the announcement and keep the information.",
    ),
    Rule(
        "staging.runup",
        "error",
        r"\bhere(?:'s| is) the (?:thing|deal|kicker|catch|truth|reality|twist|bottom line|uncomfortable truth)\b"
        r"|\bhere(?:'s| is) (?:what|why|how) (?:you need to know|(?:that|this|it) (?:means|matters|looks like)|actually|really)\b"
        r"|\blet(?:'s| us) (?:dive|delve|dig|jump) (?:right |straight |deeper )?(?:in|into)\b"
        r"|\blet(?:'s| us) (?:break (?:this|that|it) down|unpack (?:this|that|it)|get into it|be (?:honest|real|clear))\b"
        r"|\blet me (?:be (?:clear|honest|direct|blunt)|break (?:this|that|it) down|paint a picture)\b"
        r"|\b(?:make no mistake|let that sink in|read that again|i'll say it again)\b",
        "Make the point; the reader does not need the run-up.",
    ),
    Rule(
        "staging.runup",
        "review",
        r"\bhere(?:'s| is) (?:what|why|where)\b"
        r"|\bwe heard you\b|\bwhether you(?:'re| are)\b",
        "Lead with the news or the instruction itself.",
    ),
    Rule(
        "staging.reveal",
        "error",
        OPENING
        + r"(?:(?:and|but|so),? )?the (?:result|secret|kicker|upshot|catch|twist|punchline|best part|worst part|bottom line|takeaway|verdict|payoff|irony|good news|bad news|short answer|honest answer)\?"
        r"|\b(?:plot twist|spoiler alert|hot take|real talk)\s*[:.!]",
        "State the result directly unless the question serves the reader.",
    ),
    Rule(
        "staging.reveal",
        "error",
        OPENING + r"(?:Honestly|Frankly|Seriously)\?",
        "State the result directly unless the question serves the reader.",
        cased=True,
    ),
    Rule(
        "staging.reveal",
        "review",
        OPENING
        + r"The (?:headline(?: number)?|bottom line|upshot|takeaway|short version|punchline|kicker|catch|lesson|result|good news|bad news)\s*:",
        "Give the fact itself; a label that promises a reveal delays it.",
        cased=True,
    ),
    Rule(
        "staging.concession",
        "error",
        r"\bnone of (?:this|that|which) (?:means|is to say|implies|suggests)\b",
        "Say what does hold, or name who believes the opposite.",
    ),
    Rule(
        "staging.concession",
        "review",
        r"\b(?:this|that|which)(?: is not|'s not| isn't) to (?:say|suggest|imply)\b"
        r"|\bdon't get me wrong\b|\bi'm not (?:saying|suggesting|arguing)\b",
        "Keep a concession the reader would raise; cut one nobody made.",
    ),
    Rule(
        "staging.strawman",
        "review",
        r"\b(?:some|many|critics|sceptics|skeptics) (?:might|may|will|would|could) (?:say|argue|object|counter|claim)\b"
        r"|\byou (?:might|may) (?:think|be thinking|be wondering|assume)\b"
        r"|\bone might (?:think|argue|assume|be tempted)\b"
        r"|\bit(?:'s| is| would be) (?:tempting|easy) to (?:think|assume|believe|dismiss)\b"
        r"|\bcontrary to popular belief\b|\bconventional wisdom (?:says|holds|suggests)\b"
        r"|\bwhile (?:everyone else|the (?:industry|competition|rest of the (?:industry|world))) (?:is|are|was|were)\b",
        "Keep an objection someone holds; cut a foil invented for contrast.",
    ),
    Rule(
        "staging.depth",
        "review",
        r"\bat its (?:core|heart)\b|\bat the (?:heart|core) of (?:it|this|the matter)\b"
        r"|\bthe (?:real|deeper|bigger|true|underlying) (?:question|issue|problem|story|lesson|point|answer|work|win) (?:is|here is|isn't|was)\b"
        r"|\bwhat (?:really|truly|actually) matters\b"
        r"|\bthe (?:uncomfortable|hard|simple|plain|inconvenient|honest|dirty) (?:truth|secret)\b"
        r"|\b(?:is|are|was|were|becomes?|became) the (?:language|currency|architecture|backbone|lifeblood|heartbeat|bedrock|north star|connective tissue|secret sauce) of\b"
        r"|\bthat(?:'s| is) not nothing\b|\bsit with (?:that|this)\b"
        r"|\b(?:what|the part) (?:nobody|no one) (?:tells you|talks about|mentions)\b",
        "Replace the saying with the specific claim it gestures at.",
    ),
    Rule(
        "staging.signpost",
        "review",
        r"\bthis matters\b|\bwhy (?:this|that|it) matters\b|\bthat (?:distinction|difference) matters\b"
        r"|\b(?:crucially|importantly|notably|interestingly|significantly|remarkably|tellingly),"
        r"|\bworth (?:noting|emphasi[sz]ing|highlighting|repeating|naming)\b"
        r"|\bkey takeaways?\b|\bthe key (?:insight|point|takeaway|lesson) (?:is|here)\b"
        r"|\bthat(?:'s| is) the (?:real|whole|key|actual|entire) (?:point|win|story|lesson|magic|secret|trick|difference)\b",
        "Show why it matters with the fact; drop the label.",
    ),
    Rule(
        "staging.closer",
        "error",
        r"\bthe future (?:looks|is|remains) (?:bright|promising|exciting)\b|\bonly time will tell\b"
        r"|\bone thing is (?:certain|clear|for sure)\b|\bthe possibilities are endless\b"
        r"|\bexciting times (?:lie |are )?ahead\b|\bthe (?:journey|work) (?:has only|is only|has) just begun\b"
        r"|\bthe best is yet to come\b",
        "End on the last concrete fact, or cut the closing line.",
    ),
    Rule(
        "staging.closer",
        "review",
        r"\bin (?:conclusion|summary|closing|essence)\b,|\bto (?:sum up|summari[sz]e|conclude|wrap up|recap)\b,"
        r"|\ball in all\b|\bat the end of the day\b|\bwhen all is said and done\b"
        r"|\bso,? (?:the )?next time you\b|\bas we (?:move|look) (?:forward|ahead)\b"
        r"|\band that(?:'s| is) (?:okay|ok)\b",
        "Check whether the ending repeats the piece; keep a real next step.",
    ),
    Rule(
        "staging.contrast",
        "review",
        r"\bnot (?:just|only|merely|simply) [^.!?\n]{1,100}?\bbut\b"
        r"|\b(?:it|this|that|they|he|she|we|you)(?:'s|'re| is| are| was| were) not (?:just |only |merely |simply |about |really )?[^.!?\n]{1,80}?[.!?;,—-]\s*(?:it|this|that|they|he|she|we|you)(?:'s|'re| is| are| was| were)\b"
        r"|\b(?:isn't|aren't|wasn't|weren't|is not|are not|was not|were not) (?:just |only |merely |simply |about |really )?[^.!?\n]{1,80}?[.!?;,—-]\s*(?:it|this|that|they)(?:'s|'re| is| are| was| were)\b"
        r"|\b(?:doesn't|does not|didn't|did not|don't|do not) [^.!?\n]{1,80}?\.\s+(?:it|they|we|that|this) (?:just|only|simply|merely) "
        r"|\bnot because\b[^.!?\n]{1,100}?[.,;]\s*(?:but )?(?:it(?:'s| is| was) )?because\b"
        r"|\b(?:doesn't|does not) mean\b[^.!?\n]{1,100}?\.\s+it means\b"
        r"|\bless about\b[^.!?\n]{1,60}?\bmore about\b"
        r"|\b(?:more than|rather than) (?:just|simply|merely)\b|\bnot (?:simply|merely)\b"
        r"|\bstops? being\b[^.!?\n]{1,60}?\bstarts? being\b",
        "Keep a contrast that corrects a belief the reader holds; otherwise state the point.",
    ),
    Rule(
        "staging.contrast",
        "review",
        r",\s+not\s+(?:just\s+|merely\s+|simply\s+)?(?:a\s+|an\s+|the\s+|another\s+|more\s+)?[^,.;:!?\n]{1,40}(?:[.!?]|$)",
        "Keep a contrast that corrects a belief the reader holds; otherwise state the point.",
    ),
    # Rhythm: shapes applied whether or not the meaning asks for them.
    Rule(
        "rhythm.negation",
        "error",
        r"\bno [\w'-]+(?: [\w'-]+){0,2}[.,;] no [\w'-]+(?: [\w'-]+){0,2}[.,;] (?:and |or )?no [\w'-]+",
        "Say what the thing is; a drumroll of negatives adds no claim.",
    ),
    # Inflation: ordinary facts dressed as significant.
    Rule(
        "inflation.significance",
        "error",
        r"\b(?:stands?|stood|serves?|served) as a (?:testament|reminder|beacon|symbol|cornerstone|catalyst)\b|\ba testament to\b"
        r"|\b(?:a|the) pivotal (?:moment|point|step)\b"
        r"|\brich (?:tapestry|cultural heritage)\b"
        r"|\b(?:ever[ -]|rapidly |constantly )(?:evolving|changing) (?:landscape|world)\b"
        r"|\bindelible mark\b|\b(?:lasting|enduring) legacy\b|\bwatershed moment\b"
        r"|\bthe dawn of a new\b|\bto the next level\b|\blike never before\b"
        r"|\bunlock(?:s|ed|ing)? (?:the |your |its |their )?(?:full |true )?(?:power|potential)\b",
        "State what happened and let the reader judge its weight.",
    ),
    Rule(
        "inflation.significance",
        "review",
        r"\bplay(?:s|ed|ing)? an? (?:crucial|key|pivotal|vital|significant|central|critical|integral) role\b"
        r"|\b(?:underscore[sd]?|underscoring|highlight(?:s|ed|ing)?) the (?:importance|significance|need)\b"
        r"|\bsetting the stage for\b|\bpav(?:e|es|ed|ing) the way for\b"
        r"|\bat the forefront of\b|\bpush(?:es|ed|ing)? the boundaries\b"
        r"|\ba step in the right direction\b|\ba (?:broader|larger|wider) (?:shift|trend|movement)\b",
        "Say what the role or effect is; keep the phrase only if that is all you know.",
    ),
    Rule(
        "inflation.vocabulary",
        "review",
        words(STOCK),
        "Prefer the plain word unless this one is the precise term.",
    ),
    Rule(
        "inflation.intensifier",
        "review",
        words(INTENSIFIERS),
        "Cut the intensifier, or say what makes the claim strong.",
    ),
    Rule(
        "inflation.copula",
        "review",
        r"\b(?:serves?|served|stands?|stood|functions?|functioned) as an?\b|\bboasts? (?:a|an|over|more than)\b",
        "Use is or has unless the verb states a real role.",
    ),
    Rule(
        "inflation.tail",
        "review",
        r",\s+(?:highlighting|underscoring|emphasi[sz]ing|showcasing|reflecting|symboli[sz]ing|illustrating|signall?ing|reinforcing|cementing|solidifying|fostering|demonstrating (?:its|their|the|how)|marking (?:a|an|the)|further \w+ing)\b",
        "Keep the fact; keep the trailing clause only if the source supports it.",
    ),
    Rule(
        "inflation.hedge",
        "review",
        r"\b(?:could|may|might|can) (?:potentially|possibly|perhaps|conceivably)\b"
        r"|\bpotentially (?:could|may|might)\b|\bit (?:could|might|may) be argued\b"
        r"|\b(?:may|might|could) (?:eventually|ultimately) \w+"
        r"|\bdoes not (?:by itself|in itself|on its own) (?:establish|prove|mean)\b",
        "Keep the one qualification that carries the actual uncertainty.",
    ),
    # Pitch: the text sells the subject where it should describe it.
    Rule(
        "pitch.praise",
        "review",
        words(PROMOTION),
        "Name the capability or give the figure; keep literal and technical uses.",
    ),
    Rule(
        "pitch.benefit",
        "review",
        r"\b(?:helps?|lets?|allows?|enables?|empowers?) (?:you|your (?:\w+ )?(?:team|users|customers|business|organi[sz]ation|company)|teams|developers|businesses|anyone|everyone)\b"
        r"|\bso (?:that )?you (?:can|don't have to|never have to)\b"
        r"|\bmak(?:e|es|ing) it (?:easy|simple|effortless|painless|a breeze) (?:to|for)\b|\beasier than ever\b"
        r"|\bwithout the (?:hassle|headache|pain|complexity|guesswork|stress|overhead|bloat|fuss)\b"
        r"|\b(?:hassle|pain|worry|stress|friction)[ -]free\b|\bsay goodbye to\b"
        r"|\b(?:all|everything) you need\b|\ball[ -]in[ -]one\b|\bone[ -]stop\b"
        r"|\bpeace of mind\b|\bfocus on what (?:matters|you do best)\b|\btake (?:full |back )?control of\b"
        r"|\bstay (?:on top of|ahead of|in control)\b|\bwith (?:confidence|ease)(?=[.,;:!?)]|\s*$)"
        r"|\b(?:built|designed|made|crafted|engineered) (?:for|with) (?:\w+ ){0,3}in mind\b|\bfrom the ground up\b"
        r"|\byou(?:'ll| will) (?:love|never|always)\b|\byour \w+ (?:will thank you|deserves?)\b"
        r"|\b(?:works?|runs?) (?:where(?:ver)?|the way|how) you (?:work|do)\b"
        r"|\bin (?:seconds|minutes|no time|just (?:a few |\w+ )?(?:clicks?|steps?|minutes?|seconds?|lines?))\b",
        "Say what it does; the reader can work out what that is worth.",
    ),
    Rule(
        "pitch.call",
        "review",
        r"\bget started (?:today|now|in (?:seconds|minutes)|for free)\b|\b(?:try|start) (?:it|\w+) (?:today|now|for free)\b"
        r"|\bsign up (?:today|now|for free)\b|\bready to \w+[^.!?\n]{0,60}\?|\bwhat are you waiting for\b"
        r"|\blook no further\b|\bdon't miss\b|\bjoin (?:thousands|hundreds|millions)\b|\bgive it a try\b|\bcheck it out\b",
        "Give the next step once, as an instruction.",
    ),
    # Leftovers: chat wrappers and drafting moves never meant for the reader.
    Rule(
        "leftovers.chat",
        "error",
        r"\b(?:great|excellent|good|fantastic|wonderful) question\b[!.,]"
        r"|\byou(?:'re| are) absolutely right\b|\bi(?:'d| would) be happy to (?:help|assist)\b"
        r"|\bwould you like me to\b|\bshould i (?:continue|proceed|go ahead)\b"
        r"|\bhere(?:'s| is) (?:a|an|the|your) (?:revised|rewritten|polished|updated|improved|cleaned[ -]up|more concise) (?:version|draft)\b"
        r"|\bas an ai (?:language model|assistant|model)\b|\bas an ai, i\b"
        r"|\bas a large language model\b",
        "Remove the chat wrapper and keep the content.",
        profiles=EVERYWHERE,
    ),
    Rule(
        "leftovers.chat",
        "error",
        OPENING + r"(?:Certainly|Absolutely|Of course|Sure thing)!",
        "Remove the chat wrapper and keep the content.",
        cased=True,
        profiles=EVERYWHERE,
    ),
    Rule(
        "leftovers.courtesy",
        "review",
        r"\b(?:i )?hope this helps\b|\blet me know if you(?:'d| would) like\b"
        r"|\bfeel free to (?:reach out|ask|let me know)\b|\bwant me to \w+",
        "Keep a sign-off the relationship calls for; cut an assistant's offer.",
    ),
    Rule(
        "leftovers.cutoff",
        "error",
        r"\bas of my (?:last|latest|most recent) (?:knowledge |training )?(?:update|cutoff|cut-off)\b"
        r"|\bmy (?:knowledge|training) (?:cutoff|cut-off)\b|\bup to my last (?:training|update)\b"
        r"|\bi (?:don't|do not) have (?:access to )?real[ -]time\b"
        r"|\bbased on (?:the )?(?:available|provided) (?:information|sources|context)\b"
        r"|\bspecific details (?:are|remain) (?:limited|scarce|unclear)\b"
        r"|\bin the (?:provided|given) (?:text|sources|context|document)\b",
        "Say what the source does not show, or remove the sentence.",
        profiles=EVERYWHERE,
    ),
    Rule(
        "leftovers.markup",
        "error",
        r"citeturn\d|contentReference\[oaicite|oai_citation|\[attached_file:\d+\]|grok_card|"
        + TRACKING,
        "Strip the tool's markup; supply the real reference or flag the gap.",
        profiles=EVERYWHERE,
    ),
    Rule(
        "leftovers.placeholder",
        "error",
        # A link's text is not a placeholder, so "[Your account](...)" and
        # "[Insert menu][ref]" pass; two placeholders side by side do not.
        rf"\[{PLACEHOLDER}\](?!\(|\[(?!\^|{PLACEHOLDER}\]))",
        "Resolve the placeholder before publication; never fill it by guessing.",
        profiles=EVERYWHERE,
    ),
    Rule(
        "leftovers.reasoning",
        "error",
        r"\blet(?:'s| me| us) think (?:this through )?step[ -]by[ -]step\b"
        r"|\bhere(?:'s| is) my (?:thought process|reasoning|thinking)\b"
        r"|\bto approach this systematically\b",
        "Keep the reasoning the reader needs; cut the scaffolding.",
    ),
    Rule(
        "leftovers.meta",
        "review",
        r"\bin this (?:article|post|guide|essay|piece|blog post),? (?:we|i)(?:'ll| will)\b"
        r"|\bthis (?:article|post|guide|essay) (?:will )?(?:explores?|delves?|dives?|examines?|covers?|walks?)\b"
        r"|\bthe rest of this (?:essay|post|article|piece)\b"
        r"|\bwas (?:added|introduced|rewritten|refactored) to replace\b",
        "Describe the subject; mention the document only where the reader needs it.",
    ),
    # Evidence: claims the checker cannot verify.
    Rule(
        "evidence.numbers",
        "review",
        r"(?<![\d,.])\d[\d,]*(?:\.\d+)?\+?\s+(?:(?:active|happy|paying|satisfied)\s+)?(?:customers?|users?|clients?|subscribers?|teams?)\b"
        r"|(?<![\d.])\d+(?:\.\d+)?\s*%\s+(?:faster|cheaper|growth|increase|reduction)\b",
        "Verify the source, scope and measurement; a number is not evidence of fabrication.",
    ),
    Rule(
        "evidence.attribution",
        "review",
        r"\b(?:experts|analysts|researchers|scientists|observers) (?:say|believe|agree|argue|warn|suggest|note|recommend|predict)\b"
        r"|\b(?:studies|surveys) (?:show|suggest|indicate|have shown|confirm|reveal)\b|\bresearch (?:shows|suggests|indicates|has shown|confirms)\b"
        r"|\baccording to (?:experts|studies|research|analysts|industry (?:experts|reports))\b"
        r"|\bit(?:'s| is) (?:widely|generally|commonly|often) (?:believed|accepted|regarded|recogni[sz]ed|acknowledged)\b"
        r"|\bindustry (?:leaders|experts|observers|analysts) (?:say|agree|believe|predict)\b",
        "Name the source and what it found, or cut the claim.",
    ),
    # Interface copy: one string per line; register is the whole signal.
    Rule(
        "interface.figure",
        "review",
        r"\bat a glance\b|\bwhere (?:the |your )?\w+ (?:went|goes|go)\b|\b(?:adds? to|the (?:big|full|whole)) (?:the )?picture\b"
        r"|\bstands? out\b|\btells? (?:the|a|your) story\b|\byour \w+ journey\b|\bdive in(?:to)?\b"
        r"|\bstay sharp\b|\blevel up\b|\bget going\b|\bin no time\b|\ba breeze\b|\bmagic(?:al|ally)?\b",
        "Say the number or the thing; a figure of speech hides it.",
        profiles=INTERFACE,
    ),
    Rule(
        "interface.filler",
        "review",
        r"\b(?:simply|easily|quickly|successfully|seamlessly|effortlessly)\b|\bplease note\b|\bin order to\b"
        r"|\b(?:oops|whoops|uh[ -]oh|yikes)\b",
        "Cut the filler; the label should carry only what the reader acts on.",
        profiles=INTERFACE,
    ),
    Rule(
        "interface.heading",
        "review",
        r"^(?:Where|Why|How|What|When|Who)\b(?:(?: [^\s?]+){1,6}| \w+\?)$",
        "A heading is a label: name what the section holds.",
        cased=True,
        profiles=INTERFACE,
    ),
    Rule(
        "interface.shorthand",
        "review",
        r"(?:\bover|:)\s+(?:your |the |last |past )*\d+\s*$",
        "Say what the number counts; do not compress to the data model.",
        profiles=INTERFACE,
    ),
)

COMPUTED = {
    "staging.contrasts": (
        "error",
        "Contrast frames recur; state most of these points directly.",
    ),
    "rhythm.repeat": (
        "error",
        "Remove the repeated sentence or supply its distinct information.",
    ),
    "rhythm.fragments": (
        "review",
        "Fold the fragments into a sentence that makes a claim.",
    ),
    "rhythm.closers": (
        "review",
        "Several paragraphs end on a short punch line; let most end on their last fact.",
    ),
    "rhythm.questions": (
        "review",
        "Keep a question the reader is asking; answer or cut the rest.",
    ),
    "rhythm.dashes": (
        "review",
        "Three interruptions in one sentence; split it or choose other punctuation.",
    ),
    "rhythm.uniform": (
        "review",
        "Sentences run at one length; let the content set it, without chopping fragments.",
    ),
    "density.signals": (
        "error",
        "Small signals are dense; edit the passages that draw several, then check again.",
    ),
    "inflation.cluster": (
        "error",
        "Stock words cluster here; rewrite the passage in plain terms.",
    ),
    "inflation.tails": (
        "error",
        "Trailing -ing clauses recur; give each fact its own verb or cut the gloss.",
    ),
    "pitch.heading": (
        "review",
        "A heading is a label: name what the section holds.",
    ),
    "pitch.headings": (
        "error",
        "Headings address or sell to the reader; replace them with labels.",
    ),
    "particulars.share": (
        "review",
        "Few sentences name a thing or give a figure; state the particular or cut the sentence.",
    ),
    "particulars.run": (
        "review",
        "No number, name, code or link in this run; say what it refers to, or cut it.",
    ),
    "formatting.labels": (
        "review",
        "Bold labels open most list items; keep labels that carry information.",
    ),
    "formatting.bold": (
        "review",
        "Bold is everywhere; keep it for the few terms a skimming reader needs.",
    ),
    "formatting.titlecase": (
        "review",
        "Use sentence case unless the house style sets title case.",
    ),
    "formatting.instructions": (
        "review",
        "Label the section and keep the instruction in its steps, unless the headings are the steps.",
    ),
    "formatting.rules": (
        "review",
        "Drop the horizontal rules; headings already separate the sections.",
    ),
    "formatting.hashtags": (
        "review",
        "Keep the two or three tags a reader would search for.",
    ),
    "formatting.emoji": (
        "review",
        "Remove decorative emoji from headings and list items.",
    ),
    "interface.pair": (
        "review",
        "Two clipped sentences read as an aphorism; state the fact once.",
    ),
}
RULE_IDS = {rule.id for rule in RULES} | set(COMPUTED)
NORMALISE = str.maketrans(
    {"’": "'", "‘": "'", "“": '"', "”": '"', "‑": "-", "–": "-", "\xa0": " "}
)
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
# Starting only at the head of a punctuation run keeps a long run linear.
BOUNDARY = re.compile(r"(?<![.!?])[.!?]+[\"')\]*_]*(?=\s+[\"'(\[*_]*[A-Z0-9])")
ABBREVIATION = re.compile(
    r"\b(?:e\.g|i\.e|vs|cf|approx|Mr|Mrs|Ms|Dr|St|Fig|Inc|Ltd)\.$"
)
BLOCK_KINDS = (
    ("heading", re.compile(r"[ \t]{0,3}#{1,6}[ \t]")),
    ("item", re.compile(r"[ \t]*(?:[-*+]|\d{1,3}[.)])[ \t]")),
    ("table", re.compile(r"[ \t]*\|")),
)
EMOJI = re.compile("[\U0001f000-\U0001faff☀-➿⬀-⯿]")
SMALL_WORDS = frozenset(
    "a an and as at but by for from in into nor of on or per the to vs via with".split()
)
BOLD = re.compile(r"\*\*[^*\n]{1,80}\*\*")
BOLD_LABEL = re.compile(r"[ \t]*(?:[-*+]|\d{1,3}[.)])[ \t]+\*\*[^*\n]{1,60}\*\*")
RULE_LINE = re.compile(r"[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*")
HASHTAGS = re.compile(r"(?<![\w#])#[A-Za-z]\w+(?:\s+#[A-Za-z]\w+){3,}")
HEADING_MARK = re.compile(r"[ \t]{0,3}#{1,6}[ \t]+(?:\d{1,3}[.)][ \t]+)?")
# A heading that invites, addresses or teases the reader, or reads as a slogan.
PITCH_HEADING = re.compile(
    r"(?:Try|Discover|Explore|Meet|Unlock|Unleash|Enjoy|Experience|Join|Ditch|Boost"
    r"|Supercharge|Transform|Imagine|Introducing|Welcome to|Say (?:goodbye|hello)|Get)\b"
    r"|(?:Why|What|Where|When|Who|How)\b(?! to\b)[ \t]+\S[^?\n]*$"
    r"|(?:Ready|Tired|Want|Need|Looking|Still|Struggling|Sick)\b[^\n]*\?$"
    r"|(?:\S+[ \t]+){2,}\S*[A-Za-z)\"'][.!]$"
    r"|[^\n]*\b(?:you|your|yours|you're|you'll|you've)\b",
    re.I,
)
# A heading that gives an instruction. Words that are also nouns count only
# before a determiner, so "Build instructions" and "Use cases" stay labels.
ACTION = (
    "install|configure|create|add|compare|verify|choose|write|make|find|read|ask|keep"
    "|protect|deploy|remove|delete|enable|disable|define|open|close|save|connect"
    "|publish|recover|put|give|take|bring|manage|send|clone|convert|generate|avoid"
    "|prefer|treat|execute|separate|declare|know|learn|follow|apply|select|specify"
    "|provide|include|exclude|combine|validate|migrate|uninstall|contribute"
)
ACTION_OR_NOUN = (
    "run|build|use|set|check|test|start|stop|update|upgrade|download|upload|import"
    "|export|fix|debug|review|report|share|sign|log|edit|change|call|pass|return"
    "|store|scale|handle|monitor|pick|turn|do|query|filter|sort|release"
)
DETERMINER = (
    r"(?:the|a|an|your|our|this|that|these|those|it|them|each|every|all|any|one|some)\b"
)
INSTRUCTION_HEADING = re.compile(
    rf"(?:{ACTION})[ \t]+(?:{DETERMINER}|(?:from|with|to|in|on|as|for|by|up|out|and)\b)"
    rf"|(?:{ACTION_OR_NOUN})[ \t]+{DETERMINER}"
    r"|(?:install|configure|verify|publish|uninstall|deploy|contribute|migrate)$",
    re.I,
)
# What a reader could check or act on: a figure, a quotation, an acronym or a
# name after the first word. Code and links are read from the source, where
# masking has not blanked them.
PARTICULAR = re.compile(
    r"\d|\"[^\"\n]{3,}\"|\b[A-Z]{2,}|(?<=[a-z0-9,;)\]] )[\"'(\[]?[A-Z][A-Za-z]"
)
LITERAL = re.compile(r"`|\]\(|\]\[|https?://|<(?:a|code|kbd|samp|var)\b", re.I)
ITEM_MARK = re.compile(r"[ \t]*(?:[-*+]|\d{1,3}[.)])[ \t]+(?:\[[ xX]\][ \t]+)?")

# Accumulation thresholds, set against the corpora described in docs/validation.md.
CLUSTER_WINDOW = 100
CLUSTER_MINIMUM = 4
TAIL_MINIMUM = 3
TAIL_RATE = 3.0
CONTRAST_MINIMUM = 3
CONTRAST_RATE = 4.0
UNIFORM_SENTENCES = 12
UNIFORM_VARIATION = 0.30
DENSITY_MINIMUM = 6
DENSITY_RATE = 10.0
PITCH_HEADINGS = 3
PITCH_HEADING_SHARE = 0.25
# Sentences of four words or more in paragraphs and list items are counted.
PARTICULAR_SENTENCES = 12
PARTICULAR_SHARE = 0.35
PARTICULAR_RUN = 4
# Evidence findings ask for a source, whether formatting is decoration depends
# on the document's format, and narrative legitimately carries few particulars.
UNCOUNTED = ("evidence", "formatting", "particulars")


@dataclass(frozen=True)
class Finding:
    rule: str
    category: str
    severity: str
    line: int
    column: int
    text: str
    advice: str
    allowance: str | None = None


@dataclass
class Prose:
    text: str
    positions: list[int]


@dataclass(frozen=True)
class Sentence:
    start: int
    end: int
    words: int


@dataclass(frozen=True)
class Block:
    kind: str
    start: int
    end: int
    sentences: tuple[Sentence, ...]


def blank(value: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in value)


# A link destination with balanced parentheses, as in /docs/function(a), and an
# optional title. Two nesting levels and a bounded length keep matching linear.
DESTINATION = re.compile(
    r"\]\((?:[^()\\]|\\.|\((?:[^()\\]|\\.|\([^()]{0,500}\)){0,500}\)){0,1000}\)",
    re.S,
)


# Markdown reads "<" as markup only where it opens a whole tag, as CommonMark
# does: the attributes must parse and no blank line may fall inside the tag.
# So "n<k for every shard" is text, however far away the next ">" is.
GAP = r"(?:[ \t]+(?:\n[ \t]*)?|\n[ \t]*)"
VALUE = r"""(?:[^\s"'=<>`]+|'[^'\n]{0,500}'|"[^"\n]{0,500}")"""
TAG = re.compile(
    rf"<(?:[A-Za-z][A-Za-z0-9-]*(?:{GAP}[A-Za-z_:][\w.:-]*(?:[ \t]*=[ \t]*{VALUE})?)*"
    rf"(?:{GAP})?/?>"
    r"|/[A-Za-z][A-Za-z0-9-]*[ \t\n]*>"
    r"|[!?][A-Za-z][^<>\n]{0,500}>)"
)
# Stands in for a literal "<" while the HTML parser runs, then is restored.
LITERAL_LESS_THAN = "\ue000"
NEWLINE = re.compile(r"\r\n?")
# Front matter opens with a key, after any comments; a bare rule opens prose.
FRONT_MATTER = re.compile(
    r"\A---[ \t]*\n(?:[ \t]*(?:#[^\n]*)?\n)*[ \t]*[A-Za-z_][\w.-]*[ \t]*:"
    r".*?\n(?:---|\.\.\.)[ \t]*(?:\n|\Z)",
    re.S,
)
# "[label]: target", with an optional title and nothing else on the line.
DEFINITION = re.compile(
    r" {0,3}\[(?!\^)([^\]\n]{1,500})\]:[ \t]*(<[^<>\n]*>|\S+)"
    r"(?:[ \t]+(\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\)))?[ \t]*\n?"
)
ORDERED = re.compile(r"[ \t]*(\d{1,3})[.)][ \t]")


def blank_link(value: str) -> str:
    """Blank a link target but keep a tracking parameter visible to the rules."""
    kept = list(blank(value))
    for found in re.finditer(TRACKING, value, re.I):
        kept[found.start() : found.end()] = found[0]
    return "".join(kept)


def literal_markup(text: str, markdown: bool) -> str:
    """Stand in for each "<" that is text, so the HTML parser leaves it alone.

    An unfinished comment or declaration is text in every format: parsers
    disagree about it, and read as markup it would hide the rest of the document.
    """
    if not markdown:
        # A marked section such as <![endif]> is a comment to a browser.
        text = re.sub(r"<!\[[^<>]{0,200}>", lambda match: blank(match[0]), text)
    last_end = text.rfind(">")
    last_comment_end = text.rfind("-->")

    def markup(index: int) -> bool:
        if text.startswith("<!--", index):
            return last_comment_end >= index + 2
        if markdown:
            return text[index - 1 : index] != "\\" and bool(TAG.match(text, index))
        return last_end > index and not text.startswith("<![", index)

    return "".join(
        char if char != "<" or markup(index) else LITERAL_LESS_THAN
        for index, char in enumerate(text)
    )


def markdown_mask(source: str) -> str:
    """Mask common literal Markdown forms without changing source offsets."""
    text = source
    front = FRONT_MATTER.match(text)
    if front:
        text = blank(front[0]) + text[front.end() :]
    lines = text.splitlines(keepends=True)
    fence: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        opener = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            lines[index] = blank(line)
            if re.fullmatch(
                r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*\n?",
                line,
            ):
                fence = None
        elif opener:
            fence = (opener[1][0], len(opener[1]))
            lines[index] = blank(line)
        elif re.match(r"^(?: {0,3}>| {4}|\t)", line):
            lines[index] = blank(line)
        # A footnote definition is prose; a reference definition is a link target.
        elif DEFINITION.fullmatch(line):
            lines[index] = blank_link(line)
    text = "".join(lines)
    for pattern in (
        # A code span may wrap across lines but never across a blank line. It
        # opens only at the head of a backtick run, which keeps a long run linear.
        r"(?<!`)(`+)(?!`)(?:(?!\n[ \t]*\n).)*?(?<!`)\1(?!`)",
        r"~~[^\n]*?~~",
        r"<[^<>\s]+@[^<>\s]+>",
    ):
        text = re.sub(pattern, lambda m: blank(m[0]), text, flags=re.S)
    text = re.sub(r"<https?://[^>\n]+>", lambda m: blank_link(m[0]), text)
    # The brackets stay so a link label is never mistaken for a placeholder.
    text = DESTINATION.sub(lambda m: "](" + blank_link(m[0][2:-1]) + ")", text)
    # A reference label is a link target too; a placeholder or footnote mark in
    # that position is not one. Bounded labels keep a line of unclosed brackets
    # from scanning quadratically.
    return re.sub(
        r"(\[[^\]\n]{1,500}\])\[([^\]\n]{0,500})\]",
        lambda m: m[0]
        if re.fullmatch(rf"\^.*|{PLACEHOLDER}", m[2], re.I)
        else m[1] + "[" + blank(m[2]) + "]",
        text,
    )


def concealed(values: dict[str, str | None]) -> bool:
    """True when an element's own attributes keep it off the page."""
    return "hidden" in values or bool(
        re.search(
            r"(?:display\s*:\s*none|visibility\s*:\s*hidden)\b",
            values.get("style") or "",
            re.I,
        )
    )


class Elements(HTMLParser):
    """Follow the open elements of a document.

    An element ends at its end tag, with an ancestor, or where HTML lets the
    author leave the end tag out. A subclass decides what leaving one means.
    """

    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    BLOCK = {
        "p",
        "div",
        "section",
        "article",
        "header",
        "footer",
        "main",
        "li",
        "ul",
        "ol",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "br",
        "hr",
        "tr",
        "td",
        "th",
        "blockquote",
    }
    PARAGRAPH = ({"p"}, BLOCK - {"p"})
    # A start tag ends an open element of the same group, unless one of the
    # containers is nearer: "<li>" ends the item before it, not the item
    # around the list it sits in.
    SIBLINGS = (
        PARAGRAPH,
        ({"li"}, {"ul", "ol", "menu"}),
        ({"dt", "dd"}, {"dl"}),
        ({"td", "th"}, {"tr", "table"}),
        ({"tr"}, {"table", "thead", "tbody", "tfoot"}),
        ({"thead", "tbody", "tfoot"}, {"table"}),
        ({"option"}, {"select", "datalist", "optgroup"}),
        ({"optgroup"}, {"select", "datalist"}),
        ({"a"}, {"table", "td", "th"}),
    )
    ENDS_PARAGRAPH = {
        "address",
        "article",
        "aside",
        "blockquote",
        "dd",
        "details",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "menu",
        "nav",
        "ol",
        "pre",
        "section",
        "table",
        "ul",
    }

    def __init__(self, convert_charrefs: bool = False) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.stack: list[tuple[str, object]] = []
        # Where each open element sits on the stack, by name, so that ending
        # one never means searching the stack.
        self.open: dict[str, list[int]] = {}

    def nearest(self, tags: set[str]) -> int:
        """Stack index of the innermost open element with one of these names."""
        return max(
            (self.open[tag][-1] for tag in tags if self.open.get(tag)), default=-1
        )

    def enter(self, tag: str, state: object = None) -> None:
        self.open.setdefault(tag, []).append(len(self.stack))
        self.stack.append((tag, state))

    def leave(self, tag: str, state: object) -> None:
        """Called for each element that ends, innermost first."""

    def end(self, index: int) -> None:
        while len(self.stack) > index:
            tag, state = self.stack.pop()
            self.open[tag].pop()
            self.leave(tag, state)

    def imply_end(self, tag: str) -> None:
        """End whatever this start tag ends without an end tag of its own."""
        groups = [group for group in self.SIBLINGS if tag in group[0]]
        if tag == "body":
            groups.append(({"head"}, set()))
        if tag in self.ENDS_PARAGRAPH:
            groups.append(self.PARAGRAPH)
        for members, containers in groups:
            index = self.nearest(members)
            if index > self.nearest(containers):
                self.end(index)

    def handle_endtag(self, tag: str) -> None:
        if self.open.get(tag):
            self.end(self.open[tag][-1])


class ProseHTML(Elements):
    """Extract static HTML text, mapping decoded entities back to source locations."""

    SKIP = {"head", "script", "style", "template", "pre", "code", "svg", "noscript"}

    def __init__(self, source: str):
        super().__init__()
        self.source = source
        self.starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self.chars: list[str] = []
        self.positions: list[int] = []

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.starts[line - 1] + column

    def boundary(self) -> None:
        self.chars.append("\n")
        self.positions.append(self.source_offset())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.imply_end(tag)
        values = dict(attrs)
        skipped = (
            tag in self.SKIP
            or concealed(values)
            or (values.get("aria-hidden") or "").lower() == "true"
        )
        if tag in self.BLOCK:
            self.boundary()
        # What a skipped element holds is written, then cut where the element
        # ends. One that never ends is read: a tag named in passing, such as
        # "the <pre> element", must not hide the rest of the document.
        mark = len(self.chars) if skipped else None
        if not skipped:
            # Attributes are not prose, but a tracking parameter in one is a leftover.
            origin = self.source_offset()
            for found in re.finditer(TRACKING, self.get_starttag_text() or "", re.I):
                start, end = origin + found.start(), origin + found.end()
                self.chars.extend(f" {found[0]} ")
                self.positions.extend([start, *range(start, end), end - 1])
        if tag not in self.VOID:
            self.enter(tag, mark)

    def leave(self, tag: str, mark: object) -> None:
        if mark is not None:
            del self.chars[mark:]
            del self.positions[mark:]
        if tag in self.BLOCK or tag in self.SKIP:
            self.boundary()

    def handle_data(self, data: str) -> None:
        self.chars.extend(data)
        self.positions.extend(
            range(self.source_offset(), self.source_offset() + len(data))
        )

    def entity(self, token: str) -> None:
        # "R&D." has no semicolon, so none may be added when it is not an entity.
        end = self.source_offset() + len(token)
        closed = self.source[end : end + 1] == ";"
        decoded = html.unescape(token + (";" if closed else ""))
        self.chars.extend(decoded)
        self.positions.extend([self.source_offset()] * len(decoded))

    def handle_entityref(self, name: str) -> None:
        self.entity("&" + name)

    def handle_charref(self, name: str) -> None:
        self.entity("&#" + name)


def extract(source: str, format: str) -> Prose:
    if format == "text":
        return Prose(source, list(range(len(source))))
    markdown = format == "markdown"
    masked = literal_markup(markdown_mask(source) if markdown else source, markdown)
    parser = ProseHTML(masked)
    parser.feed(masked)
    parser.close()
    text = "".join(parser.chars).replace(LITERAL_LESS_THAN, "<")
    return Prose(text, parser.positions)


def infer_format(path: str, requested: str = "auto") -> str:
    if requested != "auto":
        return requested
    suffix = Path(path).suffix.lower()
    return (
        "markdown"
        if suffix in {".md", ".markdown", ".mdown"}
        else "html"
        if suffix in {".html", ".htm"}
        else "text"
    )


def allowances(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        rule, separator, reason = value.partition("=")
        if not separator or rule not in RULE_IDS or not reason.strip():
            raise ValueError(
                "--allow requires a known rule ID and a nonempty reason: RULE=REASON"
            )
        result[rule] = reason.strip()
    return result


def block_kind(line: str) -> str:
    for kind, marker in BLOCK_KINDS:
        if marker.match(line):
            return kind
    return "paragraph"


def hard_wrapped(text: str) -> bool:
    """Plain text wraps paragraphs across lines when no line is long and some block has several."""
    lines = text.split("\n")
    if any(len(line) > 100 for line in lines):
        return False
    run = longest = 0
    for line in lines:
        run = run + 1 if line.strip() else 0
        longest = max(longest, run)
    return longest >= 3


def line_kinds(lines: list[str]) -> list[str]:
    """The kind of each line, read in the light of the lines above it.

    A numbered line directly under paragraph text carries the paragraph on, as
    in "the team grew from 12 to" / "42. Next year it doubles", unless it
    starts a list at 1. CommonMark draws the same line.
    """
    kinds = []
    listed = False
    previous = "blank"
    for line in lines:
        kind = block_kind(line) if line.strip() else "blank"
        if kind == "blank":
            listed = False
        elif kind == "item":
            number = ORDERED.match(line)
            if number and number[1] != "1" and previous == "paragraph" and not listed:
                kind = "paragraph"
            else:
                listed = True
        kinds.append(kind)
        previous = kind
    return kinds


def flow(text: str, format: str, profile: str) -> str:
    """Turn soft line breaks into spaces without changing offsets."""
    if profile == "interface" or (format == "text" and not hard_wrapped(text)):
        return text
    lines = text.split("\n")
    kinds = line_kinds(lines)
    joined = []
    for index, line in enumerate(lines[:-1]):
        soft = (
            kinds[index] not in ("blank", "heading", "table")
            and kinds[index + 1] == "paragraph"
        )
        joined.append(line + (" " if soft else "\n"))
    joined.append(lines[-1])
    return "".join(joined)


def sentences(text: str, offset: int) -> tuple[Sentence, ...]:
    found = []
    start = 0
    ends = [
        match.end()
        for match in BOUNDARY.finditer(text)
        if not ABBREVIATION.search(text, max(0, match.end() - 8), match.end())
    ]
    for end in [*ends, len(text)]:
        chunk = text[start:end]
        count = len(WORD.findall(chunk))
        if count:
            lead = len(chunk) - len(chunk.lstrip())
            found.append(
                Sentence(
                    offset + start + lead, offset + start + len(chunk.rstrip()), count
                )
            )
        start = end
    return tuple(found)


def blocks(flowed: str) -> list[Block]:
    result = []
    for match in re.finditer(r"[^\n]+", flowed):
        if match[0].strip():
            result.append(
                Block(
                    block_kind(match[0]),
                    match.start(),
                    match.end(),
                    sentences(match[0], match.start()),
                )
            )
    return result


def stem(word: str) -> str:
    return re.sub(r"(?:ing|ed|es|ly|s|e|y)$", "", word.casefold())[:6]


def clusters(
    hits: list[tuple[int, int]], text: str, window: int, minimum: int
) -> list[list[tuple[int, int]]]:
    """Group hits where `minimum` distinct words fall within `window` words."""
    token_starts = [match.start() for match in WORD.finditer(text)]
    indexed = sorted(
        (bisect.bisect_right(token_starts, start), start, end) for start, end in hits
    )
    stems = [stem(text[start:end]) for _, start, end in indexed]
    found = []
    # The window slides: hits enter at `last` and leave at `first`, so a long
    # run of one word is counted once and not once for every hit in it.
    inside: dict[str, int] = {}
    first = last = 0
    while first < len(indexed):
        while last < len(indexed) and indexed[last][0] - indexed[first][0] < window:
            inside[stems[last]] = inside.get(stems[last], 0) + 1
            last += 1
        if len(inside) >= minimum:
            found.append([(start, end) for _, start, end in indexed[first:last]])
            inside.clear()
            first = last
        else:
            inside[stems[first]] -= 1
            if not inside[stems[first]]:
                del inside[stems[first]]
            first += 1
    return found


def title_case(heading: str) -> bool:
    tokens = [word for word in WORD.findall(heading) if word[0].isalpha()]
    if len(tokens) < 3:
        return False
    significant = [word for word in tokens[1:] if word.casefold() not in SMALL_WORDS]
    plain = [word for word in significant if not word.isupper() and word[1:].islower()]
    return len(plain) >= 2 and all(word[0].isupper() for word in plain)


class Audit:
    """Collect the findings for one document."""

    def __init__(
        self, source: str, format: str, allowed: dict[str, str], profile: str
    ) -> None:
        # Standard input arrives with its line endings as written.
        source = NEWLINE.sub("\n", source)
        self.source = source
        self.prose = extract(source, format)
        if not self.prose.text.strip():
            raise ValueError("no prose to check after excluding literal content")
        self.format = format
        self.profile = profile
        self.allowed = allowed
        self.text = flow(self.prose.text.translate(NORMALISE), format, profile)
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self.words = len(self.prose.text.split())
        self.thousands = max(self.words, 1) / 1000
        self.structure = blocks(self.text)
        self.findings: list[tuple[int, int, Finding]] = []
        # Per category, the characters a finding already covers.
        self.claimed: dict[str, bytearray] = {}
        self.stats: dict[str, float | int] = {"words": self.words}

    def add(
        self,
        rule: str,
        severity: str,
        advice: str,
        start: int,
        end: int,
        text: str | None = None,
    ) -> None:
        position = self.prose.positions[start]
        line_index = bisect.bisect_right(self.line_starts, position) - 1
        found = Finding(
            rule,
            rule.split(".", 1)[0],
            severity,
            line_index + 1,
            position - self.line_starts[line_index] + 1,
            text or re.sub(r"\s+", " ", self.prose.text[start:end]).strip(),
            advice,
            self.allowed.get(rule),
        )
        self.findings.append((start, end, found))

    def computed(
        self, rule: str, start: int, end: int, text: str | None = None
    ) -> None:
        severity, advice = COMPUTED[rule]
        self.add(rule, severity, advice, start, end, text)

    def spans(self, rule: str) -> list[tuple[int, int]]:
        return [
            (start, end) for start, end, found in self.findings if found.rule == rule
        ]

    def slice(self, part: Block | Sentence) -> str:
        return self.text[part.start : part.end]

    def over(self, count: int, minimum: int, rate: float) -> bool:
        """True when a count is both large enough and dense enough to report."""
        return count >= minimum and count / self.thousands >= rate

    def match_rules(self) -> None:
        # Errors claim their span first, so a weaker rule in the same category
        # cannot report the same words again.
        for rule in sorted(RULES, key=lambda rule: rule.severity != "error"):
            if self.profile not in rule.profiles:
                continue
            mask = self.claimed.setdefault(rule.category, bytearray(len(self.text)))
            flags = re.M if rule.cased else re.M | re.I
            opening = rule.pattern.startswith(OPENING)
            for match in re.finditer(rule.pattern, self.text, flags):
                start, end = match.span()
                if mask.count(1, start, end) < end - start:
                    mask[start:end] = b"\x01" * (end - start)
                    # Report the words, not the marker or emphasis before them.
                    lead = LEAD.match(match[0]).end() if opening else 0
                    self.add(rule.id, rule.severity, rule.advice, start + lead, end)

    def check_interface(self) -> None:
        for block in self.structure:
            clipped = [s for s in block.sentences if 3 <= s.words <= 6]
            if len(block.sentences) >= 2 and len(clipped) == len(block.sentences):
                self.computed("interface.pair", block.start, block.end)

    def check_sentences(self) -> None:
        previous = None
        for block in self.structure:
            for sentence in block.sentences:
                raw = self.slice(sentence)
                text = re.sub(r"\s+", " ", raw)
                # A run of spaces is masked code, so two such sentences may differ.
                key = None if "  " in raw else text.casefold()
                if sentence.words >= 5 and key and key == previous:
                    self.computed("rhythm.repeat", sentence.start, sentence.end)
                if text.count("—") >= 3:
                    self.computed("rhythm.dashes", sentence.start, sentence.end)
                previous = key
        # Reported as a figure only: people use dashes as often as models do.
        dashes = self.text.count("—")
        self.stats["em_dashes_per_1000"] = round(dashes / self.thousands, 1)

    def check_paragraphs(self) -> None:
        closers = []
        eligible = 0
        for block in self.structure:
            if block.kind != "paragraph":
                continue
            fragments = questions = 0
            for index, sentence in enumerate(block.sentences):
                fragments = fragments + 1 if sentence.words <= 4 else 0
                asks = self.slice(sentence).rstrip("\"')*_ ").endswith("?")
                questions = questions + 1 if asks else 0
                for rule, run in (
                    ("rhythm.fragments", fragments),
                    ("rhythm.questions", questions),
                ):
                    if run == 3:
                        self.computed(
                            rule, block.sentences[index - 2].start, sentence.end
                        )
            lengths = [sentence.words for sentence in block.sentences]
            if len(lengths) >= 2:
                eligible += 1
                if lengths[-1] <= 5 and max(lengths[:-1]) >= 8:
                    closers.append(block.sentences[-1])
        if len(closers) >= 3 and len(closers) * 4 >= eligible:
            self.computed(
                "rhythm.closers",
                closers[0].start,
                closers[0].end,
                f"{len(closers)} of {eligible} paragraphs end on a sentence of five words or fewer",
            )

    def check_uniformity(self) -> None:
        running = [
            sentence
            for block in self.structure
            if block.kind in ("paragraph", "item")
            for sentence in block.sentences
        ]
        lengths = [sentence.words for sentence in running]
        self.stats["sentences"] = len(lengths)
        if len(lengths) < 2:
            return
        mean = statistics.fmean(lengths)
        variation = statistics.pstdev(lengths) / mean
        self.stats["sentence_mean"] = round(mean, 1)
        self.stats["sentence_variation"] = round(variation, 2)
        if len(lengths) >= UNIFORM_SENTENCES and variation < UNIFORM_VARIATION:
            self.computed(
                "rhythm.uniform",
                running[0].start,
                running[0].end,
                f"{len(lengths)} sentences average {mean:.0f} words with variation {variation:.2f}",
            )

    def check_accumulation(self) -> None:
        contrasts = self.spans("staging.contrast")
        if self.over(len(contrasts), CONTRAST_MINIMUM, CONTRAST_RATE):
            self.computed(
                "staging.contrasts",
                *contrasts[0],
                f"{len(contrasts)} contrast frames in {self.words} words",
            )

        # Counted from the text, so a word another rule reported still counts.
        every = words(STOCK + PROMOTION + COMMON)
        stock = [match.span() for match in re.finditer(every, self.text, re.I)]
        for group in clusters(stock, self.text, CLUSTER_WINDOW, CLUSTER_MINIMUM):
            found = sorted({self.text[start:end].casefold() for start, end in group})
            self.computed(
                "inflation.cluster", group[0][0], group[-1][1], ", ".join(found)
            )

        tails = [match.span() for match in re.finditer(TAIL, self.text, re.I)]
        if self.over(len(tails), TAIL_MINIMUM, TAIL_RATE):
            self.computed(
                "inflation.tails",
                *tails[0],
                f"{len(tails)} trailing -ing clauses in {self.words} words",
            )
            # Below the threshold these clauses are ordinary; above it, show each one.
            reported = sorted(start for start, _ in self.spans("inflation.tail"))
            rule = next(rule for rule in RULES if rule.id == "inflation.tail")
            for start, end in tails:
                following = bisect.bisect_left(reported, start)
                if following == len(reported) or reported[following] >= end:
                    self.add(rule.id, rule.severity, rule.advice, start, end)

    def check_formatting(self) -> None:
        items = [block for block in self.structure if block.kind == "item"]
        labelled = [block for block in items if BOLD_LABEL.match(self.slice(block))]
        if len(labelled) >= 3 and len(labelled) * 2 >= len(items):
            self.computed(
                "formatting.labels",
                labelled[0].start,
                labelled[0].end,
                f"{len(labelled)} of {len(items)} list items open with a bold label",
            )

        bold = [match.span() for match in BOLD.finditer(self.text)]
        if self.over(len(bold), 8, 15.0):
            self.computed(
                "formatting.bold",
                *bold[0],
                f"{len(bold)} bold spans in {self.words} words",
            )

        subheadings = [
            block
            for block in self.structure
            if block.kind == "heading"
            and not self.slice(block).lstrip().startswith("# ")
        ]
        for rule, test, label in (
            ("formatting.titlecase", title_case, "use title case"),
            ("formatting.instructions", INSTRUCTION_HEADING.match, "are instructions"),
        ):
            matched = [block for block in subheadings if test(self.heading(block)[1])]
            if len(matched) >= 2:
                self.computed(
                    rule,
                    matched[0].start,
                    matched[0].end,
                    f"{len(matched)} of {len(subheadings)} subheadings {label}",
                )

        separators = [
            block for block in self.structure if RULE_LINE.fullmatch(self.slice(block))
        ]
        if len(separators) >= 3:
            self.computed(
                "formatting.rules",
                separators[0].start,
                separators[0].end,
                f"{len(separators)} horizontal rules",
            )

        for match in HASHTAGS.finditer(self.text):
            self.computed("formatting.hashtags", match.start(), match.end())

        decorated = [
            block
            for block in self.structure
            if block.kind in ("heading", "item") and EMOJI.search(self.slice(block))
        ]
        if decorated:
            self.computed(
                "formatting.emoji",
                decorated[0].start,
                decorated[0].end,
                f"{len(decorated)} headings or list items carry emoji",
            )

    def heading(self, block: Block) -> tuple[int, str]:
        """Where a heading's words start, and the words without closing marks."""
        raw = self.slice(block)
        lead = HEADING_MARK.match(raw).end()
        lead += len(raw) - lead - len(raw[lead:].lstrip("*_\"'"))
        return lead, raw[lead:].rstrip(" \t#*_")

    def check_headings(self) -> None:
        headings = [block for block in self.structure if block.kind == "heading"]
        pitched = []
        for block in headings:
            lead, text = self.heading(block)
            if PITCH_HEADING.match(text):
                pitched.append(block)
                start = block.start + lead
                self.computed("pitch.heading", start, start + len(text))
                # The heading is one finding; its phrases are not reported again.
                mask = self.claimed.setdefault("pitch", bytearray(len(self.text)))
                mask[block.start : block.end] = b"\x01" * (block.end - block.start)
        if (
            len(pitched) >= PITCH_HEADINGS
            and len(pitched) >= len(headings) * PITCH_HEADING_SHARE
        ):
            self.computed(
                "pitch.headings",
                pitched[0].start,
                pitched[0].end,
                f"{len(pitched)} of {len(headings)} headings address or sell to the reader",
            )

    def particular(self, block: Block, sentence: Sentence) -> bool:
        """True when a sentence carries a figure, a name, code, a link or a quotation."""
        text = self.slice(sentence)
        if block.kind == "item" and sentence.start == block.sentences[0].start:
            text = text[ITEM_MARK.match(text).end() :]
        positions = self.prose.positions
        written = self.source[
            positions[sentence.start] : positions[sentence.end - 1] + 1
        ]
        return bool(PARTICULAR.search(text) or LITERAL.search(written))

    def check_particulars(self) -> None:
        counted = carrying = 0
        runs: list[list[Sentence]] = []
        for block in self.structure:
            if block.kind not in ("paragraph", "item"):
                continue
            run: list[Sentence] = []
            for sentence in block.sentences:
                if sentence.words < 4:
                    continue
                counted += 1
                if self.particular(block, sentence):
                    carrying += 1
                    run = []
                    continue
                if not run:
                    runs.append(run)
                run.append(sentence)
        if not counted:
            return
        self.stats["particulars_percent"] = round(100 * carrying / counted)
        if counted >= PARTICULAR_SENTENCES and carrying < counted * PARTICULAR_SHARE:
            first = self.structure[0]
            self.computed(
                "particulars.share",
                first.start,
                first.end,
                f"{carrying} of {counted} sentences carry a number, a name, code or a link",
            )
        for run in runs:
            if len(run) >= PARTICULAR_RUN:
                opening = re.sub(r"\s+", " ", self.slice(run[0]))
                self.computed(
                    "particulars.run",
                    run[0].start,
                    run[-1].end,
                    f"{len(run)} sentences from: {opening[:60]}",
                )

    def check_density(self) -> None:
        signals = [
            (start, end)
            for start, end, found in self.findings
            if found.severity == "review"
            and not found.allowance
            and found.category not in UNCOUNTED
        ]
        if self.over(len(signals), DENSITY_MINIMUM, DENSITY_RATE):
            self.computed(
                "density.signals",
                *min(signals),
                f"{len(signals)} review findings in {self.words} words",
            )

    def result(self) -> dict:
        ordered = sorted(
            (found for _, _, found in self.findings),
            key=lambda found: (found.line, found.column, found.rule),
        )
        blocking = [f for f in ordered if f.severity == "error" and not f.allowance]
        review = [f for f in ordered if f.severity == "review" and not f.allowance]
        return {
            "passed": not blocking,
            "blocking": len(blocking),
            "review": len(review),
            "language": "en",
            "format": self.format,
            "profile": self.profile,
            "words": self.words,
            "stats": self.stats,
            "findings": [asdict(found) for found in ordered],
        }


def audit(
    source: str,
    format: str = "text",
    allowed: dict[str, str] | None = None,
    profile: str = "prose",
) -> dict:
    document = Audit(source, format, allowed or {}, profile)
    if profile == "interface":
        document.match_rules()
        document.check_interface()
    else:
        # Markdown headings are read first, so a pitched heading is one finding.
        if format != "html":
            document.check_headings()
        document.match_rules()
        document.check_sentences()
        document.check_paragraphs()
        document.check_uniformity()
        document.check_accumulation()
        document.check_particulars()
        if format != "html":
            document.check_formatting()
        document.check_density()
    return document.result()


def summary(result: dict) -> str:
    return f"{result['blocking']} blocking, {result['review']} to review"


def report(result: dict, stream=None) -> None:
    stream = stream or sys.stdout
    print(
        f"{result.get('path', '<text>')}: "
        + (
            "pass"
            if result["passed"]
            else "needs editing"
            if result["blocking"]
            else "needs review"
        )
        + f"; {result['words']} words; {summary(result)}",
        file=stream,
    )
    for finding in result["findings"]:
        status = (
            "allowed: " + finding["allowance"]
            if finding["allowance"]
            else finding["severity"]
        )
        print(
            f"  {finding['line']}:{finding['column']} [{finding['rule']}] {status}: {finding['text']}",
            file=stream,
        )
        print(f"    {finding['advice']}", file=stream)
    print(
        "  English patterns only. A pass means no blocking pattern matched; "
        "it does not verify facts, quality or authorship.",
        file=stream,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="UTF-8 files, or - for stdin")
    parser.add_argument("--text", help="Check a literal string instead of files")
    parser.add_argument(
        "--format", choices=("auto", "text", "markdown", "html"), default="auto"
    )
    parser.add_argument(
        "--profile",
        choices=PROFILES,
        default="prose",
        help="prose for documents; interface for one interface string per line",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Only English (en) is supported; no language detection",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable report, including input errors",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Also fail for unresolved review findings"
    )
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="RULE=REASON",
        help="Keep a finding visible but exempt it for this invocation",
    )
    args = parser.parse_args(argv)
    results, errors = [], []
    try:
        if args.language.lower().split("-")[0] != "en":
            raise ValueError("unsupported language; the checker covers English only")
        if (args.text is not None and args.paths) or (
            args.text is None and not args.paths
        ):
            raise ValueError(
                "provide files, - for stdin, or --text; do not combine --text with files"
            )
        if args.paths.count("-") > 1:
            raise ValueError("stdin can only be read once")
        allowed = allowances(args.allow)
        for path in args.paths or ["<text>"]:
            try:
                source = (
                    args.text
                    if args.text is not None
                    else sys.stdin.read()
                    if path == "-"
                    else Path(path).read_text(encoding="utf-8-sig")
                )
                result = {
                    "path": path,
                    **audit(
                        source.removeprefix("\ufeff"),
                        infer_format(path, args.format),
                        allowed,
                        args.profile,
                    ),
                }
                # Under --strict an unresolved review finding fails the document.
                result["passed"] = result["passed"] and not (
                    args.strict and result["review"]
                )
                results.append(result)
            except (OSError, UnicodeError, ValueError) as error:
                errors.append({"path": path, "message": str(error)})
    except ValueError as error:
        errors.append({"path": None, "message": str(error)})
    passed = not errors and all(result["passed"] for result in results)
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 2,
                    "passed": passed,
                    "results": results,
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for result in results:
            report(result)
        for error in errors:
            print(
                f"hooman: {error['path'] or 'input'}: {error['message']}",
                file=sys.stderr,
            )
    return 2 if errors else 0 if passed else 1


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    for output in (sys.stdout, sys.stderr):
        if hasattr(output, "reconfigure"):
            output.reconfigure(errors="replace")
    raise SystemExit(main())
