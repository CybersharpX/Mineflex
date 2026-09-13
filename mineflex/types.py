"""Fundamental geometry and coordinate types for Mineflex."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterator, Sequence, Union


class Vec3:
    """3D Vector representation for positions, velocities, and directional vectors."""

    __slots__ = ("_x", "_y", "_z")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    def clone(self) -> Vec3:
        return Vec3(self._x, self._y, self._z)

    def offset(self, dx: float, dy: float, dz: float) -> Vec3:
        return Vec3(self._x + dx, self._y + dy, self._z + dz)

    def __add__(self, other: Union[Vec3, Sequence[float], float, int]) -> Vec3:
        if isinstance(other, Vec3):
            return Vec3(self._x + other._x, self._y + other._y, self._z + other._z)
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vec3(self._x + other[0], self._y + other[1], self._z + other[2])
        if isinstance(other, (int, float)):
            return Vec3(self._x + other, self._y + other, self._z + other)
        return NotImplemented

    def __radd__(self, other: Union[Vec3, Sequence[float], float, int]) -> Vec3:
        return self.__add__(other)

    def __sub__(self, other: Union[Vec3, Sequence[float], float, int]) -> Vec3:
        if isinstance(other, Vec3):
            return Vec3(self._x - other._x, self._y - other._y, self._z - other._z)
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vec3(self._x - other[0], self._y - other[1], self._z - other[2])
        if isinstance(other, (int, float)):
            return Vec3(self._x - other, self._y - other, self._z - other)
        return NotImplemented

    def __mul__(self, factor: float) -> Vec3:
        return Vec3(self._x * factor, self._y * factor, self._z * factor)

    def __rmul__(self, factor: float) -> Vec3:
        return self.__mul__(factor)

    def __truediv__(self, divisor: float) -> Vec3:
        if divisor == 0:
            raise ZeroDivisionError("division by zero")
        return Vec3(self._x / divisor, self._y / divisor, self._z / divisor)

    def __neg__(self) -> Vec3:
        return Vec3(-self._x, -self._y, -self._z)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vec3):
            return (
                math.isclose(self._x, other._x, abs_tol=1e-9)
                and math.isclose(self._y, other._y, abs_tol=1e-9)
                and math.isclose(self._z, other._z, abs_tol=1e-9)
            )
        return False

    def __hash__(self) -> int:
        return hash((round(self._x, 4), round(self._y, 4), round(self._z, 4)))

    def __repr__(self) -> str:
        return f"Vec3(x={self._x:.4f}, y={self._y:.4f}, z={self._z:.4f})"

    def __iter__(self) -> Iterator[float]:
        yield self._x
        yield self._y
        yield self._z

    def distance_to(self, other: Vec3) -> float:
        return math.sqrt(self.distance_squared(other))

    def distance_squared(self, other: Vec3) -> float:
        dx = self._x - other._x
        dy = self._y - other._y
        dz = self._z - other._z
        return dx * dx + dy * dy + dz * dz

    def horizontal_distance_to(self, other: Vec3) -> float:
        dx = self._x - other._x
        dz = self._z - other._z
        return math.sqrt(dx * dx + dz * dz)

    def norm(self) -> float:
        return math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)

    length = norm

    def norm_squared(self) -> float:
        return self._x * self._x + self._y * self._y + self._z * self._z

    def normalize(self) -> Vec3:
        length = self.norm()
        if length == 0:
            return Vec3(0, 0, 0)
        return Vec3(self._x / length, self._y / length, self._z / length)

    def dot(self, other: Vec3) -> float:
        return self._x * other._x + self._y * other._y + self._z * other._z

    def cross(self, other: Vec3) -> Vec3:
        return Vec3(
            self._y * other._z - self._z * other._y,
            self._z * other._x - self._x * other._z,
            self._x * other._y - self._y * other._x,
        )

    def floored(self) -> Vec3:
        return Vec3(math.floor(self._x), math.floor(self._y), math.floor(self._z))

    def rounded(self, ndigits: int = 0) -> Vec3:
        return Vec3(round(self._x, ndigits), round(self._y, ndigits), round(self._z, ndigits))

    def abs(self) -> Vec3:
        return Vec3(abs(self._x), abs(self._y), abs(self._z))

    def to_tuple(self) -> tuple[float, float, float]:
        return (self._x, self._y, self._z)

    def to_position(self) -> Position:
        """Convert continuous 3D vector to integer grid block Position."""
        return Position.from_vec3(self)


@dataclass(frozen=True)
class Position:
    """Integer block coordinate representation."""

    x: int
    y: int
    z: int

    @classmethod
    def from_vec3(cls, vec: Vec3) -> Position:
        return cls(math.floor(vec.x), math.floor(vec.y), math.floor(vec.z))

    def to_vec3(self) -> Vec3:
        return Vec3(float(self.x), float(self.y), float(self.z))

    def offset(self, dx: int, dy: int, dz: int) -> Position:
        return Position(self.x + dx, self.y + dy, self.z + dz)

    def encode(self) -> int:
        """Encode to Minecraft 64-bit block position representation (1.14+)."""
        return ((self.x & 0x3FFFFFF) << 38) | ((self.z & 0x3FFFFFF) << 12) | (self.y & 0xFFF)

    @classmethod
    def decode(cls, val: int) -> Position:
        """Decode from Minecraft 64-bit block position representation (1.14+)."""
        x = val >> 38
        y = val & 0xFFF
        z = (val >> 12) & 0x3FFFFFF

        # Convert to signed values based on bit widths (x: 26 bits, y: 12 bits, z: 26 bits)
        if x >= 1 << 25:
            x -= 1 << 26
        if y >= 1 << 11:
            y -= 1 << 12
        if z >= 1 << 25:
            z -= 1 << 26
        return cls(x, y, z)


@dataclass(frozen=True)
class Angle:
    """Yaw and pitch representation."""

    yaw: float  # degrees
    pitch: float  # degrees

    @property
    def yaw_radians(self) -> float:
        return math.radians(self.yaw)

    @property
    def pitch_radians(self) -> float:
        return math.radians(self.pitch)

    @classmethod
    def from_radians(cls, yaw: float, pitch: float) -> Angle:
        return cls(math.degrees(yaw), math.degrees(pitch))

    def to_protocol_bytes(self) -> tuple[int, int]:
        """Convert yaw and pitch to byte values (0-255)."""
        byte_yaw = int((self.yaw % 360) * 256 / 360) & 0xFF
        byte_pitch = int((self.pitch % 360) * 256 / 360) & 0xFF
        return byte_yaw, byte_pitch

    @classmethod
    def from_protocol_bytes(cls, byte_yaw: int, byte_pitch: int) -> Angle:
        yaw = (byte_yaw * 360.0) / 256.0
        pitch = (byte_pitch * 360.0) / 256.0
        return cls(yaw, pitch)


class AABB:
    """Axis-Aligned Bounding Box for physics simulation and collision testing."""

    __slots__ = ("min_x", "min_y", "min_z", "max_x", "max_y", "max_z")

    def __init__(
        self,
        min_x: float,
        min_y: float,
        min_z: float,
        max_x: float,
        max_y: float,
        max_z: float,
    ) -> None:
        self.min_x = min(min_x, max_x)
        self.min_y = min(min_y, max_y)
        self.min_z = min(min_z, max_z)
        self.max_x = max(min_x, max_x)
        self.max_y = max(min_y, max_y)
        self.max_z = max(min_z, max_z)

    @classmethod
    def from_block(cls, pos: Position | Vec3) -> AABB:
        x = math.floor(pos.x)
        y = math.floor(pos.y)
        z = math.floor(pos.z)
        return cls(x, y, z, x + 1.0, y + 1.0, z + 1.0)

    @classmethod
    def from_entity(cls, pos: Vec3, width: float, height: float) -> AABB:
        hw = width / 2.0
        return cls(pos.x - hw, pos.y, pos.z - hw, pos.x + hw, pos.y + height, pos.z + hw)

    def offset(self, dx: float, dy: float, dz: float) -> AABB:
        return AABB(
            self.min_x + dx,
            self.min_y + dy,
            self.min_z + dz,
            self.max_x + dx,
            self.max_y + dy,
            self.max_z + dz,
        )

    def expand(self, dx: float, dy: float, dz: float) -> AABB:
        min_x = self.min_x + dx if dx < 0 else self.min_x
        max_x = self.max_x + dx if dx > 0 else self.max_x
        min_y = self.min_y + dy if dy < 0 else self.min_y
        max_y = self.max_y + dy if dy > 0 else self.max_y
        min_z = self.min_z + dz if dz < 0 else self.min_z
        max_z = self.max_z + dz if dz > 0 else self.max_z
        return AABB(min_x, min_y, min_z, max_x, max_y, max_z)

    def contract(self, dx: float, dy: float, dz: float) -> AABB:
        return AABB(
            self.min_x + dx,
            self.min_y + dy,
            self.min_z + dz,
            self.max_x - dx,
            self.max_y - dy,
            self.max_z - dz,
        )

    def intersects(self, other: AABB) -> bool:
        return (
            self.max_x > other.min_x
            and self.min_x < other.max_x
            and self.max_y > other.min_y
            and self.min_y < other.max_y
            and self.max_z > other.min_z
            and self.min_z < other.max_z
        )

    def contains(self, vec: Vec3) -> bool:
        return (
            self.min_x <= vec.x <= self.max_x
            and self.min_y <= vec.y <= self.max_y
            and self.min_z <= vec.z <= self.max_z
        )

    def calculate_x_offset(self, other: AABB, offset_x: float) -> float:
        if other.max_y <= self.min_y or other.min_y >= self.max_y:
            return offset_x
        if other.max_z <= self.min_z or other.min_z >= self.max_z:
            return offset_x
        if offset_x > 0.0 and other.max_x <= self.min_x:
            d = self.min_x - other.max_x
            if d < offset_x:
                offset_x = d
        elif offset_x < 0.0 and other.min_x >= self.max_x:
            d = self.max_x - other.min_x
            if d > offset_x:
                offset_x = d
        return offset_x

    def calculate_y_offset(self, other: AABB, offset_y: float) -> float:
        if other.max_x <= self.min_x or other.min_x >= self.max_x:
            return offset_y
        if other.max_z <= self.min_z or other.min_z >= self.max_z:
            return offset_y
        if offset_y > 0.0 and other.max_y <= self.min_y:
            d = self.min_y - other.max_y
            if d < offset_y:
                offset_y = d
        elif offset_y < 0.0 and other.min_y >= self.max_y:
            d = self.max_y - other.min_y
            if d > offset_y:
                offset_y = d
        return offset_y

    def calculate_z_offset(self, other: AABB, offset_z: float) -> float:
        if other.max_x <= self.min_x or other.min_x >= self.max_x:
            return offset_z
        if other.max_y <= self.min_y or other.min_y >= self.max_y:
            return offset_z
        if offset_z > 0.0 and other.max_z <= self.min_z:
            d = self.min_z - other.max_z
            if d < offset_z:
                offset_z = d
        elif offset_z < 0.0 and other.min_z >= self.max_z:
            d = self.max_z - other.min_z
            if d > offset_z:
                offset_z = d
        return offset_z

    @property
    def center(self) -> Vec3:
        return Vec3(
            (self.min_x + self.max_x) / 2.0,
            (self.min_y + self.max_y) / 2.0,
            (self.min_z + self.max_z) / 2.0,
        )

    def __repr__(self) -> str:
        return (
            f"AABB({self.min_x:.2f}, {self.min_y:.2f}, {self.min_z:.2f} -> "
            f"{self.max_x:.2f}, {self.max_y:.2f}, {self.max_z:.2f})"
        )
