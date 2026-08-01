# Chapter 13 Canvas Question Bank

**Chapter:** Probabilistic Reasoning  
**Total questions:** 50  
**Suggested value:** 1 point each  
**Question type:** 50 multiple-choice questions  

---

## Multiple-Choice Questions

### Question 1 — Multiple Choice
**Prompt:** Which statement best defines a Bayesian network?

- A. An undirected graph containing only deterministic variables
- B. A directed acyclic graph whose nodes are random variables and whose nodes include local probability information
- C. A table that lists every possible world without using independence assumptions
- D. A search tree used only for deterministic planning

**Correct answer:** B  
**Explanation:** A Bayesian network is a directed acyclic graph in which nodes represent random variables and local distributions quantify the effects of parent nodes.  
**Chapter reference:** Section 13.1

### Question 2 — Multiple Choice
**Prompt:** Why must the graph in a Bayesian network be acyclic?

- A. Every node must have exactly one parent
- B. Conditional probabilities cannot contain Boolean variables
- C. Directed cycles would violate the required directed acyclic graph structure
- D. Cycles prevent the use of continuous variables

**Correct answer:** C  
**Explanation:** Bayesian networks are defined as directed acyclic graphs, so no directed path may return to its starting node.  
**Chapter reference:** Section 13.1

### Question 3 — Multiple Choice
**Prompt:** In a Bayesian network, an arrow from node X to node Y usually indicates that:

- A. X directly influences Y and is a parent of Y
- B. X and Y are always independent
- C. Y must occur before X
- D. X and Y must have the same probability distribution

**Correct answer:** A  
**Explanation:** An arrow from X to Y makes X a parent of Y and usually represents a direct influence from X to Y.  
**Chapter reference:** Section 13.1

### Question 4 — Multiple Choice
**Prompt:** What must be true of the probabilities in each complete row of a conditional probability table?

- A. They must all be equal
- B. They must all be greater than 0.5
- C. They must multiply to 1
- D. They must sum to 1

**Correct answer:** D  
**Explanation:** Each row represents an exhaustive set of possible values for the node under one conditioning case, so the row must sum to 1.  
**Chapter reference:** Section 13.1

### Question 5 — Multiple Choice
**Prompt:** A Boolean node has k Boolean parents. How many independently specifiable probabilities are required for its standard CPT?

- A. k
- B. 2^k
- C. k^2
- D. 2k

**Correct answer:** B  
**Explanation:** Each combination of Boolean parent values creates one conditioning case, producing 2^k independently specifiable probabilities.  
**Chapter reference:** Section 13.1

### Question 6 — Multiple Choice
**Prompt:** What does the probability table for a node with no parents represent?

- A. A posterior distribution
- B. A likelihood function
- C. A prior distribution
- D. A Markov blanket

**Correct answer:** C  
**Explanation:** A node with no parents has an unconditional or prior probability distribution.  
**Chapter reference:** Section 13.1

### Question 7 — Multiple Choice
**Prompt:** In the Toothache–Cavity–Catch example, which conditional independence relationship is represented?

- A. Toothache and Catch are conditionally independent given Cavity
- B. Cavity is independent of Toothache given Catch
- C. Weather is caused by Cavity
- D. Catch and Weather are direct causes of Toothache

**Correct answer:** A  
**Explanation:** Cavity directly influences Toothache and Catch, while Toothache and Catch are conditionally independent once Cavity is known.  
**Chapter reference:** Figure 13.1 and Section 13.1

### Question 8 — Multiple Choice
**Prompt:** In the burglary alarm network, why do JohnCalls and MaryCalls each have only Alarm as a parent?

- A. John and Mary directly observe burglary and earthquake events
- B. John and Mary always call together
- C. Burglary and Earthquake are independent of Alarm
- D. Their calling behavior is modeled as depending directly on whether the alarm sounds

**Correct answer:** D  
**Explanation:** The network assumes that burglary and earthquake influence the calls only through their effect on Alarm.  
**Chapter reference:** Figure 13.2 and Section 13.1

