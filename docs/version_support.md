# Version Support Architecture & Matrix

Mineflex adopts an explicit, incremental protocol versioning architecture based on `ProtocolRegistry` and protocol version adapters.

---

## Supported Versions Matrix

| Minecraft Version | Protocol Version | Configuration State | Encryption (CFB8) | Compression | Status |
|---|---|---|---|---|---|
| **1.20.1** | **763** | Handshake -> Login -> Play | Transparent | zlib | **Fully Supported & Tested** |
| **1.20.2** | **764** | Handshake -> Login -> Config -> Play | Transparent | zlib | **Fully Supported** |
| **1.20.4** | **765** | Handshake -> Login -> Config -> Play | Transparent | zlib | **Supported** |
| **1.21.x** | **767** | Handshake -> Login -> Config -> Play | Transparent | zlib | **Supported** |

---

## 1.20.2+ Configuration State Handling

Starting in Minecraft 1.20.2 (Protocol 764), the server introduces a distinct `CONFIGURATION` protocol state (state ID `4`) between Login and Play.

Mineflex fully implements this lifecycle inside `ClientConnection`:

1. **State Transition**: Upon receiving `LoginSuccessPacket`, the client transitions to `CONFIGURATION` (if protocol >= 764) or immediately to `PLAY` (if protocol 763).
2. **Configuration Negotiation**:
   - `ClientInformationPacket`: Transmits client locale, view distance, skin flags, and hand settings.
   - `KnownPacksPacket`: Negotiates vanilla and server resource/datapack IDs.
   - `FeatureFlagsPacket`: Receives enabled game features (e.g. `minecraft:vanilla`, `minecraft:bundle`).
   - `RegistryDataPacket`: Streams dynamic registry tags and definitions.
   - `KeepAliveConfigurationClientboundPacket`: Automatically acknowledged via `KeepAliveConfigurationServerboundPacket`.
3. **Transition to Play**:
   - Server dispatches `FinishConfigurationClientboundPacket` (ID `0x02`).
   - Client connection transparently replies with `FinishConfigurationServerboundPacket` (ID `0x02`).
   - State shifts to `PLAY` and gameplay packet streaming commences.

---

## AES-128 CFB8 Decryption Stream Pipeline

Minecraft protocol encryption uses an AES-128 stream cipher in CFB8 mode.

```
Socket Byte Stream
        │
        ▼
[DecryptingStreamReader] (AES-128-CFB8 In-Place Decryption)
        │
        ▼
[PacketFramer] (VarInt Length Parsing & Frame Slicing)
        │
        ▼
[zlib Decompressor] (If threshold met)
        │
        ▼
[Packet Decoder] (ProtocolRegistry lookup -> Strongly typed Packet)
        │
        ▼
[Bot Dispatcher / Handlers]
```

By decoupling decryption at the stream reader layer, the entire packet framing, VarInt parsing, and packet decoding pipeline operates unmodified whether encryption is active or inactive.
