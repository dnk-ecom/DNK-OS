# (no title)
URL: https://raw.githubusercontent.com/pullboard-dev/pullboard/main/docs/architecture.md

# Identity, storage and trust in the relay

The relay is the hosted service that puts your board on your phone and on your other machines. It stores sealed board records and decides who may fetch them. Reading them takes the board key, and only your paired devices hold it.

This page explains who is who on the relay, every table it stores, what it can read, how pairing moves the board key, and where the protection ends. It is written from the code, and each claim names the file that makes it true. The promises behind it are the H rows in `SPEC.md`, chiefly H5 and H7.

## The parts

```
                     GitHub (people's identity)
                     a GitHub App with Metadata read-only
                               ^
                               | sign-in; a role check on every write
                               |
  +-------------+  ps_ cookie  +-------------------------------------+
  | Phone       |<------------>| Relay                               |
  | browser     | sealed       |  /data/auth.sqlite                  |
  | device key  | records,     |  /data/boards/devices.sqlite        |
  | (IndexedDB) | wrapped keys,|  /data/boards/<board>.journal.sqlite|
  | board keys  | approvals    |  /data/backups/  (14 days)          |
  | (localStorage)             +-------------------------------------+
  +-------------+                    ^ pm_ (machine)    ^ pa_ (one per agent)
        ^                            |                  |
        | the person's tap     +-----+------------------+------+
        |                      | Machine                       |
  +-----+----+   terminal      |  board key file (mode 600)    |
  |  Person  |---------------->|  relay.json: pm_, pa_ cache   |
  +----------+                 |  device roster (public keys)  |
                               |   agent   agent   agent  ...  |
                               +-------------------------------+
```

- **Person**: a human with a GitHub account.
- **Phone**: a browser signed in as the person and paired with a machine.
- **Machine**: a computer with a linked repository. Its CLI holds the board key.
- **Agent**: a worktree on a machine, registered on the board as a seat.
- **Relay**: one Node service (`relay/server.mjs`) that orders sealed records and checks who may fetch them.

## Who is who

### People sign in with GitHub

The relay signs people in through a GitHub App whose only permission is repository Metadata, read-only (`githubAppManifest` in `relay/github.js`). It refuses a GitHub token that carries OAuth App scopes (`tokenResult` in `relay/github.js`). The GitHub user token is used once to learn the account's numeric id and login; only that id and login are stored (`signedIn` in `relay/auth.js`).

The relay asks GitHub for the person's repository role on every write, and caches read checks for under ten minutes (`access` and `ACCESS_WINDOW_MS` in `relay/auth.js`). It pins the repository's numeric id when a board is linked, so a different reposito