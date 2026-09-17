# 20 evaluation tasks of varying difficulty
TASKS = [
    # Easy (5)
    {"id": "E1", "spec": "Write a function `add_numbers(a, b)` that returns the sum of two numbers."},
    {"id": "E2", "spec": "Write a function `is_even(n)` that returns True if n is even, False otherwise."},
    {"id": "E3", "spec": "Write a function `reverse_string(s)` that reverses a string."},
    {"id": "E4", "spec": "Write a function `celsius_to_fahrenheit(c)` that converts Celsius to Fahrenheit."},
    {"id": "E5", "spec": "Write a function `count_vowels(s)` that counts the number of vowels in a string (case-insensitive)."},
    
    # Medium (8)
    {"id": "M1", "spec": "Write a function `find_max(lst)` that returns the maximum value in a list without using the built-in max() function. Handle empty list by returning None."},
    {"id": "M2", "spec": "Write a function `is_palindrome(s)` that checks if a string is a palindrome, ignoring spaces, punctuation, and capitalization."},
    {"id": "M3", "spec": "Write a function `factorial(n)` that calculates the factorial of n recursively. Raise ValueError for negative n."},
    {"id": "M4", "spec": "Write a function `fibonacci(n)` that returns the nth Fibonacci number. n=0 returns 0, n=1 returns 1. Optimize it with memoization or iterative approach."},
    {"id": "M5", "spec": "Write a function `merge_dicts(dict1, dict2)` that merges two dictionaries. If there are overlapping keys, the values should be added together (assuming they are numbers)."},
    {"id": "M6", "spec": "Write a function `flatten_list(nested_list)` that takes a list of lists and returns a single flat list."},
    {"id": "M7", "spec": "Write a function `remove_duplicates(lst)` that removes duplicate elements from a list while preserving the original order."},
    {"id": "M8", "spec": "Write a function `binary_search(arr, target)` that returns the index of target in a sorted array arr, or -1 if not found. Must run in O(log n) time."},
    
    # Hard (7)
    {"id": "H1", "spec": "Write a function `lru_cache_impl(capacity)` that returns a class or implements an LRU Cache with get and put methods in O(1) time complexity."},
    {"id": "H2", "spec": "Write a function `is_valid_parentheses(s)` that takes a string containing just the characters '(', ')', '{', '}', '[' and ']', and determines if the input string is valid (properly closed and nested)."},
    {"id": "H3", "spec": "Write a function `longest_substring_without_repeating(s)` that finds the length of the longest substring without repeating characters."},
    {"id": "H4", "spec": "Write a function `word_frequency(text)` that takes a string of text, removes punctuation, ignores case, and returns a dictionary of words and their frequency, sorted by frequency (descending) and then alphabetically."},
    {"id": "H5", "spec": "Write a function `evaluate_postfix(expression)` that evaluates a postfix notation (Reverse Polish Notation) string like '3 4 + 2 *' -> 14. Support +, -, *, /."},
    {"id": "H6", "spec": "Write a function `topological_sort(graph)` that takes a directed acyclic graph represented as a dictionary {node: [neighbors]} and returns a valid topological ordering. Handle cycles by raising a ValueError."},
    {"id": "H7", "spec": "Write a function `roman_to_int(s)` that converts a valid Roman numeral string to an integer. Example: 'MCMXCIV' -> 1994."}
]
