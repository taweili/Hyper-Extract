# Machine Learning

**Category**: Artificial Intelligence  
**Created**: February 22, 2026  
**Last Updated**: February 22, 2026

---

## Overview

**Machine Learning (ML)** is an important branch of **Artificial Intelligence (AI)**, dedicated to studying how computer systems can automatically improve through experience.

The core idea of machine learning is: instead of relying on explicit hard-coded rules, learn patterns and regularities from data through algorithms.

---

## Definition

Machine learning is a multidisciplinary field involving **probability theory**, **statistics**, **approximation theory**, **convex analysis**, **computational complexity theory**, and many other disciplines.

It is the core of artificial intelligence and the fundamental way to make computers intelligent. Machine learning algorithms automatically discover patterns by analyzing large amounts of data, and use these patterns to make predictions or decisions on unknown data.

---

## Classification System

### 1. Supervised Learning

Supervised learning uses **labeled training data** for learning. The algorithm learns mapping relationships from input features and corresponding output labels.

**Common Algorithms**:
- Linear Regression
- Logistic Regression
- Decision Tree
- Random Forest
- Support Vector Machine (SVM)
- Neural Networks

**Application Scenarios**:
- House price prediction
- Spam classification
- Image recognition
- Medical diagnosis

### 2. Unsupervised Learning

Unsupervised learning uses **unlabeled data**, and the algorithm needs to discover structures and patterns in the data on its own.

**Common Algorithms**:
- Clustering: K-Means, Hierarchical Clustering, DBSCAN
- Dimensionality Reduction: PCA, t-SNE, Autoencoders
- Association Rule Mining: Apriori, FP-Growth

**Application Scenarios**:
- Customer segmentation
- Anomaly detection
- Recommendation systems
- Topic modeling

### 3. Reinforcement Learning (RL)

Reinforcement learning learns through **interaction between an agent and the environment**. The agent obtains rewards (Reward) through trial and error, with the goal of maximizing long-term cumulative rewards.

**Core Concepts**:
- State
- Action
- Policy
- Reward
- Value Function

**Common Algorithms**:
- Q-Learning
- Policy Gradient
- Actor-Critic
- DQN (Deep Q-Network)
- PPO (Proximal Policy Optimization)

**Application Scenarios**:
- Game AI (e.g., AlphaGo)
- Robot control
- Autonomous driving
- Resource scheduling

### 4. Semi-Supervised Learning

Combines a small amount of labeled data with a large amount of unlabeled data for learning.

### 5. Self-Supervised Learning

Constructs supervision signals from the data itself, without manual annotation.

---

## Key Concepts

### 1. Feature

Features are measurable attributes or variables that describe data. In machine learning, features are the representation of the raw data input to the model.

**Examples**:
- In house price prediction, features may include: area, number of rooms, location, construction year
- In image recognition, features may be pixel values or extracted visual features

### 2. Model

A model is a mathematical representation or function learned by a machine learning algorithm, used to predict outputs from input features.

**Common Model Types**:
- Linear models
- Tree models
- Neural network models
- Probabilistic graphical models

### 3. Training

Training is the process of adjusting model parameters using training data, so that the model can learn patterns in the data.

### 4. Inference/Prediction

Inference is the process of using a trained model to make predictions on new data.

### 5. Overfitting

Overfitting refers to the phenomenon where a model performs well on training data but has poor generalization ability on new data.

### 6. Underfitting

Underfitting refers to the phenomenon where a model fails to fully learn data patterns, performing poorly on both training and test sets.

---

## Related Fields

### 1. Deep Learning

Deep learning is a subfield of machine learning that uses multi-layer **neural networks** to learn representations of data.

**Common Network Architectures**:
- Convolutional Neural Networks (CNN): Suitable for images
- Recurrent Neural Networks (RNN)/Transformer: Suitable for sequential data (text, speech)
- Generative Adversarial Networks (GAN): Used to generate new data

### 2. Data Mining

