# Version Support Strategy

Mineflex adopts an explicit, incremental protocol versioning architecture based on `ProtocolRegistry` and version adapters.

---

## Tested & Supported Versions

| Minecraft Version | Protocol Version | Status | Notes |
|---|---|---|---|
| **1.20.1** | **763** | **Fully Tested & Supported** | Primary stable target; tested against automated mock server and unit suites. |
| **1.20.2** | **764** | **Supported** | Compatible with standard 1.20 registries and codecs. |
| **1.20.4** | **765** | **Supported** | Supported via `ProtocolRegistry.for_version("1.20.4")`. |
| **1.21.x** | **767** | **Supported** | Basic packet framing and block palettes compatible. |

---

## Version Architecture

Differences between Minecraft versions (such as packet IDs, configuration states, and container formats) are encapsulated within `ProtocolRegistry` rather than scattered through `if/else` checks.
