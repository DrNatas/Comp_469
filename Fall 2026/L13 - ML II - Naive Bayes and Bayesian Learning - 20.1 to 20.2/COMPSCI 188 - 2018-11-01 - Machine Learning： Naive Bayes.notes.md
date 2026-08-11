# CS188 — Machine Learning II: Naïve Bayes (AIMA 20.1–20.2, partial)

*Cleaned-up lecture transcript, organized by topic. Timestamps and
housekeeping (candy breaks, "any questions," etc.) removed — that's not
lecture content.*

> **A note on sources, and on what's actually in this file:** the
> transcript was generated from auto-captions (`COMPSCI 188 -
> 2018-11-01 - Machine Learning： Naive Bayes.en.vtt`), a YouTube-style
> rolling caption track where each cue repeats the previous line and
> appends new words with per-word timestamps. Extraction de-duplicated
> the rolling repeats to reconstruct a plain transcript, then reorganized
> it by topic and lightly cleaned it for readability. A handful of short
> passages are garbled beyond confident recovery (auto-captions mishear
> proper nouns and rare words) — these are flagged inline rather than
> silently guessed at.
>
> **Scope mismatch, and why it's not a "ran out of time" situation like
> other lectures in this series:** this folder's slide deck
> (`cs188-sp26-lec21.pdf`, same folder) is titled *"Machine Learning II:
> Naïve Bayes and Bayesian Learning"* and covers two distinct halves —
> (1) Naïve Bayes classification, and (2) full Bayesian learning
> (maximum-a-posteriori vs. true Bayesian prediction, the Surprise Candy
> Co. example, the "numbers game" / poverty-of-stimulus argument). The
> **2018 video's own title, however, only ever claims "Machine Learning:
> Naive Bayes"** — it was never billed as covering Bayesian learning, and
> in fact it doesn't reach that material at all; the entire 50-odd
> minutes is Naïve Bayes classification, parameter estimation, and
> overfitting/smoothing. Sections 1–23 below are the actual lecture
> content, cross-checked line-by-line against the slide deck wherever the
> two overlap (the numbers agree exactly everywhere checked — see the
> worked spam example in Section 13, whose final `98.9%`/`1.1%` split and
> whose opening `-1.1`/`-0.4` log-priors both match the deck precisely).
> Section 24 is an **appendix drawn only from the slide deck**, clearly
> marked as such, summarizing the Bayesian-learning half that this
> particular recording never gets to — treat it as reading material, not
> as a transcript of anything spoken. The original `.vtt` is untouched —
> check it against the source video if exact wording ever matters.

---

## 1. From Given Models to Learned Models

Everything so far in the course assumed **somebody hands you a model**:
a search problem with edge weights, a game with a Bayes net and
conditional probability tables. The course has been about *using* that
model to act optimally — sequencing actions (first part), managing
inference under uncertainty (second part). This lecture shifts to
**where the model comes from**: machine learning is about acquiring a
model, or a model's parameters, from **data and experience**.

**The chain of reasoning for why this matters:** you want to build good
systems. Good systems need to be accurate. Accurate systems come from
good models. Good models come from good data. This lecture is about that
last link — turning data into a model.

**Three things you could learn**, previewed (only the first is the
subject of this lecture):

- **Parameters** — the individual numbers that determine exactly how a
  model behaves, e.g. the probabilities inside a Bayes net's conditional
  probability tables.
- **Structure** — e.g. given a set of random variables and observational
  data about them, learn something about their correlations (or even
  causation) and use that to build the Bayes net's *graph*, not just its
  numbers.
- **Hidden concepts** — clustering data, looking for latent patterns.
  Neural nets, in large part, are about learning hidden representations
  and hidden concepts.

Today: **model-based classification**, worked through concretely via
**naïve Bayes**. Later lectures cover a sequence of other takes on
machine learning, each highlighting a different subset of the big ideas.

---

## 2. Classification: The Basic Setup

**Classification** takes an input and predicts an output/label — inputs
are conventionally called `X`, outputs `Y`. It's not the only kind of
machine learning (clustering is another), but it's probably the most
widely used. Two running examples for the lecture: a **spam filter**
(does this email get you a window into how other *natural language*
tasks work) and **digit recognition** (a window into how other *vision*
tasks work) — both simple classification problems where inputs and
outputs are well-understood, but which already surface most of the big
ideas in ML.

---

## 3. Worked Example: The Spam Filter

