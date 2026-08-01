# Chapter 12 Multiple-Choice Questions: Quantifying Uncertainty

Based only on Chapter 12, **Quantifying Uncertainty**. The chapter covers acting under uncertainty, probability notation, full joint distributions, independence, Bayes’ rule, conditional independence, naive Bayes, and probabilistic Wumpus World reasoning.    

---

## Questions

1. **What is the main purpose of Chapter 12?**
   A. To eliminate uncertainty from intelligent agents
   B. To represent uncertainty using numeric degrees of belief
   C. To replace probability with propositional logic
   D. To prove all plans are guaranteed to succeed

2. **Which of the following is a major source of uncertainty for real-world agents?**
   A. Perfect observability
   B. Partial observability
   C. Complete knowledge of all outcomes
   D. Fully deterministic sensors

3. **Why can logical agents struggle in uncertain environments?**
   A. They cannot store facts
   B. They must often consider every possible explanation or contingency
   C. They always use probability
   D. They never use belief states

4. **The logical qualification problem refers to the difficulty of:**
   A. Listing all conditions needed to guarantee an action’s success
   B. Computing a truth table
   C. Defining a random variable
   D. Choosing the smallest sample space

5. **In the airport taxi example, why might leaving 24 hours early be irrational?**
   A. It has zero chance of success
   B. It ignores all evidence
   C. It may have poor utility because of excessive waiting
   D. It cannot be represented probabilistically

6. **A rational decision under uncertainty depends on:**
   A. Probability only
   B. Utility only
   C. Both likelihood and outcome value
   D. Syntax only

7. **Probability theory represents:**
   A. Degrees of belief
   B. Absolute logical truth only
   C. Physical movement rules
   D. Utility preferences only

8. **Utility theory represents:**
   A. An agent’s preferences over outcomes
   B. The number of possible worlds
   C. The syntax of propositions
   D. The probability axioms

9. **Decision theory combines:**
   A. Probability theory and utility theory
   B. Logic and search trees only
   C. Syntax and grammar only
   D. Random variables and actuators only

10. **The principle of maximum expected utility says an agent should choose the action that:**
    A. Has the fewest outcomes
    B. Has the highest probability of any single outcome
    C. Has the highest probability-weighted average utility
    D. Avoids probability calculations

11. **A decision-theoretic agent’s belief state differs from earlier belief states because it includes:**
    A. Only impossible states
    B. Probabilities over states
    C. Only logical contradictions
    D. No information about the world

12. **In the toothache example, why is the rule “Toothache implies cavity” incorrect?**
    A. Toothaches may have causes other than cavities
    B. Cavities are impossible
    C. Toothaches cannot be observed
    D. Probability forbids medical diagnosis

13. **Which of the following is one reason strict logical rules fail in diagnosis?**
    A. Laziness
    B. Perfect knowledge
    C. Guaranteed outcomes
    D. Complete testing

14. **Theoretical ignorance means:**
    A. The agent refuses to reason
    B. The domain theory is incomplete
    C. The agent has too many utilities
    D. The sample space is empty

15. **Practical ignorance means:**
    A. Necessary tests may not have been run or may be unavailable
    B. The agent knows every hidden variable
    C. All outcomes are guaranteed
    D. The world has no uncertainty

16. **A probability statement such as P(cavity | toothache) is relative to:**
    A. The agent’s current evidence
    B. The agent’s programming language syntax
    C. The number of actions available
    D. The name of the random variable only

17. **If a patient later receives new evidence, the probability of cavity can change because:**
    A. The patient’s real condition must have changed
    B. The agent’s knowledge state has changed
    C. Probability axioms no longer apply
    D. Utilities are no longer needed

18. **A sample space is:**
    A. The set of all possible worlds under consideration
    B. The set of all actions an agent can take
    C. The list of all utility values only
    D. The syntax of probability notation

19. **Possible worlds in a sample space are:**
    A. Mutually exclusive and exhaustive
    B. Always overlapping
    C. Always impossible
    D. Always equally useful

20. **A fully specified probability model assigns probabilities to:**
    A. Each possible world
    B. Only the most likely action
    C. Only impossible events
    D. Only utility functions

21. **The total probability of all possible worlds in a sample space must equal:**
    A. 0
    B. 0.5
    C. 1
    D. 2

22. **An event in probability theory is best understood as:**
    A. A set of possible worlds
    B. A single actuator command
    C. A utility function
    D. A theorem-proving rule

23. **The probability of a proposition is found by:**
    A. Adding the probabilities of worlds where the proposition is true
    B. Subtracting all false worlds from 2
    C. Choosing the largest utility value
    D. Counting only the number of actions

24. **A prior probability is:**
    A. A probability before considering new evidence
    B. A probability after all possible evidence is known
    C. A guaranteed logical conclusion
    D. A utility value

25. **A posterior probability is:**
    A. A probability conditioned on evidence
    B. A probability that ignores observations
    C. A random action
    D. A full joint distribution

26. **The expression P(a | b) is read as:**
    A. Probability of b given a
    B. Probability of a given b
    C. Probability of a and b being impossible
    D. Utility of a after b

