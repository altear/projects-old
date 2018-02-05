# Vorpal

A python library for identifying anomalous computer usage by analyzing log files with unsupervised learning.

# Background

An anomaly can be broadly defined as a sample that differs in someway from the rest of the population. There are two<sup>[1](#footnote-1)</sup> types of anomalies:

- Point: samples that differ greatly from the general population
- Contextual: samples that differ greatly from some subset of the population 

This library will only consider point anomalies, because selecting contexts often requires knowledge of the system or data (ie. labels). 

---

The algorithm used for anomaly detection will be iForest, which scores samples by how easy they are to isolate from a population.

---

Feature generation: to be investigated

# References

## Papers

- [Detecting Anomalies in System Log Files using Machine Learning Techniques](ftp://ftp.informatik.uni-stuttgart.de/pub/library/medoc.ustuttgart_fi/BCLR-0148/BCLR-0148.pdf)


- [DeepLog](https://acmccs.github.io/papers/p1285-duA.pdf)

## Tools

- [logilizer](https://github.com/logpai/loglizer)
- [syslog-ng](https://github.com/balabit/syslog-ng)
- [log tools](https://github.com/adamhadani/logtools)
- [go-access](https://goaccess.io/)

## Other

- [Understanding Log Analytics](https://medium.com/@xenonstack/understanding-log-analytics-log-mining-anomaly-detection-5fdd1f94297c)

# Tags

Tags: python, log analysis, log mining, log data, anomaly

# Foot Notes

1. <span id="footnote-1">Other papers/documentation will often define a third type of anomaly called a collective or aggregated anomaly. This type of anomaly is when a groups of samples become anomalous when considered together. I believe this should not be considered a third type of anomaly. The reason for this is that once a collection is formed, it becomes a sample that must be either a contextual or point anomaly. Therefore whether to form collections is a decision to made during preprocessing.</span>