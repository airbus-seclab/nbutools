# `GetConfigInfos` module

`GetConfigInfos` performs an unauthenticated scan of the given list of
NetBackup hosts to determine as much information about their configuration as
possible. It will notably list available `pbx_exchange` extensions, fingerprint
the target's role, display authentication and authorization information, etc.

This tool can be helpful to get more detailed information about a set of hosts
mapped using the `PreAuthCartography` module. Most notably, it can help identify
misconfigurations or inconsistencies.