### Question 9 — Multiple Choice
**Prompt:** How does a Bayesian network define the full joint probability distribution?

- A. By adding all prior probabilities
- B. By multiplying each node's conditional probability given its parents
- C. By averaging all CPT entries
- D. By multiplying only the probabilities of root nodes

**Correct answer:** B  
**Explanation:** The joint probability of an assignment is the product of the local conditional probabilities for all nodes.  
**Chapter reference:** Equations 13.1 and 13.2

### Question 10 — Multiple Choice
**Prompt:** Using the burglary network values shown in the chapter, what is the approximate probability of Alarm=true, Burglary=false, Earthquake=false, JohnCalls=true, and MaryCalls=true?

- A. 0.628
- B. 0.0628
- C. 0.00628
- D. 0.000628

**Correct answer:** C  
**Explanation:** Multiplying 0.90 × 0.70 × 0.01 × 0.999 × 0.998 gives approximately 0.00628.  
**Chapter reference:** Section 13.2

### Question 11 — Multiple Choice
**Prompt:** The chain rule expresses a joint probability distribution as:

- A. A product of conditional probabilities ordered over the variables
- B. A sum of all prior probabilities
- C. A single conditional probability table
- D. A ratio of two Markov blankets

**Correct answer:** A  
**Explanation:** The chain rule repeatedly applies the product rule to express a joint distribution as a product of conditional terms.  
**Chapter reference:** Section 13.2

### Question 12 — Multiple Choice
**Prompt:** What is a topological ordering of the nodes in a Bayesian network?

- A. Any alphabetical ordering of variables
- B. An ordering from effects to causes only
- C. An ordering based on probability magnitude
- D. An ordering consistent with the direction of the graph's arrows

**Correct answer:** D  
**Explanation:** In a topological order, every parent appears before its children.  
**Chapter reference:** Section 13.2

### Question 13 — Multiple Choice
**Prompt:** Why does ordering causes before effects usually produce a more compact Bayesian network?

- A. It removes all hidden variables
- B. It tends to reduce the number of parents and required probability parameters
- C. It guarantees that every node has exactly one child
- D. It converts all variables into continuous variables

**Correct answer:** B  
**Explanation:** Causal ordering better exposes conditional independence and usually avoids unnecessary links and CPT entries.  
**Chapter reference:** Sections 13.2 and 13.2, "Compactness and node ordering"

### Question 14 — Multiple Choice
**Prompt:** When constructing a Bayesian network, how should the parents of a node Xi be selected?

- A. Select every earlier node
- B. Select only root nodes
- C. Select a minimal set of earlier nodes that makes Xi conditionally independent of its other predecessors
- D. Select only nodes with identical value ranges

**Correct answer:** C  
**Explanation:** The construction method chooses a minimal parent set that satisfies the required conditional independence relationship.  
**Chapter reference:** Section 13.2

### Question 15 — Multiple Choice
**Prompt:** Why are Bayesian networks described as nonredundant representations?

- A. They avoid specifying the same probability information in multiple inconsistent ways
- B. They contain no conditional probabilities
- C. They require every variable to be independent
- D. They use only one probability value per network

**Correct answer:** A  
**Explanation:** Local conditional distributions define the joint distribution without duplicate probability specifications that could contradict each other.  
**Chapter reference:** Section 13.2

### Question 16 — Multiple Choice
**Prompt:** For n Boolean variables where each node has at most k parents, approximately how many numbers are needed to specify the Bayesian network?

- A. 2^n
- B. n^k
- C. 2n + k
- D. 2^k × n

**Correct answer:** D  
**Explanation:** Each node requires at most 2^k parameters, and there are n nodes.  
**Chapter reference:** "Compactness and node ordering"

### Question 17 — Multiple Choice
**Prompt:** According to the chapter's example, how many probability values are needed for a Bayesian network with 30 Boolean nodes and five parents per node?

- A. 160
- B. 960
- C. 32,000
- D. More than one billion

