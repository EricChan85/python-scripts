Write an algorithm called best_compression(S), in Python, that takes a string S and outputs a minimal abbreviation of S. An abbreviation is constructed by replacing repeated consecutive substrings as follows: if the same substring X appears N times consecutively, then those N occurrences can be replaced by the string (X)N.

For example:
Input = babababbaaaaababbbab
Output = b(ab)3b(a)5babbbab