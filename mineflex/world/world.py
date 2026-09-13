"""World state, chunk column management, and block queries."""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Tuple, Union

from mineflex.data.provider import Registry
from mineflex.protocol.packets.play.world import ChunkDataPacket
from mineflex.types import AABB, Position, Vec3
from mineflex.world.block import Block
from mineflex.world.chunk import Chunk


class World:
    """Represents the Minecraft world composed of loaded chunk columns."""

    def __init__(self, registry: Optional[Registry] = None) -> None:
        self.registry = registry or Registry("1.20.1")
        self.chunks: Dict[Tuple[int, int], Chunk] = {}

    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional[Chunk]:
        return self.chunks.get((chunk_x, chunk_z))

    def get_or_create_chunk(self, chunk_x: int, chunk_z: int) -> Chunk:
        key = (chunk_x, chunk_z)
        if key not in self.chunks:
            self.chunks[key] = Chunk(chunk_x, chunk_z)
        return self.chunks[key]

    def load_chunk_packet(self, packet: ChunkDataPacket) -> Chunk:
        chunk = self.get_or_create_chunk(packet.chunk_x, packet.chunk_z)
        chunk.load_data(packet.data)
        for be in packet.block_entities:
            bx = (packet.chunk_x << 4) | (be["packed_xz"] >> 4)
            bz = (packet.chunk_z << 4) | (be["packed_xz"] & 0xF)
            chunk.block_entities[(bx, be["y"], bz)] = be
        return chunk

    def get_block_state(self, pos: Union[Vec3, Position]) -> int:
        x = math.floor(pos.x)
        y = math.floor(pos.y)
        z = math.floor(pos.z)
        chunk = self.get_chunk(x >> 4, z >> 4)
        if chunk is None:
            return 0
        return chunk.get_block_state(x, y, z)

    def set_block_state(self, pos: Union[Vec3, Position], state_id: int) -> None:
        x = math.floor(pos.x)
        y = math.floor(pos.y)
        z = math.floor(pos.z)
        chunk = self.get_or_create_chunk(x >> 4, z >> 4)
        chunk.set_block_state(x, y, z, state_id)

    def get_block(self, pos: Union[Vec3, Position]) -> Block:
        """Get a rich Block instance at the given position."""
        x = math.floor(pos.x)
        y = math.floor(pos.y)
        z = math.floor(pos.z)
        state_id = self.get_block_state(pos)
        block_def = self.registry.get_block_by_state_id(state_id)
        return Block(
            position=Vec3(float(x), float(y), float(z)),
            state_id=state_id,
            definition=block_def,
        )

    set_block = set_block_state

    def get_colliding_bounding_boxes(self, target_box: AABB) -> List[AABB]:
        """Find all block bounding boxes intersecting with the given AABB."""
        min_x = math.floor(target_box.min_x)
        max_x = math.ceil(target_box.max_x)
        min_y = max(Chunk.MIN_Y, math.floor(target_box.min_y))
        max_y = min(Chunk.MAX_Y, math.ceil(target_box.max_y))
        min_z = math.floor(target_box.min_z)
        max_z = math.ceil(target_box.max_z)

        colliding_boxes: List[AABB] = []
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                for z in range(min_z, max_z):
                    block = self.get_block(Vec3(x, y, z))
                    if block.solid and not block.is_air:
                        for shape in block.get_collision_shapes():
                            if shape.intersects(target_box):
                                colliding_boxes.append(shape)
        return colliding_boxes

    def find_blocks(
        self,
        matching: Union[str, int, Callable[[Block], bool]],
        point: Vec3,
        max_distance: int = 16,
        count: int = 100,
    ) -> List[Vec3]:
        """Find matching block positions within a radius around point."""
        results: List[Vec3] = []
        center_x = math.floor(point.x)
        center_y = math.floor(point.y)
        center_z = math.floor(point.z)

        matcher: Callable[[Block], bool]
        if callable(matching):
            matcher = matching
        elif isinstance(matching, str):
            def matcher(b: Block) -> bool:
                return b.name == matching
        elif isinstance(matching, int):
            def matcher(b: Block) -> bool:
                return b.id == matching or b.state_id == matching
        else:
            return results

        max_dist_sq = max_distance * max_distance

        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                for dz in range(-max_distance, max_distance + 1):
                    if dx * dx + dy * dy + dz * dz > max_dist_sq:
                        continue
                    b_pos = Vec3(center_x + dx, center_y + dy, center_z + dz)
                    block = self.get_block(b_pos)
                    if matcher(block):
                        results.append(b_pos)
                        if len(results) >= count:
                            return results
        return results

    def find_block(
        self,
        matching: Union[str, int, Callable[[Block], bool]],
        point: Vec3,
        max_distance: int = 16,
    ) -> Optional[Block]:
        """Find the single closest matching block within radius."""
        matches = self.find_blocks(matching, point, max_distance=max_distance, count=1000)
        if not matches:
            return None
        matches.sort(key=lambda p: p.distance_squared(point))
        return self.get_block(matches[0])