**Correct answer:** B  
**Explanation:** The chapter computes 2^5 × 30 = 960 parameters.  
**Chapter reference:** "Compactness and node ordering"

### Question 18 — Multiple Choice
**Prompt:** What is a likely consequence of choosing a poor node ordering?

- A. The network becomes cyclic automatically
- B. The network can no longer represent a joint distribution
- C. The network may require more links and many more probability parameters
- D. All variables become independent

**Correct answer:** C  
**Explanation:** Poor orderings may hide useful conditional independence relationships and create unnecessarily large CPTs.  
**Chapter reference:** Figure 13.3 and accompanying discussion

### Question 19 — Multiple Choice
**Prompt:** In the very poor ordering shown in Figure 13.3(b), how many distinct probabilities are required?

- A. 31
- B. 13
- C. 10
- D. 5

**Correct answer:** A  
**Explanation:** The poor ordering requires 31 probabilities, the same number as the full joint distribution for five Boolean variables.  
**Chapter reference:** Figure 13.3

### Question 20 — Multiple Choice
**Prompt:** Which statement is the non-descendants property?

- A. A node is independent of its parents given its children
- B. A node is independent of all descendants given no evidence
- C. A node is independent of its children given its parents
- D. A node is conditionally independent of its non-descendants given its parents

**Correct answer:** D  
**Explanation:** This is the conditional independence property derived from the semantics of Bayesian networks.  
**Chapter reference:** Section 13.2.1

### Question 21 — Multiple Choice
**Prompt:** Which nodes make up the Markov blanket of a variable?

- A. Only its parents
- B. Its parents, its children, and the other parents of its children
- C. Only its descendants
- D. Every node in the network

**Correct answer:** B  
**Explanation:** Conditioning on the Markov blanket makes the variable independent of all other nodes.  
**Chapter reference:** Section 13.2.1

### Question 22 — Multiple Choice
**Prompt:** In the burglary network, which conditioning set makes Burglary independent of JohnCalls and MaryCalls according to the chapter?

- A. JohnCalls and MaryCalls
- B. Burglary and Earthquake
- C. Alarm and Earthquake
- D. Alarm only

**Correct answer:** C  
**Explanation:** Alarm and Earthquake form the relevant Markov blanket around Burglary in the example.  
**Chapter reference:** Section 13.2.1

### Question 23 — Multiple Choice
**Prompt:** What is the first step in testing d-separation using the procedure in the chapter?

- A. Construct the ancestral subgraph containing X, Y, Z, and their ancestors
- B. Delete all evidence nodes
- C. Convert all nodes to continuous variables
- D. Normalize every CPT

**Correct answer:** A  
**Explanation:** The test begins with the ancestral subgraph of the variables of interest and their ancestors.  
**Chapter reference:** Section 13.2.1

### Question 24 — Multiple Choice
**Prompt:** What operation creates the moral graph during a d-separation test?

- A. Remove all links between parents and children
- B. Reverse every arrow
- C. Delete all common children
- D. Connect unlinked nodes that share a common child, then make the graph undirected

**Correct answer:** D  
**Explanation:** Moralization connects co-parents and then replaces directed edges with undirected edges.  
**Chapter reference:** Section 13.2.1

### Question 25 — Multiple Choice
**Prompt:** When does Z d-separate X and Y in the moralized ancestral graph?

- A. When X and Y have the same parents
- B. When Z blocks every path between X and Y
- C. When Z contains no evidence variables
- D. When X and Y are adjacent

**Correct answer:** B  
**Explanation:** If every path between X and Y is blocked by Z, the network entails their conditional independence given Z.  
**Chapter reference:** Section 13.2.1

### Question 26 — Multiple Choice
**Prompt:** What is a deterministic node in a Bayesian network?

- A. A node with no parents
- B. A node whose probability is always 0.5
- C. A node whose value is exactly determined by its parents
- D. A node that must be continuous

**Correct answer:** C  
**Explanation:** Deterministic nodes represent logical or numerical functions of their parent values.  
**Chapter reference:** Section 13.2.2

