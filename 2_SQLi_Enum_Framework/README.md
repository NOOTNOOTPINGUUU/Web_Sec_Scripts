# SQLi Enum Framework

An OOP-based automated enumeration framework for Blind SQL Injection.

## Motivation

During Blind SQLi training in PortSwigger's labs, it often requires a lot of manual enumeration to guess the password. So I decided to build this script to automate the enumeration process.

## Features

* **OOP Architecture**: Built with classes so it's easy to add new payloads or target different databases in the future.
* **Binary Enumeration**: Uses a binary search-style strategy to increase the efficiency of the enumeration process.
* **Threaded Enumeration**: Includes an option for multi-threading to significantly reduce running time.

## Roadmap
* Add support for more databases (MySQL, Microsoft SQL Server).
* Add multiple attack methods for more scenarios.
* Add retry mechanisms for bad internet connections.