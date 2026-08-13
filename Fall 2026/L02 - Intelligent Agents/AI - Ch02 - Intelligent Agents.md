# AI — Chapter 2: Intelligent Agents

*Cleaned-up lecture transcript, organized by topic. Timestamps removed.*

> **A note on this cleanup:** this file was generated from the auto-captions
> (`AI - Ch02 - Intelligent Agents [_b8o2DvMdis].en.srt`), which are speech
> recognition output, not a human transcript. Two kinds of edits were made:
> (1) the ASR consistently mis-heard the word "agent" as "isn't," "essent,"
> "essence," "asset," "ascent," "resin," "Hessian," and similar — those are
> corrected throughout, since the entire lecture is about agents and no
> other reading fits. (2) A small number of other clearly-garbled words were
> fixed from context (e.g. "suck the load/door" → "suck the dirt," "roam
> be" → "room B," "peasant" → "patient"), and some repetitive spoken
> conditionals were reformatted into lists/tables for readability. The
> original `.srt` is untouched — if exact wording ever matters (e.g. for a
> quote), check it against the source video.

---

## 1. What Is an Agent?

In this chapter we will talk about how to design intelligent agents, and
what considerations we have to make when designing them. We start with the
definition of an agent.

Earlier we discussed AI, but we didn't provide a specific definition of an
agent. Here we will define an agent specifically for the purpose of
designing intelligent agents.

**An agent is anything that can be viewed as perceiving its environment
through sensors and acting on that environment using actuators.** For
something to be an agent — for the purpose of designing intelligent agents
— the agent perceives the environment using sensors and uses actuators to
take actions on the environment.

So when defining an agent it is extremely important that we mention the
environment: that the agent has sensors, and that the agent has actuators
to act on the environment. It's also important to note that the sensors
and actuators are part of the agent itself, whereas the environment is
outside the agent — that's where the interaction happens.

### Examples of agents and their sensors/actuators

- **Human agent** — eyes, ears, and other organs as sensors; hands, legs,
  vocal tract, etc. as actuators, used to take actions on the environment.
- **Robotic agent** — cameras and infrared range finders as sensors;
  various motors as actuators. In a self-driving car, for example, wheels
  and motors are the actuators.
- **Software agent** — sensory inputs can be keystrokes it receives, file
  contents, and network packets; it acts on the environment by displaying
  on the screen, writing to files, and sending network packets.

## 2. Percepts and Percept Sequences

When talking about agents and how agents perceive the environment, it's
important that we understand the difference between a **percept** and a
**percept sequence**.

- A **percept** is an agent's perceptual input at any given instant — at
  one instant of time. For a robotic agent, that's whatever picture it's
  viewing, or whatever input it's taking from an infrared sensor, at that
  moment.
- A **percept sequence** is the complete history of everything the agent
  has ever perceived. For a human agent, the percept sequence is
  everything they've ever received through their eyes, ears, and other
  sensory organs since birth.

## 3. Agent Function vs. Agent Program

It's also important that we understand the difference between two things:
the **agent function** and the **agent program**.

Say you're given a new agent and don't know what it does — we'd like an
instruction manual for it. That instruction manual can be written or
described at two levels:

1. **Agent function** — describes *what* the agent does.
2. **Agent program** — describes *how* it's actually implemented.

To better describe these two, let's take an example: the **vacuum-cleaner
world**.

## 4. Example: The Vacuum-Cleaner World

### 4.1 Setup

We have two rooms, room A and room B. The icons on screen represent dirt
in a room, so room A may be dirty or clean, and likewise room B may be
dirty or clean.

The vacuum-cleaner agent can perceive two things:

1. Which square (room) it is currently in.
2. Whether that room has dirt or not.

As actions, the agent can move left, move right, suck up the dirt, or do
nothing. That's how this agent interacts with its environment.

### 4.2 The agent function (as a table)

The agent function is simply something like a tiny instruction manual that
says: *here's a situation, and here's the action.* For the vacuum agent:
if the current square is dirty, suck the dirt; otherwise, move to the
other square. It characterizes what happens in every situation — it will
keep oscillating between rooms until all rooms are clean.

More specifically, the agent function can be represented as a table, where
the first column is the percept sequence and the second column is the
action to take:

| Percept (location, status) | Action     |
|-----------------------------|------------|
| Room A, clean                | Move right |
| Room A, dirty                 | Suck       |
| Room B, clean                | Move left  |
| Room B, dirty                 | Suck       |

That table is the agent function — it characterizes what the agent does in
every possible situation.

### 4.3 The agent program (an implementation)

The agent program is the underlying working mechanism — the actual
implementation of how the agent works. Here's a very simple one for the
vacuum agent: it's a function that takes the current location and status
(square A or B; dirty or clean) as input, and returns an action.

- If the status is dirty — no matter what room — return **suck the dirt**.
- Else (the room is clean):
  - If in location A, return **move right**.
  - If in location B, return **move left**.

That small function is the agent program for the vacuum-cleaner agent.

### 4.4 Characterizing an agent via its function/program

Given a new agent, we use the agent function and the agent program to
characterize what it does. The agent function describes an agent's
behavior by mapping any given percept sequence to an action.

To describe any given agent, we'd have to tabulate its agent function —
and this is typically a very large table, potentially infinitely large,
because we'd have to list every possible scenario the agent could be
exposed to and the corresponding action. In principle, we build this table
by exposing the agent to all possible percept sequences and recording what
action it takes in response.

This table is an **external characterization** of the agent — we're
ignoring the internal details of how the agent works, and instead looking
at it from the outside: what it does in various scenarios. The agent
program, by contrast, is an **internal implementation** of the agent
function — a concrete program running within some physical system.

## 5. Rationality: "Doing the Right Thing"

One of the best definitions of AI is *designing agents that act
rationally.* So how do we define acting rationally? Should we consider the
environment the agent will be deployed in, or can we define rationality
while ignoring the environment?

**In general, a rational agent is one that does the right thing** — every
entry in its agent-function table is filled out correctly. That's not a
complete definition, but it's the starting intuition.

To understand this more precisely, we need to consider the *consequences*
of the agent's behavior. When an agent is placed in an environment, it
generates a sequence of actions based on what it perceives. That sequence
of actions causes the environment to go through a sequence of states —
because the agent is acting on the environment, the environment
experiences consequences.

**If that sequence of environment states is desirable, the agent has
performed well.** This agent may have a good agent program or agent
function on its own, but what matters is: when the agent acts on the
environment, are the resulting changes desirable? If yes, the agent is
rational; if not, even a "good" agent program/function is not acting
rationally.

**We're interested in environment states, not agent states.** We're not
concerned with what happens inside the agent — only what happens to the
environment.

We should not define an agent's success in terms of the agent's own
opinion of itself. An agent could achieve "perfect rationality" simply by
*deluding itself* that its performance was perfect — "this is what I was
designed for, I did exactly what I was supposed to do" — but the actual
impact on the environment may not be good. (Human agents, notably, are
very prone to this kind of "sour grapes" excuse-making when they don't
achieve what they set out to do.)

## 6. Performance Measures Should Judge the Environment, Not the Agent

Our evaluation metric — how good or bad an agent is — should focus on the
**environment**, not on how the agent behaves internally. We should design
performance measures according to what we want in the environment, rather
than dictating how the agent should behave, because ultimately what
matters is the impact on the environment.

### A flawed example

For the vacuum agent, we might propose: *measure performance by the amount
of dirt cleaned up in an eight-hour shift.* This looks reasonable at
first, but here's the problem: the agent could collect some dirt, throw it
back onto the floor, pick it up again, throw it back down, and repeat —
racking up a large "amount of dirt collected" total while never actually
leaving the environment clean.

**This is why a performance measure has to be designed to capture exactly
what we actually want in the environment** — not a proxy that can be
gamed.

## 7. What Rationality Depends On

Overall, what is rational at any given time depends on four things:

1. **The performance measure** that defines the criteria for success.
2. **The agent's prior knowledge** of the environment.
3. **The actions** the agent can perform.
4. **The agent's percept sequence to date.**

- *Depends on the performance measure*: a vacuum agent that endlessly
  oscillates, throwing dirt back down and re-collecting it, is still
  "rational" if the performance measure only counts total dirt collected
  — because it satisfies that definition, however bad the definition is.
- *Depends on prior knowledge*: an agent that cleans every room it visits,
  even rooms that are already clean, may be behaving rationally if it
  simply doesn't know in advance which rooms are already clean.
- *Depends on available actions*: if an agent physically cannot clean the
  corners of a room, it's rational for it not to try, because it can't
  perform that action.
- *Depends on percept sequence to date*: i.e., what the agent has actually
  perceived/learned over time.

## 8. A Formal Definition of a Rational Agent

> For each possible percept sequence, a rational agent should select an
> action that is expected to **maximize its performance measure**, given
> the evidence provided by the percept sequence and whatever built-in
> knowledge the agent has.

This is *not* the same as "a robot is good if it saves humanity." The
definition says nothing about specific goals like saving or harming
humanity — an agent is rational if it does what it's designed to do and
tries to maximize the performance measure it was given. If it's designed
to help people and it does that, it's rational; if it's designed to save
people and it does that, it's rational. Knowledge can be pre-loaded into
the agent, or the agent can learn from its percept sequence over time —
but what's rational always depends on the performance measure in use.

## 9. A Cautionary Example: When a Performance Measure Goes Wrong

Assume, for the vacuum-cleaner example: the performance measure awards one
point for each clean square at each time step, over a lifetime of 1,000
time steps. Prior knowledge: there are two squares, but the agent doesn't
know their dirt distribution. Available actions: move left, move right,
suck. Percept sequence: the agent perceives its location and whether that
location has dirt.

The agent's behavior: clean a square if it's dirty, move to the other
square if not. Is this agent rational? **Yes** — it's using its prior
knowledge, using all available actions, correctly perceiving its percept
sequence, and doing exactly what maximizes the stated performance measure.

But here's the problem: once all the dirt is cleaned up, the agent will
oscillate back and forth between room A and room B *forever*, since moving
still doesn't cost it anything under this performance measure, and nothing
in the definition says it shouldn't oscillate. **The agent is still
rational — the performance measure is simply not good enough to capture
what we actually wanted from the environment.**

## 10. Task Environments and PEAS

To correctly specify what an agent should do, the first step is to specify
its **task environment** as fully as possible. A task environment is a
combination of four things — remembered by the acronym **PEAS**:

- **P**erformance measure
- **E**nvironment
- **A**ctuators
- **S**ensors

### Example: a fully automated taxi

| PEAS component | Specification |
|---|---|
| **Performance measure** | Safe, fast, legal, comfortable trip, maximizes profit for the owners, works in all weather conditions |
| **Environment** | Roads, traffic, pedestrians, customers |
| **Actuators** | Steering, acceleration, brake, signal, horn, display |
| **Sensors** | Cameras, GPS, odometer, accelerometer, engine sensors, keyboard (for a person to interact with) |

Specifying all four of these up front is what lets us go on to build the
agent function or agent program.

## 11. More PEAS Examples

| Agent type | Performance measure | Environment | Note |
|---|---|---|---|
| Online medical diagnosis system (e.g. WebMD) | Healthy patient, reduced costs | Patient, hospital staff | *Not* "correct diagnosis" — a correct diagnosis doesn't always lead to a healthy patient. |
| Satellite imaging analysis system | Correct image categorization | — | — |
| Part-picking robot | Percentage of parts in the **correct bins** | — | *Not* "percentage of parts picked correctly" — the robot could pick a part up fine and still put it in the wrong bin. |
| Refinery controller | Purity, yield, safety | — | — |
| Interactive English tutor | **Student's score** on the test | — | *Not* "how well the teacher teaches" — a tutor's actual goal is student outcomes, not a self-reported teaching-quality metric. |

The common thread: a performance measure should always be chosen to
capture the actual desired impact on the environment, not a proxy that's
easier to measure but doesn't reflect what we really want.

## 12. Chapter Summary

- An **agent** is something that perceives and acts in an environment,
  via sensors and actuators.
- The **agent function** specifies the actions taken by the agent in
  response to a percept sequence.
- The **performance measure** evaluates the behavior of an agent in an
  environment.
- A **rational agent** is one expected to maximize its performance
  measure, given the percept sequence it has seen so far.
- A **task environment** is defined by four things: performance measure,
  environment, actuators, and sensors (**PEAS**).
- The first step in designing an agent is to specify its task environment
  as fully as possible.