### Question 27 — Multiple Choice
**Prompt:** What is context-specific independence?

- A. A variable becomes independent of some parents for particular values of other parents
- B. Every variable is independent when no evidence is given
- C. A node has no descendants
- D. A network contains only deterministic nodes

**Correct answer:** A  
**Explanation:** CSI captures independence that holds only in particular conditioning contexts.  
**Chapter reference:** Section 13.2.2

### Question 28 — Multiple Choice
**Prompt:** Which pair of assumptions is used by the noisy-OR model described in the chapter?

- A. Every parent is deterministic, and all parents have equal probability
- B. Only one cause may be active, and all variables are continuous
- C. Causes must be mutually exclusive, and the child must be a root node
- D. All relevant causes are represented, and inhibition of each cause is independent of inhibition of the others

**Correct answer:** D  
**Explanation:** Noisy-OR assumes that the cause set is complete, possibly with a leak node, and that causal inhibitions are independent.  
**Chapter reference:** Section 13.2.2

### Question 29 — Multiple Choice
**Prompt:** What is the purpose of a leak node in a noisy-OR model?

- A. To remove unlikely parent variables
- B. To represent miscellaneous or unmodeled causes
- C. To force the child node to false
- D. To convert the model into a Markov chain

**Correct answer:** B  
**Explanation:** A leak node accounts for possible causes that are not represented explicitly.  
**Chapter reference:** Section 13.2.2

### Question 30 — Multiple Choice
**Prompt:** How many parameters does a noisy logical relationship typically require for a child with k parents?

- A. O(2^k)
- B. O(k^2)
- C. O(k)
- D. O(2k!)

**Correct answer:** C  
**Explanation:** Canonical noisy relationships reduce the parameter requirement from exponential to linear in the number of parents.  
**Chapter reference:** Section 13.2.2

### Question 31 — Multiple Choice
**Prompt:** Why can a continuous variable not be represented by explicitly listing a probability for every possible value?

- A. It has infinitely many possible values
- B. It cannot have parents
- C. Its probabilities never sum to 1
- D. It must always be deterministic

**Correct answer:** A  
**Explanation:** Continuous quantities have infinitely many possible values, so explicit enumeration is impossible.  
**Chapter reference:** Section 13.2.3

### Question 32 — Multiple Choice
**Prompt:** What is the main tradeoff when discretizing a continuous variable?

- A. More categories always increase both accuracy and speed
- B. Fewer categories always eliminate uncertainty
- C. Discretization prevents the use of evidence
- D. More categories may improve accuracy but create larger CPTs and slower inference

**Correct answer:** D  
**Explanation:** Finer discretization can reduce approximation error but increases model and inference complexity.  
**Chapter reference:** Section 13.2.3

### Question 33 — Multiple Choice
**Prompt:** Which two parameters specify a Gaussian distribution in the chapter's discussion?

- A. Minimum and maximum
- B. Mean and variance
- C. Median and mode
- D. Slope and intercept only

**Correct answer:** B  
**Explanation:** A Gaussian distribution is specified by its mean μ and variance σ².  
**Chapter reference:** Section 13.2.3

### Question 34 — Multiple Choice
**Prompt:** What is a hybrid Bayesian network?

- A. A network containing only hidden variables
- B. A network that combines Bayesian and neural networks
- C. A network containing both discrete and continuous variables
- D. A network with both directed and undirected cycles

**Correct answer:** C  
**Explanation:** Hybrid Bayesian networks include a mixture of discrete and continuous random variables.  
**Chapter reference:** Section 13.2.3

### Question 35 — Multiple Choice
**Prompt:** In a linear-Gaussian conditional distribution, how does the child distribution depend on a continuous parent?

- A. The child's mean varies linearly with the parent, while the standard deviation is fixed
- B. The child's variance must be zero
- C. The child's mean is fixed, while the standard deviation varies linearly
- D. The child becomes a Boolean variable

