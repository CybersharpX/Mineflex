"""Collision detection and auto-stepping resolution for physics simulation."""

from __future__ import annotations

from typing import Tuple

from mineflex.types import AABB, Vec3
from mineflex.world.world import World


def resolve_collision(
    entity_box: AABB,
    vel: Vec3,
    world: World,
    step_height: float = 0.6,
    is_on_ground: bool = False,
) -> Tuple[Vec3, bool, bool]:
    """Resolve AABB movement against world block collisions with auto-stepping."""
    desired_dx = vel.x
    desired_dy = vel.y
    desired_dz = vel.z

    expanded_box = entity_box.expand(desired_dx, desired_dy, desired_dz)
    colliding_boxes = world.get_colliding_bounding_boxes(expanded_box)

    # 1. Normal resolution without stepping
    adj_dy = desired_dy
    for box in colliding_boxes:
        adj_dy = box.calculate_y_offset(entity_box, adj_dy)
    box_y = entity_box.offset(0, adj_dy, 0)

    adj_dx = desired_dx
    for box in colliding_boxes:
        adj_dx = box.calculate_x_offset(box_y, adj_dx)
    box_x = box_y.offset(adj_dx, 0, 0)

    adj_dz = desired_dz
    for box in colliding_boxes:
        adj_dz = box.calculate_z_offset(box_x, adj_dz)

    # 2. Check if auto-stepping over obstacle can be performed
    horizontal_collided = (desired_dx != adj_dx) or (desired_dz != adj_dz)
    can_step = (is_on_ground or (desired_dy != adj_dy and desired_dy < 0)) and horizontal_collided

    if can_step:
        # Simulate moving up by step_height
        lift_expanded = entity_box.expand(desired_dx, step_height, desired_dz)
        lift_boxes = world.get_colliding_bounding_boxes(lift_expanded)

        step_dy = step_height
        for box in lift_boxes:
            step_dy = box.calculate_y_offset(entity_box, step_dy)
        stepped_box_y = entity_box.offset(0, step_dy, 0)

        step_dx = desired_dx
        for box in lift_boxes:
            step_dx = box.calculate_x_offset(stepped_box_y, step_dx)
        stepped_box_x = stepped_box_y.offset(step_dx, 0, 0)

        step_dz = desired_dz
        for box in lift_boxes:
            step_dz = box.calculate_z_offset(stepped_box_x, step_dz)
        stepped_box_z = stepped_box_x.offset(0, 0, step_dz)

        # Move back down
        step_down_dy = -step_dy + adj_dy
        for box in lift_boxes:
            step_down_dy = box.calculate_y_offset(stepped_box_z, step_down_dy)

        # Compare horizontal distances traveled
        dist_normal_sq = adj_dx * adj_dx + adj_dz * adj_dz
        dist_step_sq = step_dx * step_dx + step_dz * step_dz

        if dist_step_sq > dist_normal_sq:
            adj_dx = step_dx
            adj_dy = step_dy + step_down_dy
            adj_dz = step_dz

    collided_y = desired_dy != adj_dy
    ground = collided_y and desired_dy < 0
    collided_horiz = (desired_dx != adj_dx) or (desired_dz != adj_dz)

    return Vec3(adj_dx, adj_dy, adj_dz), ground, collided_horiz
