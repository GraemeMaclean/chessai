# Development Notes

## Student-First Mentality

As this project is intended to be used as an educational tool,
we focus on simplicity whenever possible.
The primary reason to introduce complexity is when it is needed for performance reasons.

In order to keep the codebase verbose and easy for students to use,
we follow the following guidelines.

### Semantic Subclasses

In general, this project tries to avoid the use of constants that are used to convey semantics.
Instead, the project prefers semantic subclasses that are intuitive for students.

For example, there are many `chessai.core.action.Action` subclasses as they convey different purposes to students.

### Typing and Default Values

This project is fully typed which is useful beyond the benefits of minimizing type errors.
Types also improve student understanding of the expected inputs and outputs of the functions they will implement.

Beyond typing, default values to functions should be simple types, which is often None.
When using None is not possible, the default value should be semantically meaningful.
For example, the number of files and ranks on a board is defaulted to a constant instead of just an integer 8.
