# Authentication in Mineflex

Mineflex isolates authentication mechanisms into `mineflex.auth`.

---

## Authentication Modes

### 1. Offline Mode (`auth="offline"`)

* Standard for local test servers, LAN games, or development environments where `online-mode=false`.
* Generates a deterministic offline UUID using the canonical Mojang algorithm (`UUID.nameUUIDFromBytes("OfflinePlayer:" + username)`).
* Performs zero external network requests.

### 2. Microsoft / Xbox Live Mode (`auth="microsoft"`)

* For connecting to official `online-mode=true` vanilla and public servers.
* Requires valid Microsoft OAuth bearer tokens obtained through the Xbox Live / Mojang authorization pipeline.

---

## Security Guarantees

* **Zero Plaintext Token Logging**: The built-in `CredentialRedactingFilter` in `mineflex.logging` intercepts and redacts passwords, bearer tokens, and session secrets from all output.
* **Exceptions without Leaks**: Exceptions never embed sensitive auth parameters into error messages.