**Correct answer:** A  
**Explanation:** The linear-Gaussian model uses a Gaussian child whose mean is a linear function of the parent and whose standard deviation is constant.  
**Chapter reference:** Section 13.2.3

### Question 36 — Multiple Choice
**Prompt:** A network with discrete variables as parents of continuous linear-Gaussian variables defines which type of distribution?

- A. A uniform distribution
- B. A noisy-OR distribution
- C. A deterministic distribution
- D. A conditional Gaussian distribution

**Correct answer:** D  
**Explanation:** Given any assignment to the discrete variables, the continuous variables have a multivariate Gaussian distribution.  
**Chapter reference:** Section 13.2.3

### Question 37 — Multiple Choice
**Prompt:** Which model uses the cumulative standard normal distribution to create a soft probability threshold?

- A. Noisy-OR
- B. Probit
- C. Enumeration
- D. Pointwise product

**Correct answer:** B  
**Explanation:** The probit model uses the integral of the standard normal distribution to map a continuous value to a probability.  
**Chapter reference:** Section 13.2.3

### Question 38 — Multiple Choice
**Prompt:** Which statement correctly compares the logit and probit models?

- A. They produce exactly identical distributions
- B. Probit has longer tails than logit
- C. Logit has longer tails and is often easier to manipulate mathematically
- D. Logit can be used only with discrete parents

**Correct answer:** C  
**Explanation:** The chapter notes that the logit has longer tails, while the logistic function is often mathematically convenient.  
**Chapter reference:** Section 13.2.3

### Question 39 — Multiple Choice
**Prompt:** Which three claim-cost variables are outputs in the car insurance Bayesian network?

- A. MedicalCost, LiabilityCost, and PropertyCost
- B. Age, Mileage, and VehicleYear
- C. Accident, Theft, and RiskAversion
- D. MakeModel, Airbag, and SafetyFeatures

**Correct answer:** A  
**Explanation:** The network predicts medical, liability, and property costs that the insurer may have to pay.  
**Chapter reference:** Section 13.2.4

### Question 40 — Multiple Choice
**Prompt:** Which two hidden event variables are central to the car insurance case study?

- A. GoodStudent and ExtraCar
- B. Age and YearsLicensed
- C. Airbag and AntiTheft
- D. Accident and Theft

**Correct answer:** D  
**Explanation:** Accident and Theft are hidden future events that must be inferred from observed application information and prior experience.  
**Chapter reference:** Section 13.2.4


---

## Multiple-Choice Questions 41–50

### Question 41 — Multiple Choice
**Prompt:** In the simple Cavity network, how is Weather represented in relation to Cavity, Toothache, and Catch?

- A. Weather is a parent of Cavity
- B. Weather is a child of Toothache
- C. Weather is independent of the other three variables
- D. Weather is conditionally dependent on Catch

**Correct answer:** C  
**Explanation:** Weather appears as an isolated node, indicating that it is independent of Cavity, Toothache, and Catch.  
**Chapter reference:** Figure 13.1

### Question 42 — Multiple Choice
**Prompt:** What does the absence of a direct link between two nodes in a Bayesian network imply?

- A. The variables must always be absolutely independent
- B. The variables may still be dependent through other paths or under some conditioning sets
- C. The variables must have equal probabilities
- D. One of the variables must be hidden

**Correct answer:** B  
**Explanation:** A missing edge does not necessarily imply unconditional independence; dependence can still arise through other paths in the graph.  
**Chapter reference:** Sections 13.1 and 13.2.1

### Question 43 — Multiple Choice
**Prompt:** How many conditioning cases are in the standard CPT of a Boolean node with k Boolean parents?

- A. k
- B. 2k
- C. k²
- D. 2^k

**Correct answer:** D  
**Explanation:** Each unique combination of the k Boolean parent values defines one conditioning case, giving 2^k cases.  
**Chapter reference:** Section 13.1

### Question 44 — Multiple Choice
**Prompt:** How can node ordering affect a Bayesian network that represents the same joint distribution?

