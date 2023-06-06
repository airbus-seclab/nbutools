# `ListUsersInfoFromDB` module

`ListUsersInfoFromDB` dumps users from a Linux NetBackup Primary Server database
using local access (or remotely if the database is configured to allow remote
authenticated access). To do so, it performs the following actions:

* Parse `NBDB.db` configuration files to retrieve the DBA password,
* Connect to the Sybase database and print usernames and hashes of their
  corresponding passwords stored in the database.

**Note:** this tool has the following pre-requites:
* Access to NetBackup configuration files (in theory, only accessible to the
  `root` user),
* Network access to the Sybase database (which only accepts authentication from
  `localhost` by default).
