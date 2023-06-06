# `PreAuthCartography` module

`PreAuthCartography` performs an unauthenticated remote scan of the given list
of NetBackup hosts to determine their version, role and, if relevant, their
associated primary server. Optionally, it can also categorize relationships
between components and plot them as a graph.

This tool can be useful to provide additional details regarding open TCP `1556`
ports discovered after scanning a target network range.