- A. It can change the number of links and parameters required
- B. It changes the probability axioms
- C. It forces the graph to contain cycles
- D. It prevents the use of evidence variables

**Correct answer:** A  
**Explanation:** Different orderings can produce networks with very different levels of compactness even when they represent the same joint distribution.  
**Chapter reference:** Figure 13.3

### Question 45 — Multiple Choice
**Prompt:** Which set correctly identifies a node's Markov blanket?

- A. Its parents only
- B. Its children only
- C. Its parents, its children, and the other parents of its children
- D. All of its ancestors and descendants

**Correct answer:** C  
**Explanation:** Conditioning on the Markov blanket makes the node conditionally independent of every other node in the network.  
**Chapter reference:** Section 13.2.1

### Question 46 — Multiple Choice
**Prompt:** Which sequence correctly describes the d-separation procedure presented in the chapter?

- A. Normalize the CPTs, remove evidence nodes, and count paths
- B. Reverse all edges, remove root nodes, and test adjacency
- C. Build the ancestral subgraph, moralize it, make edges undirected, and test whether Z blocks all paths
- D. Convert the Bayesian network into a decision tree and compare leaves

**Correct answer:** C  
**Explanation:** The procedure uses the ancestral subgraph, adds links between co-parents, converts the graph to an undirected graph, and checks whether the conditioning set blocks every path.  
**Chapter reference:** Section 13.2.1

### Question 47 — Multiple Choice
**Prompt:** What is a major parameter advantage of a noisy-OR model with k parents?

- A. It requires O(k) parameters rather than O(2^k)
- B. It requires no probabilities
- C. It always requires exactly one parameter
- D. It requires O(k²) parameters rather than O(k)

**Correct answer:** A  
**Explanation:** Noisy logical relationships can reduce the number of required parameters from exponential to linear in the number of parents.  
**Chapter reference:** Section 13.2.2

### Question 48 — Multiple Choice
**Prompt:** In a linear-Gaussian conditional distribution, which statement is correct?

- A. The child's mean is unrelated to the parent value
- B. The child's mean varies linearly with the continuous parent value
- C. The child's standard deviation must equal zero
- D. The child must be Boolean

**Correct answer:** B  
**Explanation:** The linear-Gaussian model gives the child a Gaussian distribution whose mean is a linear function of the parent and whose standard deviation is fixed.  
**Chapter reference:** Section 13.2.3

### Question 49 — Multiple Choice
**Prompt:** Which statement correctly describes the complexity of exact inference by enumeration for Boolean variables?

- A. Both time and space are constant
- B. Time is linear and space is exponential
- C. Time is exponential, while recursive space usage is linear in the number of variables
- D. Both time and space are always quadratic

**Correct answer:** C  
**Explanation:** Enumeration sums over exponentially many assignments but does not explicitly construct the full joint table, so its recursive space usage is linear.  
**Chapter reference:** Section 13.3.1

### Question 50 — Multiple Choice
**Prompt:** How does variable elimination improve on straightforward enumeration?

- A. It removes all evidence variables before inference
- B. It converts every variable to a continuous variable
- C. It repeats the same subexpressions to verify accuracy
- D. It stores and reuses intermediate factors to avoid repeated calculations

**Correct answer:** D  
**Explanation:** Variable elimination is a dynamic-programming method that computes intermediate factors once and reuses them.  
**Chapter reference:** Section 13.3.2

---

## Compact Answer Key

1. B  
2. C  
3. A  
4. D  
5. B  
6. C  
7. A  
8. D  
9. B  
10. C  
11. A  
12. D  
13. B  
14. C  
15. A  
16. D  
17. B  
18. C  
19. A  
20. D  
21. B  
22. C  
23. A  
24. D  
25. B  
26. C  
27. A  
28. D  
29. B  
30. C  
31. A  
32. D  
33. B  
34. C  
35. A  
36. D  
37. B  
38. C  
39. A  
40. D  
41. C  
42. B  
43. D  
44. A  
45. C  
46. C  
47. A  
48. B  
49. C  
50. D