**Setup:** input = an email, output = spam or ham (non-spam). You need
data first — a large, hand-labeled (or ecosystem-labeled, e.g. users
clicking "mark as spam") collection of example emails. **In practice,
getting the right data is often the hardest part of building and
deploying an ML system**; how natural or costly it is to collect labels
often determines how feasible a system is to build at all.

**Live-graded examples from an actual (smallish, older) labeled spam
corpus**, read aloud and classified by the class:

- *"Dear sir, I must solicit your confidence in this transaction... by
  virtue of its nature as being utterly confidential and top secret."*
  → **spam** ("it looks really important").
- *"To be removed from future mailings, simply reply... 99 million email
  addresses for only $99."* → **spam** ("that's like a million email
  addresses per dollar").
- *"I know this is blatantly off-topic but I'm beginning to go insane...
  had an old Dell Dimension XPS sitting in the corner... when I plugged
  it in, hit the power, nothing happened."* → **ham**, though noted as a
  genuinely fuzzy case: whether an unsolicited-but-personal email counts
  as spam is an individual judgment call, and some people mark things
  spam just because they don't want to read them, "even if it's from
  their mom."

**What made the first two obviously spam, and how do you automate that
judgment?** Something about the content has to power the decision — this
is where **features** come in. Defining good features is a large part of
deploying an ML system. For spam:

- **Words** — e.g. "only $99," "utterly confidential and top secret."
  Each such feature is a **noisy indicator**: it nudges belief toward
  spam probabilistically, but no single one is decisive. The model's job
  is to **aggregate many pieces of weak evidence**.
- **Text patterns that abstract over individual words** — e.g. "any
  dollar sign followed by digits" is a bad sign as a *pattern*, not tied
  to one word. **ALL CAPS** is another — no single word is responsible,
  it's an aggregate property of the text.
- **Non-text / ecosystem metadata** — in practice, a lot of real spam
  signal comes not from content at all but from context: is the sender
  in your contacts? Has this exact email been broadcast to many inboxes
  in a short window? (Your own inbox can't tell that, but the email
  *provider*, seeing many accounts at once, can.)

---

## 4. Worked Example: Digit Recognition

**Setup:** input = an image (grid of pixels, black/white or grayscale),
output = a digit 0–9. Need a large hand-labeled set — critically, **you
cannot just collect "every digit"**: every image of a handwritten digit
is unique, at least one pixel different from every other example you've
seen. The system has to **generalize**, not memorize a lookup table.

Class exercise looking at ambiguous handwritten samples: most digits
were easy to agree on, but at least one was genuinely disputed —
underscoring that even human-labeled training data carries **noise and
disagreement**, and models trained on it will inherit some of that.

**Features for digits — the raw and the smarter kind:**

- **Raw pixels**, binary (on/off by threshold) — simple, but **not
  invariant**: shift a digit a few pixels and you get an entirely
  different feature vector for "the same" digit.
- **Invariant representations** — number of connected ink components,
  aspect ratio, number of loops, edges — the kind of thing computer
  vision cares about, robust to shifts/tilts/scale. Historically these
  were hand-designed; increasingly, as methods improve (neural nets,
  covered in a couple of weeks), such higher-level features get
  **induced automatically** rather than hand-engineered.

---

## 5. Other Classification Applications (a Quick Tour)

- **Medical diagnosis** — input: symptoms/tests; output: disease.
- **Fraud detection** — input: account/transaction activity; output:
  suspicious or not, at both the individual-transaction and network
  level.
- **Automatic essay grading.**
- **Customer service email routing** — which of many agents/queues an
  incoming email should go to.
- **Review sentiment** — good/bad, and tracking whether sentiment shifts
  after some event (e.g. a product announcement).
- **Language identification** — what language is this document in?
  Contrasted explicitly with **machine translation**, which is *not*
  classification — translation has to *generate* new structured output,
  not just pick a label.

---

## 6. Model-Based Classification

Echoing the **model-based vs. model-free** distinction from
reinforcement learning: rather than learning directly from prediction
errors (model-free), **model-based classification** builds an explicit
probabilistic model from data, then does **inference** in that model to
make predictions. Today: model-based. Model-free classification methods
come in later lectures.

**The model:** a Bayes net whose random variables are the class label
`Y` (e.g. spam/ham, or digit 0–9) and a set of input features. The
simplest possible structure that still works well — **naïve Bayes** —
puts `Y` as a single parent with all features as independent children:

```
        Y
   /  |    \
 F1  F2 ... Fn
```

