"""Unit tests for Vec3, Position, Angle, and AABB types."""

import math

from mineflex.types import AABB, Angle, Position, Vec3


def test_vec3_arithmetic():
    v1 = Vec3(1, 2, 3)
    v2 = Vec3(4, 5, 6)

    # Addition
    v_add = v1 + v2
    assert v_add == Vec3(5, 7, 9)

    # Subtraction
    v_sub = v2 - v1
    assert v_sub == Vec3(3, 3, 3)

    # Scalar multiplication
    v_mul = v1 * 2.0
    assert v_mul == Vec3(2, 4, 6)

    # Division
    v_div = v2 / 2.0
    assert v_div == Vec3(2.0, 2.5, 3.0)

    # Negation
    assert -v1 == Vec3(-1, -2, -3)


def test_vec3_methods():
    v = Vec3(3, 4, 0)
    assert math.isclose(v.norm(), 5.0)
    assert math.isclose(v.distance_to(Vec3(0, 0, 0)), 5.0)

    norm = v.normalize()
    assert math.isclose(norm.norm(), 1.0)

    v_floor = Vec3(1.7, -2.3, 4.0).floored()
    assert v_floor == Vec3(1.0, -3.0, 4.0)

    v_offset = v.offset(1, 1, 1)
    assert v_offset == Vec3(4, 5, 1)

    v3 = Vec3(1, 0, 0)
    v4 = Vec3(0, 1, 0)
    assert v3.dot(v4) == 0.0
    assert v3.cross(v4) == Vec3(0, 0, 1)


def test_position_encoding_decoding():
    pos = Position(12345, 64, -67890)
    encoded = pos.encode()
    decoded = Position.decode(encoded)
    assert decoded.x == pos.x
    assert decoded.y == pos.y
    assert decoded.z == pos.z


def test_position_negative_coordinates():
    pos_edge = Position(-33554432, -2048, -33554432)  # Edge limits
    assert Position.decode(pos_edge.encode()).x == pos_edge.x
    # Standard negative coords
    pos2 = Position(-100, -64, -200)
    encoded2 = pos2.encode()
    decoded2 = Position.decode(encoded2)
    assert decoded2.x == -100
    assert decoded2.y == -64
    assert decoded2.z == -200


def test_angle_conversion():
    angle = Angle(180.0, 45.0)
    byte_yaw, byte_pitch = angle.to_protocol_bytes()
    decoded_angle = Angle.from_protocol_bytes(byte_yaw, byte_pitch)

    assert math.isclose(decoded_angle.yaw, 180.0, abs_tol=2.0)
    assert math.isclose(decoded_angle.pitch, 45.0, abs_tol=2.0)


def test_aabb_intersection():
    box1 = AABB(0, 0, 0, 2, 2, 2)
    box2 = AABB(1, 1, 1, 3, 3, 3)
    box3 = AABB(3, 3, 3, 4, 4, 4)

    assert box1.intersects(box2)
    assert not box1.intersects(box3)
    assert box1.contains(Vec3(1, 1, 1))
    assert not box1.contains(Vec3(2.5, 1, 1))


def test_aabb_offsets():
    player_box = AABB(0, 0, 0, 0.6, 1.8, 0.6)
    ground_box = AABB(-1, -1, -1, 2, 0, 2)

    # Falling down by 0.5 units
    offset_y = ground_box.calculate_y_offset(player_box, -0.5)
    assert offset_y == 0.0  # Blocked by ground at y=0
