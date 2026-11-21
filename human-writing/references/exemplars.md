# Exemplars

These passages were written by people between 1863 and 2021. Read the ones for
the kind of document in hand before drafting or rewriting. They show a form:
how a description opens, what one sentence carries, where a report puts what
happened and where it puts what that means. Take no wording and no facts from
them. An author's own writing sample outranks them.

Each passage is quoted exactly from the source named, so its spelling,
punctuation and conventions are those of its time and place. The note under
each passage says what to observe.

## Description

For a README, a reference page or a product description.

> tmux is a terminal multiplexer: it enables a number of terminals to be
> created, accessed, and controlled from a single screen. tmux may be detached
> from a screen and continue running in the background, then later reattached.
>
> When tmux is started it creates a new session with a single window and
> displays it on screen. A status line at the bottom of the screen shows
> information on the current session and is used to enter interactive
> commands.
>
> A session is a single collection of pseudo terminals under the management of
> tmux. Each session has one or more windows linked to it. A window occupies
> the entire screen and may be split into rectangular panes, each of which is
> a separate pseudo terminal (the pty(4) manual page documents the technical
> details of pseudo terminals). Any number of tmux instances may connect to
> the same session, and any number of windows may be present in the same
> session. Once all sessions are killed, tmux exits.

tmux(1) manual page, DESCRIPTION. Nicholas Marriott, OpenBSD, 2021.
[Source](https://raw.githubusercontent.com/openbsd/src/ff8fb92b25131022f39b5b59d4b0f2efc6939ec8/usr.bin/tmux/tmux.1).
The first sentence defines the program. Each later sentence states one
behaviour. Terms are defined once and reused: session, window, pane.

> PEP stands for Python Enhancement Proposal. A PEP is a design document
> providing information to the Python community, or describing a new feature
> for Python or its processes or environment. The PEP should provide a concise
> technical specification of the feature and a rationale for the feature.
>
> We intend PEPs to be the primary mechanisms for proposing major new
> features, for collecting community input on an issue, and for documenting
> the design decisions that have gone into Python. The PEP author is
> responsible for building consensus within the community and documenting
> dissenting opinions.

PEP 1, “What is a PEP?”. Barry Warsaw, Jeremy Hylton, David Goodger and Nick
Coghlan, 2000.
[Source](https://raw.githubusercontent.com/python/peps/cd1e507dd86cfee5aed5caa2b74a1a2449f2978b/pep-0001.txt).
The name is expanded, then defined, then given its purpose. Responsibility is
assigned to a named role.

## Explanation

For a design note, a specification, a decision record or a technical post.

> The view of the system is built upon three principles. First, resources are
> named and accessed like files in a hierarchical file system. Second, there
> is a standard protocol, called 9P, for accessing these resources. Third, the
> disjoint hierarchies provided by different services are joined together into
> a single private hierarchical file name space. The unusual properties of
> Plan 9 stem from the consistent, aggressive application of these principles.
>
> A large Plan 9 installation has a number of computers networked together,
> each providing a particular class of service. Shared multiprocessor servers
> provide computing cycles; other large machines offer file storage. These
> machines are located in an air-conditioned machine room and are connected by
> high-performance networks. Lower bandwidth networks such as Ethernet or ISDN
> connect these servers to office- and home-resident workstations or PCs,
> called terminals in Plan 9 terminology. Figure 1 shows the arrangement.

“Plan 9 from Bell Labs”. Rob Pike, Dave Presotto, Sean Dorward, Bob Flandrena,
Ken Thompson, Howard Trickey and Phil Winterbottom, 1995.
[Source](https://raw.githubusercontent.com/plan9foundation/plan9/ed1a9c21e3297d7497a48053d33683375c75fbb4/sys/doc/9.ms).
The principles are counted and then stated in order. The second paragraph
describes a real installation, part by part.

> An important feature of transactional databases like SQLite is "atomic
> commit". Atomic commit means that either all database changes within a
> single transaction occur or none of them occur. With atomic commit, it is as
> if many different writes to different sections of the database file occur
> instantaneously and simultaneously. Real hardware serializes writes to mass
> storage, and writing a single sector takes a finite amount of time. So it is
> impossible to truly write many different sectors of a database file
> simultaneously and/or instantaneously. But the atomic commit logic within
> SQLite makes it appear as if the changes for a transaction are all written
> instantaneously and simultaneously.
>
> SQLite has the important property that transactions appear to be atomic even
> if the transaction is interrupted by an operating system crash or power
> failure.
>
> This article describes the techniques used by SQLite to create the illusion
> of atomic commit.

“Atomic Commit In SQLite”. The SQLite authors, as archived in December 2021.
[Source](https://web.archive.org/web/20211214172557id_/https://www.sqlite.org/atomiccommit.html).
The term is quoted and defined in the next sentence. The constraint is stated
as a fact about hardware before the claim about the software.

## Specification

For definitions, option references and product specifications.

> Private cloud. The cloud infrastructure is provisioned for exclusive use by
> a single organization comprising multiple consumers (e.g., business units).
> It may be owned, managed, and operated by the organization, a third party,
> or some combination of them, and it may exist on or off premises.
>
> Community cloud. The cloud infrastructure is provisioned for exclusive use
> by a specific community of consumers from organizations that have shared
> concerns (e.g., mission, security requirements, policy, and compliance
> considerations). It may be owned, managed, and operated by one or more of
> the organizations in the community, a third party, or some combination of
> them, and it may exist on or off premises.
>
> Public cloud. The cloud infrastructure is provisioned for open use by the
> general public. It may be owned, managed, and operated by a business,
> academic, or government organization, or some combination of them. It exists
> on the premises of the cloud provider.
>
> Hybrid cloud. The cloud infrastructure is a composition of two or more
> distinct cloud infrastructures (private, community, or public) that remain
> unique entities, but are bound together by standardized or proprietary
> technology that enables data and application portability (e.g., cloud
> bursting for load balancing between clouds).

The NIST Definition of Cloud Computing, Special Publication 800-145. Peter Mell
and Timothy Grance, 2011.
[Source](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf).
Four entries share one structure: the term, who may use it, who may own it,
where it may sit. A reader can compare any two entries line by line.

## Report

For an incident report, a postmortem or an investigation.

> On January 15, 2009, about 1527 eastern standard time, US Airways flight
> 1549, an Airbus Industrie A320-214, N106US, experienced an almost complete
> loss of thrust in both engines after encountering a flock of birds and was
> subsequently ditched on the Hudson River about 8.5 miles from LaGuardia
> Airport (LGA), New York City, New York. The flight was en route to Charlotte
> Douglas International Airport, Charlotte, North Carolina, and had departed
> LGA about 2 minutes before the in-flight event occurred. The 150 passengers,
> including a lap-held child, and 5 crewmembers evacuated the airplane via the
> forward and overwing exits. One flight attendant and four passengers were
> seriously injured, and the airplane was substantially damaged. The
> scheduled, domestic passenger flight was operating under the provisions of
> 14 Code of Federal Regulations Part 121 on an instrument flight rules flight
> plan. Visual meteorological conditions prevailed at the time of the
> accident.

Aircraft Accident Report NTSB/AAR-10/03, Executive Summary. National
Transportation Safety Board, 2010.
[Source](https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1003.pdf).
Date, time, flight, aircraft, event, place and outcome come in the first
sentence. Every figure has a unit. Nothing is characterised.

> a. After assembly and acceptance testing, the oxygen tank no. 2 which flew
> on Apollo 13 was shipped from Beech Aircraft Corporation to North American
> Rockwell (NR) in apparently satisfactory condition.
>
> b. It is now known, however, that the tank contained two protective
> thermostatic switches on the heater assembly, which were inadequate and
> would subsequently fail during ground test operations at Kennedy Space
> Center (KSC).
>
> c. In addition, it is probable that the tank contained a loosely fitting
> fill tube assembly. This assembly was probably displaced during subsequent
> handling, which included an incident at the prime contractor's plant in
> which the tank was jarred.
>
> d. In itself, the displaced fill tube assembly was not particularly serious,
> but it led to the use of improvised detanking procedures at KSC which almost
> certainly set the stage for the accident.
>
> e. Although Beech did not encounter any problem in detanking during
> acceptance tests, it was not possible to detank oxygen tank no. 2 using
> normal procedures at KSC. Tests and analyses indicate that this was due to
> gas leakage through the displaced fill tube assembly.

Report of Apollo 13 Review Board, Chapter 5. NASA, 1970.
[Source](https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo_13_review_board.txt).
Each finding is one lettered paragraph. Certainty is graded in plain words:
known, probable, almost certainly. Cause is claimed only where tests support
it.

## Status report

For a progress update or a status notice.

> NASA continues to work on resolving an issue with the payload computer on
> the Hubble Space Telescope. The operations team will be running tests and
> collecting more information on the system to further isolate the problem.
> The science instruments will remain in a safe mode state until the issue is
> resolved. The telescope itself and science instruments remain in good
> health.
>
> The computer halted on Sunday, June 13. An attempt to restart the computer
> failed on Monday, June 14. Initial indications pointed to a degrading
> computer memory module as the source of the computer halt. When the
> operations team attempted to switch to a back-up memory module, however, the
> command to initiate the backup module failed to complete. Another attempt
> was conducted on both modules Thursday evening to obtain more diagnostic
> information while again trying to bring those memory modules online.
> However, those attempts were not successful.

Hubble Space Telescope payload computer update, 18 June 2021. NASA Goddard
Space Flight Center.
[Source](https://web.archive.org/web/20210924164236id_/https://www.nasa.gov/api/2/ubernode/471844).
The current state comes first, then what happens next, then what is unaffected.
The history follows with a day for each event, and the failure is stated
plainly.

> NEAR SPOTTSYLVANIA C. H., May 11, 1864--8.30 A.M.
>
> MAJOR-GENERAL HALLECK, Chief of Staff of the Army, Washington, D. C.
>
> We have now ended the 6th day of very hard fighting. The result up to this
> time is much in our favor. But our losses have been heavy as well as those
> of the enemy. We have lost to this time eleven general officers killed,
> wounded and missing, and probably twenty thousand men. I think the loss of
> the enemy must be greater--we having taken over four thousand prisoners in
> battle, whilst he has taken from us but few except a few stragglers. I am
> now sending back to Belle Plain all my wagons for a fresh supply of
> provisions and ammunition, and purpose to fight it out on this line if it
> takes all summer.
>
> The arrival of reinforcements here will be very encouraging to the men, and
> I hope they will be sent as fast as possible, and in as great numbers. My
> object in having them sent to Belle Plain was to use them as an escort to
> our supply trains. If it is more convenient to send them out by train to
> march from the railroad to Belle Plain or Fredericksburg, send them so.

Dispatch to Major-General Halleck, 11 May 1864. Ulysses S. Grant.
[Source](https://web.archive.org/web/20211215113901id_/https://www.gutenberg.org/cache/epub/4367/pg4367.txt).
Position, result, losses with figures, the next action and the request, in that
order. The estimate is marked as one.

## Message

For an email, a memo or a reply.

> Dear Dr. Paine:
>
> Pursuant to your directives of April 17 and April 21, 1970, I am
> transmitting the final Report of the Apollo 13 Review Board.
>
> Concurrent with this transmittal, I have recessed the Board, subject to
> call.
>
> We plan to reconvene later this year when most of the remaining special
> tests have been completed, in order to review the results of these tests to
> determine whether any modifications to our findings, determinations, or
> recommendations are necessary. In addition, we will stand ready to reconvene
> at your request.
>
> Sincerely yours,
>
> Edgar M. Cortright

Letter of transmittal, Report of Apollo 13 Review Board. Edgar M. Cortright,
1970.
[Source](https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo_13_review_board.txt).
The first sentence says what is being sent and under what instruction. The rest
states what has been done and what happens next.

> EXECUTIVE MANSION, WASHINGTON, July 13, 1863.
>
> MAJOR-GENERAL GRANT:
>
> MY DEAR GENERAL:--I do not remember that you and I ever met personally. I
> write this now as a grateful acknowledgment of the almost inestimable
> service you have done the Country. I write to say a word further. When you
> first reached the vicinity of Vicksburg, I thought you should do what you
> finally did--march the troops across the neck, run the batteries with the
> transports, and thus go below; and I never had any faith except a general
> hope that you knew better than I, that the Yazoo Pass expedition and the
> like could succeed. When you dropped below, and took Port Gibson, Grand
> Gulf, and vicinity, I thought you should go down the river and join General
> Banks; and when you turned northward, east of the Big Black, I feared it was
> a mistake. I now wish to make the personal acknowledgment that you were
> right and I was wrong.
>
> Yours very truly,
>
> A. LINCOLN.

Letter to Major-General Grant, 13 July 1863. Abraham Lincoln.
[Source](https://web.archive.org/web/20240225131209id_/https://www.gutenberg.org/files/2658/2658.txt).
The purpose is stated in the second sentence. The disagreement is set out with
its places and movements, and the last sentence is the point of the letter.

## Procedure

For instructions and how-to guides.

> It is generally advised by medical men to avoid violent exercise immediately
> after eating. They are right; but I cannot advise you to rest long, or at
> all, after breakfast, but rather to finish what you could not do before the
> meal, and get off at once while it is early and cool. Do not hurry or work
> hard at first if you can avoid it.
>
> On the march, rest often whether you feel tired or not; and, when resting,
> see that you do rest.
>
> The most successful marching that I witnessed in the army was done by
> marching an hour, and resting ten minutes. You need not adhere strictly to
> this rule: still I would advise you to halt frequently for sight-seeing, but
> not to lie perfectly still more than five or ten minutes, as a reaction is
> apt to set in, and you will feel fatigued upon rising.

How to Camp Out, Chapter VII. John M. Gould, 1877.
[Source](https://web.archive.org/web/20240327130908id_/https://www.gutenberg.org/files/17575/17575.txt).
The reader is addressed directly, as instructions allow. The rule is given with
its measure, an hour of marching and ten minutes of rest, and with the reason.

## Sources and licences

The passages were retrieved on 21 November 2026. Each was cut from the
downloaded source by script and compared with it word for word.

| Passage | Basis for reuse |
| --- | --- |
| tmux(1) | ISC licence; notice below |
| PEP 1 | Placed in the public domain or under CC0 1.0 by its authors |
| Plan 9 from Bell Labs | MIT licence; notice below |
| Atomic Commit In SQLite | Dedicated to the public domain by the SQLite authors |
| NIST SP 800-145 | Work of the US government; the publication states it is not subject to copyright |
| NTSB/AAR-10/03 | Work of the US government; the NTSB states its staff reports are in the public domain |
| Report of Apollo 13 Review Board, two passages | Work of the US government |
| Hubble update | NASA web content; NASA permits factual use without explicit permission |
| Grant, Lincoln, Gould | Published before 1929 |

Works of the US government are in the public domain in the United States. The
Apollo 13 passages come from NASA's plain-text transcription of the report.

```text
tmux(1): Copyright (c) 2007 Nicholas Marriott <nicholas.marriott@gmail.com>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF MIND, USE, DATA OR PROFITS, WHETHER
IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

```text
Plan 9 from Bell Labs: Copyright 2021 Plan 9 Foundation

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
