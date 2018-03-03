# 

A python library for generating regular expressions that will match given text.

---

When searching for tools to generate regular expressions, there is a chorus of discouragement stating that computers cannot generate human meaningful regular expressions and therefore are not useful.

This is true. Computers still struggle to generate human meaningful expressions. However that does not make them not useful. Today, machine learning is expanding rapidly, with feature sets playing an ever important role. The ability for a program to generate new features from text is therefore an interesting topic, and worthy of exploration. 

---

```
Follow me and soon you'll be,
familiar with everything you see.
To break from me is also easy,
But I'll return as quick as you count one, two, three.
```

# Code

Regular Expression generator that uses a genetic algorithm to create patterns that will match a given text. It works by optimizing "^.*$" based on a scoring function.

To alternate between more general and more specific solutions, costs can be associated with the usage of literals, character classes, and repetitions. 

# Applications

- Train ml algorithms with little human understanding of the data (find unpredicted cases)

# Note to Self

when done, answer this github question: https://stackoverflow.com/questions/17749987/python-library-to-generate-regular-expressions