Data mining is the process of extracting useful information and knowledge from large amounts of data, with many overlapping techniques with machine learning.

### 3. Natural Language Processing (NLP)

NLP focuses on enabling computers to understand, interpret, and generate human language.

**Applications**:
- Machine translation
- Sentiment analysis
- Question answering systems
- Text summarization

### 4. Computer Vision

Computer vision aims to enable computers to obtain meaningful information from images or videos.

**Applications**:
- Image recognition
- Object detection
- Image segmentation
- Face recognition

### 5. Statistics

Statistics provides the theoretical foundation and methodological support for machine learning.

---

## Application Scenarios

1. **Healthcare**: Disease diagnosis, drug discovery, genomic analysis
2. **Finance**: Credit scoring, fraud detection, algorithmic trading
3. **Retail**: Recommendation systems, demand forecasting, customer segmentation
4. **Transportation**: Autonomous driving, traffic prediction, route optimization
5. **Manufacturing**: Quality control, predictive maintenance, supply chain optimization
6. **Education**: Personalized learning, intelligent tutoring, learning analytics
7. **Entertainment**: Content recommendation, game AI, special effects generation

---

## Historical Development

### 1940s-1950s: Origins

- 1943: Walter Pitts and Warren McCulloch proposed the mathematical model of neurons
- 1950: Alan Turing proposed the "Turing Test"
- 1952: Arthur Samuel developed the first checkers learning program
- 1959: Samuel first used the term "machine learning"

### 1960s-1970s: Early Development

- 1967: Nearest Neighbor algorithm proposed
- 1969: Minsky and Papert published "Perceptrons", pointing out the limitations of single-layer perceptrons

### 1980s-1990s: Renaissance

- 1986: Backpropagation algorithm became popular again
- 1989: Convolutional neural network concept proposed
- 1995: Support Vector Machine (SVM) proposed
- 1997: LSTM (Long Short-Term Memory) proposed

### 2000s-2010s: Big Data Era

- 2006: Geoffrey Hinton proposed "Deep Belief Networks", deep learning began to revive
- 2012: AlexNet led significantly in ImageNet competition, marking the arrival of the deep learning era
- 2014: GAN (Generative Adversarial Network) proposed
- 2017: Transformer architecture proposed

### 2020s-Present: Large Model Era

- 2020: GPT-3 released
- 2022: ChatGPT released, causing global attention
- 2023: Multimodal large models emerged

---

## Important People and Institutions

### People

- **Geoffrey Hinton**: "Father of Deep Learning", important contributor to the backpropagation algorithm
- **Yann LeCun**: Pioneer of convolutional neural networks, first director of Facebook AI Research
- **Yoshua Bengio**: Important scholar in the field of deep learning
- **Andrew Ng**: Co-founder of Google Brain, co-founder of Coursera
- **Demis Hassabis**: Founder of DeepMind, leader of the AlphaGo project

### Institutions

- **Google DeepMind**: Research institution for AlphaGo, AlphaFold
- **OpenAI**: Research institution for GPT series models
- **Meta AI** (formerly Facebook AI): PyTorch, FAIR
- **Microsoft Research Asia (MSRA)**
- **Stanford Artificial Intelligence Laboratory (SAIL)**
- **MIT Computer Science and Artificial Intelligence Laboratory (CSAIL)**

---

## Challenges and Future Directions

### Current Challenges

1. Data requirements: Deep learning requires large amounts of labeled data
2. Interpretability: Black-box models make it difficult to understand decision-making processes
3. Robustness: Adversarial examples can easily cause model failures
4. Fairness: Algorithms may have biases
5. Computational resources: Large models require enormous computing power
6. Security: Security safeguards for AI systems

### Future Directions

1. Few-shot Learning
2. Explainable AI
3. Federated Learning
4. Causal Inference
5. Multimodal Learning
6. Autonomous Learning

---

## References

- Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.
- Murphy, K. P. (2012). *Machine Learning: A Probabilistic Perspective*. MIT Press.
- Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning*. Springer.