27. **The conditional probability P(a | b) is defined as:**
    A. P(a) + P(b)
    B. P(a ∧ b) / P(b), when P(b) > 0
    C. P(a) / P(a ∧ b)
    D. P(b) / P(a)

28. **The product rule states that:**
    A. P(a ∧ b) = P(a | b)P(b)
    B. P(a ∧ b) = P(a) + P(b)
    C. P(a | b) = P(a) always
    D. P(a) = P(b) always

29. **A random variable is:**
    A. A function from possible worlds to values
    B. A utility value for an action
    C. A syntax rule
    D. A guaranteed outcome

30. **A Boolean random variable has which possible values?**
    A. True and false
    B. Only true
    C. Only numbers from 1 to 6
    D. Any real number only

31. **A probability distribution over a discrete random variable gives:**
    A. A probability for each possible value of the variable
    B. A single action for the agent
    C. A list of all utilities only
    D. A proof that uncertainty is impossible

32. **A full joint distribution specifies:**
    A. The probability of every complete assignment of values to the variables
    B. Only the probability of the most likely event
    C. Only the prior probability of one variable
    D. Only action utilities

33. **In the Toothache, Cavity, Catch example, the full joint distribution has:**
    A. 2 entries
    B. 4 entries
    C. 8 entries
    D. 16 entries

34. **Marginalization is also called:**
    A. Summing out
    B. The product rule
    C. Utility maximization
    D. Conditioning on all variables

35. **Marginalization is used to:**
    A. Sum over variables that are not needed in the final query
    B. Remove all probabilities from a model
    C. Choose an action without evidence
    D. Convert utility into syntax

36. **Normalization is used to:**
    A. Scale relative probabilities so they sum to 1
    B. Make every event equally likely
    C. Remove evidence from the model
    D. Replace posterior probability with utility

37. **In the chapter’s full joint example, P(cavity | toothache) equals:**
    A. 0.2
    B. 0.4
    C. 0.6
    D. 0.8

38. **Why is a full joint distribution often impractical?**
    A. It grows exponentially with the number of variables
    B. It cannot answer probabilistic queries
    C. It never sums to 1
    D. It ignores possible worlds

39. **For n Boolean variables, a full joint distribution has size:**
    A. O(n)
    B. O(n²)
    C. O(2ⁿ)
    D. O(log n)

40. **Independence between a and b means:**
    A. Knowing b does not change the probability of a
    B. a logically implies b
    C. a and b must both be false
    D. a and b cannot appear in the same sample space

41. **If a and b are independent, then:**
    A. P(a ∧ b) = P(a)P(b)
    B. P(a ∧ b) = P(a) + P(b)
    C. P(a | b) = P(b)
    D. P(a) = 0

42. **Why is independence useful?**
    A. It can factor a large distribution into smaller pieces
    B. It makes all variables logically equivalent
    C. It removes the need for evidence
    D. It guarantees every action succeeds

43. **The chapter’s weather and dental example illustrates that:**
    A. Weather and dental variables can be treated as independent in that model
    B. Weather always causes cavities
    C. Toothache always predicts rain
    D. Independence is never useful

44. **Bayes’ rule is especially useful for:**
    A. Reasoning from observed effects back to possible causes
    B. Removing all uncertainty
    C. Avoiding priors
    D. Proving propositional validity

45. **In medical diagnosis, Bayes’ rule often helps compute:**
    A. P(disease | symptom) from causal knowledge such as P(symptom | disease)
    B. The exact utility of every possible world without probabilities
    C. The syntax of random variables
    D. A guaranteed plan

46. **The meningitis example demonstrates that:**
    A. A strong symptom likelihood can still lead to a small disease posterior if the disease prior is very low
    B. Rare diseases always have high posterior probability
    C. Bayes’ rule ignores base rates
    D. Symptoms logically imply diseases

47. **Conditional independence means:**
    A. Two variables are independent once another variable is known
    B. Two variables are always independent in every context
    C. Two variables are logically equivalent
    D. Evidence can never change probabilities

48. **In the dental example, Toothache and Catch can be conditionally independent given:**
    A. Cavity
    B. Weather
    C. Utility
    D. Sample space

49. **The naive Bayes model assumes that:**
    A. Effect variables are conditionally independent given the cause variable
    B. All variables are absolutely independent of everything
    C. Evidence is impossible to observe
    D. Priors are never used

50. **In the probabilistic Wumpus World example, probability improves on pure logic by:**
    A. Ranking unknown squares by how likely they are to contain pits
    B. Proving every unknown square is safe
    C. Removing all hidden information
    D. Ignoring breezes and pits

---

## Answer Key

1. B
2. B
3. B
4. A
5. C
6. C
7. A
8. A
9. A
10. C
11. B
12. A
13. A
14. B
15. A
16. A
17. B
18. A
19. A
20. A
21. C
22. A
23. A
24. A
25. A
26. B
27. B
28. A
29. A
30. A
31. A
32. A
33. C
34. A
35. A
36. A
37. C
38. A
39. C
40. A
41. A
42. A
43. A
44. A
45. A
46. A
47. A
48. A
49. A
50. A
