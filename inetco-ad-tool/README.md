# Toolkit

A bunch of simple tools for my personal use (and whoever else finds them useful)

- Minimal implementation, these tools are not made to handle all cases. They've only been filled out far enough to deal with the problems so far

- Minimal or non-existent exception handling/testing

## Table of Contents

[TOC]

## Gradle to Maven Dependency Migration

Usage example:

```
$ gradle-to-maven gradleFile 
```

The above example will parse a gradle build file and print out the results

# Development Notes

Development processes followed in this package

## Installation

```
python -m easy_install /path/to/this/project
```

## Dependency Management

### Finding Requirements

Use [pipreqs](https://github.com/bndr/pipreqs) to find requirements. Pipreqs iterates through a project and creates a `requirements.txt` file based on imports. Usage:

```
pip install pipreqs
pipreqs .
```

### Including Requirements

Following the  leave requirements in the `requirements.txt`



## Authors 

Andre Telfer - telfer006@gmail.com