Prediction = probabilistic inference (e.g. variable elimination):
instantiate the observed features, query for the posterior distribution
over `Y`. This gives you not just a label but a **probability** —
allowing questions like "how often is the model right?" (accuracy) and
"are its probabilities even well-calibrated?" (some classifiers only
output a hard label, no usable probability at all).

**Two design questions** any model-based classifier has to answer: what
structure should the Bayes net have (today: the simplest one, naïve
Bayes), and how should its parameters be learned from data (the bulk of
today's lecture).

---

## 7. The Naïve Bayes Independence Assumption

For digit recognition: one node per pixel, all as children of the class
node `Y`. **This is a strong — arguably "radical" — assumption**: it
says that *conditioned on the class*, all the features are
**independent** of each other. Sanity-checked against intuition and
found wanting: knowing an email is spam (or ham) for certain, are the
first two words of the message independent? Clearly not — yet naïve
Bayes assumes exactly that. **Despite being a poor model of the true
generative process, it turns out to work well for classification in
practice.**

```
P(Y, F1, ..., Fn) = P(Y) · ∏i P(Fi | Y)
```

The joint factors into a prior over the class times a product of
per-feature conditionals, each feature depending *only* on the class,
not on the other features.

---

## 8. General Naïve Bayes: Joint Distribution and Parameter Count

A general naïve Bayes model needs:

- A **prior** `P(Y)` — one number per class value.
- For each feature, a small conditional table `P(Fi | Y)` — how likely
  that feature's value is, for each class.

**The payoff, stated explicitly:** the joint distribution being
implicitly described is **exponential** in the number of features — but
the thing you actually have to *store and estimate* is **linear** in the
number of features (one prior table, plus one small conditional table
per feature). This is the same flavor of win as Bayes-net factorization
generally (see the independence/conditional-independence material from
the Bayes-nets lecture): a structural assumption buys an exponential
compression, at the cost of accuracy in cases where the assumption is
actually violated.

---

## 9. Inference in Naïve Bayes

Nothing new here — it's **inference by enumeration**, a special case of
what's already been covered:

```
P(Y | evidence) = α · P(Y, evidence)
                = α · P(Y) · ∏i P(fi | Y)      (product over observed features)
```

Compute the unnormalized product for every value of `Y`, then normalize
(divide by the sum) to get the true posterior. That's the entire
inference procedure — no new algorithm, just the standard Bayes-net
machinery applied to a particularly simple network.

**What's actually new** relative to earlier Bayes-net material: knowing
*where the numbers themselves come from*. The needed quantities — prior
`P(Y)` and each conditional `P(Fi | Y)` — are collectively called the
**parameters** of the model, conventionally denoted **θ (theta)**. As θ
changes, the same naïve Bayes *structure* can behave completely
differently (more spam-suspicious, less spam-suspicious, etc.) — the
parameters are what has to come from data.

---

## 10. Where the Numbers Come From: Estimating Parameters

**Digit example, made concrete.** The prior `P(Y)`: if you collect,
say, a million examples of each digit 0–9 in equal amounts, every prior
would come out to 10% — but real-world digit frequency isn't actually
uniform (ZIP codes in California skew toward digits starting with 9;
certain digits are more common in "general" numeric data than others,
for reasons worth thinking about). **The way you construct/collect your
data set directly shapes the distributions your model will assume hold
at test time** — this becomes important later when discussing risk
minimization and distribution mismatch.

**Feature conditionals, concretely:** e.g. `P(pixel[3,1]=on | Y=5)`
might come out to something like **80%**, estimated simply as "in all
my training examples labeled 5, how often was pixel (3,1) on?" Different
pixels will be diagnostic for different digits (a pixel that's on for
most 6s might be rare for 1s) — this raw counting is exactly maximum
likelihood estimation (formalized in Section 19).

---

## 11. The Bag-of-Words Model for Text

Text needs a different treatment than fixed pixel grids, because
**documents vary in length** and a word's *position* mostly doesn't
matter to its meaning. The standard naïve Bayes text model:

```
P(Y, W1, ..., Wn) = P(Y) · ∏i P(Wi | Y)
```

— structurally identical to the pixel case, but with an extra
assumption: not only are the word-features conditionally independent
given the class (naïve Bayes as usual), they're also **identically
distributed** — `P(Wi | Y)` is the *same* distribution regardless of
position `i`. This means the entire per-class model collapses to a
single **histogram over the vocabulary**, learned once per class rather
than once per document-position. This is the **bag-of-words model** —
and it's exactly why the model generalizes gracefully to
documents of any length (a document one word longer than anything seen
before is not a problem: "the same as it means in any other position").

---

## 12. Worked Example: Classifying an Email, Word by Word

*(Numbers below are cross-checked between the spoken example and the
matching slide, "Computing the class probabilities" / the corpus stats
slide — they agree exactly everywhere both sources give a number.)*

**Corpus stats given:** in this (older, smallish) labeled corpus, **2/3
of emails are ham, 1/3 are spam** — explicitly flagged as unrepresentative
of today's inboxes ("spam has gotten worse since this corpus was
collected"), a concrete illustration of training-distribution vs.
real-world-distribution mismatch.

**A surprising note on the raw word tables:** the single most frequent
word in the *spam* histogram turns out to be **"the"** (not "free," "your
guesses" were "free" and "you," reasonably) — and the most frequent word
in *ham* is also a common function word. **The raw per-class frequency
of a word is not where the classification signal lives** — what matters
is the **relative** likelihood (the ratio) between classes, since common
words like "the" occur often in both. The actual informative words (e.g.
"free") are much further down the frequency list but have a lopsided
*ratio* between spam and ham.

**Step-by-step, watching the running probability update as words arrive
(a live "Gary would you like to lose weight while you sleep" example):**

1. **No words seen yet** — only the prior applies: running total
   `P(spam)=0.33`, `P(ham)=0.67`. Working in **log space** to avoid
   numeric underflow from multiplying many small probabilities together:
   cumulative log-score starts at **`log(0.33) ≈ -1.1`** for spam,
   **`log(0.67) ≈ -0.4`** for ham. Prediction so far: **ham**, "two-thirds
   confident."
2. **"Gary"** — an uncommon word for both classes, but relatively more
   common in ham (direct address by name is a ham-ish feature; "most
   people aren't named Gary"). Belief shifts *more* toward ham — "ten
   times more confident than before."
3. **"would," "you"** — "would" is a harmless, common word that barely
   moves the needle (nudges slightly toward ham); "you" is described as
   "mildly suspicious" — very common in general, but slightly more
   common in spam. Neither is decisive on its own — this is exactly the
   "weak evidence, aggregated" story from Section 3.
4. **"...like to lose weight while you sleep"** — around **"weight"**
   and **"sleep"**, the running product flips: these turn out to be
   strong spam indicators.
5. **Final result** (matching the slide exactly): normalizing the two
   tiny running products gives **`P(spam) = 98.9%`**, **`P(ham) =
   1.1%`** — the model ends up confidently spam despite starting out
   leaning ham on the prior and the word "Gary."

**Takeaway restated:** naïve Bayes classification is exactly this — weak,
individually ambiguous pieces of evidence get multiplied together
(summed in log space), and the class that wins the resulting race is the
prediction. The email above had genuinely **conflicting evidence** (some
words favored ham, some spam), and the final answer only became clear
after weighing all of it.

**On log-space arithmetic (Q&A aside):** you can't just sum log
probabilities and call that a probability — summing logs corresponds to
multiplying probabilities, which is what you want for the *joint*, but
turning the *final* answer back into a normalized probability requires
converting back (exponentiating) — and in practice this has to be done
carefully (e.g. shifting by the max/min term first) to avoid numeric
underflow, rather than exponentiating each huge negative log directly.

---

## 13. A Richer Alternative: The Bigram (Markov) Model

An extension, mentioned as "a great question" from the audience: instead
of assuming each word is independent of the others given the class,
condition each word on **both the class and the previous word**:

```
P(wordk | word(k-1), C)
```

(handling the very first word via a start symbol). Without the class
conditioning, this is exactly the standard **bigram model** of language.
**Conditioned on the class, it's a strictly better language model** — a
document generated from it would read far more like real English than
one generated word-by-word from an unordered bag-of-words histogram.

**But better *classification* accuracy is not guaranteed**, and depends
entirely on how much the bag-of-words assumption actually costs you for
the task at hand. Illustrative test: take a spam document, randomly
permute its words — it's no longer valid English, but **it's still
almost certainly spam**. Same for a sports article permuted into
word-salad versus a politics article — you can no longer read it, but
"goal team win" still reads as sports-shaped. **Tasks whose class label
doesn't hinge on word *order* are exactly where the naïve/bag-of-words
assumption pays for itself** in simplicity without costing much accuracy;
where order genuinely carries the signal, you need the richer (and much
more expensive to estimate) conditional structure.

---

## 14. Training, Held-Out, and Test Data

**Framing question:** why bother with any of this data machinery at all?
Because the actual goal ("the final exam") is performance on **future,
unseen** data — e.g. a spam classifier released into a real inbox. A
large part of ML theory is about formalizing the connection between "did
well on the data I have" and "will do well on data I don't have yet."

**The standard split**, and why each piece exists:

- **Training set** — where parameters get estimated/learned.
- **Test set** — held back, *never* used to inform any modeling
  decision, used only to check final accuracy. Testing on training data
  gives inflated results ("you always know your training data — the
  question is whether you generalized").
- **Held-out data** — a third slice, separate from both, used during
  development to make modeling decisions (e.g. how much smoothing to
  use — Section 20) without contaminating the untouched test set. The
  warning given: researchers are tempted to peek at test-set mistakes
  and adjust accordingly — that peeking is a **slow leak** of test data
  into the modeling process, which is exactly what held-out data is
  there to prevent.

**Parameters vs. hyperparameters:** parameters are things like "the
probability of pixel (7,3) for digit 8" — learned directly from counting
training data. **Hyperparameters** are modeling *choices* that aren't
themselves learned by counting — e.g. whether to fold lowercase and
uppercase versions of a word into one feature, or how much smoothing
strength to use. Hyperparameters are typically tuned by checking
performance on **held-out** data, not training or test data.

---

## 15. Empirical Risk Minimization and What Can Go Wrong

**The principle, informally:** you'd like the model that performs best
on the *true* future test distribution — but you don't know that
distribution (just like not knowing what questions will be on a real
final exam). So instead: pick the model that performs best on your
**training set**, and hope that transfers. This is **empirical risk
minimization**, usually phrased as an optimization problem (today:
direct probability estimation; optimization-based methods come in later
lectures).

**Three distinct ways this can fail**, mapped to a study-for-finals
analogy:

1. **Not enough training data** — your practice exams didn't cover
   enough of the space of possible questions (high sampling variance).
2. **Overfitting** — you had plenty of practice exams but **rote
   memorized** them instead of learning generalizable patterns; the real
   exam looks nothing like what you memorized. Mitigated by limiting
   hypothesis complexity / penalizing overly specific models.
3. **Distribution mismatch** — you studied hard, with plenty of
   practice, but "you studied for CS189 and then walked into the CS188
   final" — the training distribution and the real deployment
   distribution simply don't match (non-stationarity). This is flagged
   as the hardest of the three to say anything precise about, and the
   one ML theory has the *least* to say about compared to the first two.

---

## 16. Evaluation Metrics Beyond Accuracy

**Accuracy** (fraction correctly classified) is the obvious first
metric — and it's **not actually a great one for spam detection**.
Reasons surfaced in discussion:

- **Class imbalance** — if spam is rare, a classifier that never flags
  anything can still score high accuracy while being useless.
- **Asymmetric costs** — a stray "free print cartridges" spam email
  reaching your inbox is a minor annoyance (just don't read it); an
  important email from your boss getting **mis-flagged as spam** is much
  worse. The two error types (false positive vs. false negative) aren't
  equally costly, so raw accuracy — which weighs them equally — isn't
  what you actually want. What you generally want instead is a
  task-specific **utility** with asymmetric costs baked in.
- **Partial credit tasks** (e.g. machine translation) — being "a little
  off" and being "completely wrong" aren't the same failure, so a metric
  that only checks exact match misses something accuracy-style metrics
  can't capture.

---

## 17. Overfitting and Underfitting

**Curve-fitting illustration** (continuous regression, used purely to
build intuition before returning to discrete classification): given a
scatter of data points, fit progressively richer hypothesis classes —

- **Constant function** — captures only the mean; **underfitting**
  (misses real trends in the data).
- **Linear** — better; hypothesis space now includes slope+intercept.
- **Quadratic** — captures a "dip" the line missed.
- **Degree-15 polynomial** — threads almost perfectly through every
  point — but this is **overfitting**: training error keeps dropping as
  more terms are added, while held-out error at some point turns around
  and gets *worse*, because the extra flexibility is now fitting sampling
  noise, not real structure. The hyperparameter here is the polynomial's
  max degree; the right way to pick it is watching **held-out**, not
  training, performance — training accuracy alone is uninformative
  because it can always be driven arbitrarily high by adding flexibility.

**The same failure mode in discrete classification:** a hypothetical
digit example — evidence from most pixels favors "3" over "2," but one
particular corner pixel happens, purely by sampling accident, to have
been on 1–2 times for "2" in the training set and **exactly 0 times**
for "3." Multiplying that zero-derived tiny probability in tips the
entire prediction to "2," **overriding much stronger, more genuinely
informative evidence** from every other pixel. This is overfitting to
"the idiosyncrasies of the samples I have," not to any real, generalizing
signal.

**Odds-ratio audit of the actual spam/ham data**, surfacing the same
problem directly: sorting words by (spam-probability / ham-probability)
finds many words that occur **exactly once** in the training data for
one class and zero times for the other (e.g. "Southwest": once in ham,
never in spam) — driving an extreme, entirely noise-driven odds ratio.
**"It's really dangerous to give things the probability 0"** — the
general principle overfitting is teaching here, independent of the
specific model.

> Naïve Bayes overfitting characteristically shows up as **zeros in
> probability tables** driven by sampling variance. Other model families
> will show overfitting in different, model-specific ways.

---

## 18. Maximum Likelihood Estimation

**Concrete setup:** a jar of jellybeans, red vs. blue, unknown true
ratio. Draw 3 beans: 2 red, 1 blue. The **maximum likelihood estimate
(MLE)** — also called the relative-frequency estimate — just uses the
observed counts directly: `P(red) = 2/3`.

**Why it's called "maximum likelihood":** for corpus `D`, define
`likelihood(D; θ) = P(D; θ)` as a function of the assumed parameter θ.
Trying different candidate values of θ (all-red, 50/50, etc.) and asking
which one makes the *observed* data most probable — the value that
**maximizes** this likelihood turns out to be exactly the empirical
relative frequency. Formally (matching the slide's coin-toss derivation,
generalizing the jellybean example): for evidence `d` with `h` heads/reds
and `t` tails/blues,

```
L(d; θ) = h·log(θ) + t·log(1-θ)
∂L/∂θ = h/θ − t/(1-θ) = 0   ⟹   θ_ML = h/(h+t)
```

For the jellybean case (h=2, t=1): `θ_ML = 2/3` — matching the direct
count.

**Why MLE alone isn't good enough:** it happily assigns probability
**zero** to anything unseen in the training data, and that's exactly the
mechanism behind the overfitting failure in Section 17. The instructor's
framing: "we want our model to assign probability to events it's never
seen" — one rare pixel or word shouldn't be able to torpedo an otherwise
well-balanced aggregation of evidence. The philosophical version of this
worry is attributed to **Laplace**: having observed the sun rise every
morning so far doesn't justify assigning it probability *exactly* 1,
because you know, in principle, it's possible (however unlikely) that it
won't someday.

---

## 19. Laplace Smoothing

**The fix Laplace proposed:** pretend you've already seen every possible
outcome some number of extra times, before looking at the real data —
this guarantees no outcome ever gets probability exactly zero.

**Worked through on the jellybean numbers** (2 red, 1 blue observed):

```
MLE (no smoothing):        P(red) = 2/3 ≈ 0.667      P(blue) = 1/3 ≈ 0.333
Laplace, strength k=1:     P(red) = (2+1)/(3+2) = 3/5 = 0.6
                            P(blue) = (1+1)/(3+2) = 2/5 = 0.4
Laplace, strength k=100:   P(red) = (2+100)/(3+200) ≈ 0.502
                            P(blue) = (1+100)/(3+200) ≈ 0.498
```

Red is still favored throughout, but the estimate gets flatter (closer
to uniform) as the smoothing strength `k` grows — **k is a dial trading
off fit against generalization**: `k=0` recovers raw MLE (fits the
training data best, generalizes worst); very large `k` washes out
everything the data says (never overfits, but also never learns
anything). General form, for a `K`-valued variable with strength `α`:

```
θk = (Nk + α) / (N + Kα)
```

(matching the slide's formula exactly — as `α ≫ N`, this tends to the
uniform prior `1/K`; as `α ≪ N`, it tends to the plain ML estimate
`Nk/N`.) The lecture explicitly notes this is **one specific way** to
estimate probabilities under uncertainty, not the only one — and that
this "knob you can turn to control generalization vs. fitting" pattern
recurs throughout machine learning far beyond naïve Bayes.

*(One passage here is hard to make out in the auto-captions — the
instructor says something like "not going to talk about the conditionals
room, I think we've skipped this too," apparently marking a deliberate
skip of some further topic. What exactly was being skipped isn't
recoverable from the transcript; it isn't picked back up later in the
recording.)*

---

## 20. Smoothing in Practice: Odds Ratios Before and After

Returning to the real spam corpus with smoothing applied: recomputing
the odds-ratio ranking *after* smoothing, the words that previously
dominated purely because they happened to occur once in only one class
**no longer percolate to the top** — they've been pulled back toward
the flat prior, since a single occurrence is no longer enough to
overwhelm it.

**Top ham-favoring and spam-favoring words after smoothing** — mostly
sensible ("money," "credit" — presumably as part of "credit card" — favor
spam), but with a genuinely surprising find flagged explicitly: **default
system font names** turn up as informative features (garbled in the
auto-captions — something like "Helvetica" vs. a font naturally
associated with a particular era/platform's default). The lesson drawn
out loud: **you don't always know in advance which features will end up
useful** — it's worth actually inspecting a trained model to see what it
learned, because it can surface things about the problem you didn't
anticipate.

---

## 21. Tuning Hyperparameters on Held-Out Data

Restating Section 14's point with the smoothing-strength `k` as the
concrete example: `k=0` gives the best possible *training* accuracy (by
construction — that's literally the maximum-likelihood estimate), so
**you cannot pick k by looking at training accuracy** — it will always
tell you to smooth as little as possible. Instead: fit parameters on
training data, then check different hyperparameter settings (like `k`)
against **held-out** data to find the setting that actually generalizes,
and only then run a **final** evaluation on the untouched test set.

---

## 22. Errors and Features

Every real classifier makes mistakes. Two real error examples surfaced
from the instructor's own quickly-built naïve Bayes spam system: a
promotional email misclassified as ham, and a "$30 Amazon promotional
certificate" email misclassified as spam when it may have been legitimate
— both flagged as genuinely hard/ambiguous cases, possibly just noise in
the underlying data rather than a fixable modeling error.

**The general fix for errors: more/better features.** For spam, words
alone weren't sufficient — ecosystem metadata mattered too (Section 3).
For digits, raw pixels alone aren't sufficient — edge/loop/rotation-and-
scale-invariant features do better (Section 4). Both can be folded
straight into naïve Bayes as additional variables; future lectures cover
more flexible ways to add and even *induce* such features automatically.

**Aside: spam classification as an adversarial arms race.** Unlike digit
recognition (a 7 isn't trying to evade detection), **spam is generated by
people actively trying to defeat the classifier**. Historical anecdote:
spammers once started appending entire chapters of *Pride and Prejudice*
to spam emails specifically to dilute the word-frequency signal and slip
past word-based filters — prompting defenders to shift toward
sender/metadata-based features, prompting spammers to spoof sender
information, prompting detection of templated mass-sends, and so on.
**This is why spam filtering is a poor "canonical" example of
classification** despite being pedagogically convenient — most real
classification problems don't have an adversary actively reshaping the
input distribution to defeat you.

---

## 23. Closing Summary (as delivered)

The lecture ends on the note that estimating probabilities directly (as
done throughout today) is **one approach among several** in machine
learning — later lectures cover optimization-based methods more
generally — but the core recurring pattern introduced today (a knob
controlling the fit/generalization tradeoff, evaluated via held-out data,
checked finally on an untouched test set) recurs everywhere in ML, well
beyond naïve Bayes specifically.

---

## 24. Appendix — Bayesian Learning (Slide Deck Only, Not Reached in This Recording)

*Everything below is drawn exclusively from `cs188-sp26-lec21.pdf`. None
of it is narrated anywhere in the 2018 video transcribed above — see the
note at the top of this file. Treat this as a compact reading summary of
the deck's second half, not a transcript.*

**Three statistical stances on supervised learning**, building on
Section 18–19's maximum likelihood estimate:

```
Maximum likelihood:   h_ML  = argmax_h P(D | h)
Maximum a posteriori: h_MAP = argmax_h P(h | D) = argmax_h P(D | h) P(h)
                        (h_ML = h_MAP when the prior P(h) is uniform)
Bayesian learning:    P(y | x, D) = Σ_h P(y | x; h) P(D | h) P(h)
```

MAP adds a prior over hypotheses `P(h)` (reflecting prior knowledge or a
simplicity preference) on top of the likelihood term Section 18 already
covered. **Full Bayesian learning goes further still**: rather than
committing to any single hypothesis (not even the MAP one), it keeps the
**entire posterior distribution over hypotheses** and averages
predictions across all of them, weighted by how probable the data makes
each one.

### Worked example: Surprise Candy Co.

Five kinds of candy bags, each an unknown mixture of cherry/lime candies,
with given prior probabilities over which kind of bag you have:

```
h1 (10%): 100% cherry        h2 (20%): 75% cherry / 25% lime
h3 (40%): 50% cherry / 50% lime
h4 (20%): 25% cherry / 75% lime      h5 (10%): 100% lime
```

Draw 5 candies from an unknown bag, **all lime**. Posterior over which
bag it is, via `P(hk | D) = α · P(D | hk) · P(hk)`:

```
P(h1|5 limes) = α · 0.0^5  · 0.1 = 0                    → 0
P(h2|5 limes) = α · 0.25^5 · 0.2 = 0.000195α             → 0.00122
P(h3|5 limes) = α · 0.5^5  · 0.4 = 0.0125α               → 0.07803
P(h4|5 limes) = α · 0.75^5 · 0.2 = 0.0475α               → 0.29650
P(h5|5 limes) = α · 1.0^5  · 0.1 = 0.1α                  → 0.62424
                          (α = 1/0.16005 ≈ 6.2424)
```

`h5` (all-lime bag) is now the most probable explanation, though not
certain. Full Bayesian **prediction** for the next draw averages over all
five hypotheses weighted by their posteriors, rather than just betting
everything on `h5`:

```
P(lime on 6th | 5 limes) = Σk P(lime | hk) · P(hk | 5 limes)
                          = 0×0 + 0.25×0.00122 + 0.5×0.07830
                            + 0.75×0.29650 + 1.0×0.62424
                          = 0.88607
```

As more limes are drawn in a row, the deck shows this prediction
probability climbing smoothly from 0.5 (no data) toward ~0.97 (10 limes
in a row) — approaching, but never quite reaching, certainty, since `h5`
never gets literally ruled *in* with probability 1 (only `h1`, contradicted
by a single lime draw, gets ruled fully *out*).

**Drawback flagged on the slide:** exact Bayesian learning requires
summing over the entire hypothesis space, which can be expensive or
outright intractable when `H` is large or infinite. (MCMC and related
sampling methods are noted as having driven a major practical revival of
Bayesian learning for exactly this reason.)

### The "poverty of the stimulus" argument, and the numbers game

A second illustration of Bayesian reasoning favoring simpler hypotheses,
posed via language acquisition: children learn grammar quickly from only
*positive* examples of valid sentences, never told which sentences are
invalid. If every grammar consistent with the data were equally
available, the simplest one technically consistent with "some sentences
are valid" is "**all** strings are valid" — which is not what children
actually learn, historically taken as an argument for strong innate
grammatical structure.

**The deck pushes back on this via a toy "numbers game"** (credited to
Tenenbaum via Murphy Ch. 3): shown the set `{16, 8, 2, 64}` and asked
what the underlying concept is, humans strongly favor "powers of 2" over
"all numbers," even though "all numbers" is also perfectly consistent
with the data. A Bayesian likelihood calculation shows why, **without**
needing to invoke innate structure as the explanation:

```
P({16,8,2,64} | powers of 2) = (1/7)^4 ≈ 4.2×10⁻⁴
P({16,8,2,64} | everything)  = (1/100)^4 = 10⁻⁸
```

The "powers of 2" hypothesis makes this *specific* data enormously more
likely than "everything" does (roughly 40,000× more likely) — under the
assumption that examples are drawn uniformly at random from the true
underlying set, seeing four powers of 2 in a row is a near-coincidence
under "everything" but expected under "powers of 2." The slide frames
this likelihood gap as "far outweighing any reasonable simplicity-based
prior," offering an alternative to "children must have innate grammar"
that doesn't require assuming special-purpose innate structure — plain
Bayesian inference over a hypothesis space already favors the
simpler/more specific explanation whenever it fits the observed examples
this well. A follow-up figure compares this Bayesian model's predicted
generalization patterns for several different example sets (`60`;
`60,80,10,30`; `60,52,57,55`; `16`; `16,8,2,64`; `16,23,19,20`) directly
against measured human generalization judgments, shown as closely
matching.

### Summary slide (verbatim structure)

- Statistical learning replaces an arbitrary loss function (e.g. squared
  error) with a general probability-based approach.
- For parameters of a simple discrete distribution, **ML = empirical
  frequency**; smoothing addresses the resulting problems with unseen
  events (exactly Sections 18–20 above).
- Naïve Bayes classifiers are simple Bayes nets that work well for many
  tasks (Sections 6–13 above).
- Bayesian learning is the most general approach of the three, but can be
  intractable for large hypothesis spaces.
