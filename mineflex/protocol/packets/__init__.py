"""Packet registrations for Mineflex."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mineflex.protocol.registry import ProtocolRegistry


def register_standard_packets(registry: ProtocolRegistry) -> None:
    """Register all standard packets for protocol 763 (1.20.1) into the registry."""
    # Handshake
    from mineflex.protocol.packets.handshake import HandshakePacket

    registry.register(HandshakePacket)

    # Status
    from mineflex.protocol.packets.status import (
        PingPacket,
        PongPacket,
        StatusRequestPacket,
        StatusResponsePacket,
    )

    registry.register(StatusRequestPacket)
    registry.register(StatusResponsePacket)
    registry.register(PingPacket)
    registry.register(PongPacket)

    # Login
    from mineflex.protocol.packets.login import (
        DisconnectLoginPacket,
        EncryptionRequestPacket,
        EncryptionResponsePacket,
        LoginAcknowledgedPacket,
        LoginStartPacket,
        LoginSuccessPacket,
        SetCompressionPacket,
    )

    registry.register(LoginStartPacket)
    registry.register(DisconnectLoginPacket)
    registry.register(EncryptionRequestPacket)
    registry.register(EncryptionResponsePacket)
    registry.register(LoginSuccessPacket)
    registry.register(SetCompressionPacket)
    registry.register(LoginAcknowledgedPacket)

    # Play
    from mineflex.protocol.packets.play import (
        BlockUpdatePacket,
        ChatMessagePacket,
        ChunkDataPacket,
        ClickContainerPacket,
        ClientInformationPacket,
        CloseContainerClientboundPacket,
        CloseContainerServerboundPacket,
        ConfirmTeleportPacket,
        DestroyEntitiesPacket,
        DisconnectPlayPacket,
        InteractPacket,
        KeepAliveClientboundPacket,
        KeepAliveServerboundPacket,
        LoginPlayPacket,
        OpenScreenPacket,
        PlayerActionPacket,
        SetContainerContentPacket,
        SetContainerSlotPacket,
        SetEntityVelocityPacket,
        SetExperiencePacket,
        SetHealthPacket,
        SetHeldItemPacket,
        SetPlayerOnGroundPacket,
        SetPlayerPositionAndRotationPacket,
        SetPlayerPositionPacket,
        SetPlayerRotationPacket,
        SpawnEntityPacket,
        SwingArmPacket,
        SynchronizePositionPacket,
        SystemChatPacket,
        UpdateEntityPositionPacket,
        UpdateEntityPositionRotationPacket,
        UpdateEntityRotationPacket,
        UpdateTimePacket,
        UseItemOnPacket,
        UseItemPacket,
    )

    registry.register(KeepAliveClientboundPacket)
    registry.register(KeepAliveServerboundPacket)
    registry.register(LoginPlayPacket)
    registry.register(SynchronizePositionPacket)
    registry.register(ConfirmTeleportPacket)
    registry.register(ClientInformationPacket)
    registry.register(SetPlayerPositionPacket)
    registry.register(SetPlayerPositionAndRotationPacket)
    registry.register(SetPlayerRotationPacket)
    registry.register(SetPlayerOnGroundPacket)
    registry.register(PlayerActionPacket)
    registry.register(SwingArmPacket)
    registry.register(UseItemOnPacket)
    registry.register(UseItemPacket)
    registry.register(SetHealthPacket)
    registry.register(SetExperiencePacket)
    registry.register(UpdateTimePacket)
    registry.register(SystemChatPacket)
    registry.register(DisconnectPlayPacket)
    registry.register(ChatMessagePacket)
    registry.register(ChunkDataPacket)
    registry.register(BlockUpdatePacket)
    registry.register(SpawnEntityPacket)
    registry.register(UpdateEntityPositionPacket)
    registry.register(UpdateEntityPositionRotationPacket)
    registry.register(UpdateEntityRotationPacket)
    registry.register(DestroyEntitiesPacket)
    registry.register(SetEntityVelocityPacket)
    registry.register(InteractPacket)
    registry.register(SetContainerContentPacket)
    registry.register(SetContainerSlotPacket)
    registry.register(OpenScreenPacket)
    registry.register(CloseContainerClientboundPacket)
    registry.register(ClickContainerPacket)
    registry.register(CloseContainerServerboundPacket)
    registry.register(SetHeldItemPacket)

    # Configuration (1.20.2+)
    from mineflex.protocol.packets.configuration import (
        DisconnectConfigurationPacket,
        FeatureFlagsPacket,
        FinishConfigurationClientboundPacket,
        FinishConfigurationServerboundPacket,
        KeepAliveConfigurationClientboundPacket,
        KeepAliveConfigurationServerboundPacket,
        KnownPacksPacket,
        RegistryDataPacket,
    )

    registry.register(FinishConfigurationClientboundPacket)
    registry.register(FinishConfigurationServerboundPacket)
    registry.register(RegistryDataPacket)
    registry.register(FeatureFlagsPacket)
    registry.register(KnownPacksPacket)
    registry.register(KeepAliveConfigurationClientboundPacket)
    registry.register(KeepAliveConfigurationServerboundPacket)
    registry.register(DisconnectConfigurationPacket)
