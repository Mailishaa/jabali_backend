from rejesha_green.repositories import forest_zone_repository
from rejesha_green.models.forest_zone import ForestBlocks, ResourceTypes


def create_forest_zone(db, zone):
    return forest_zone_repository.create_forest_zone(db, zone)


def get_all_forest_zones(db):
    return forest_zone_repository.get_all_forest_zones(db)


def get_forest_zone(db, zone_id):
    return forest_zone_repository.get_forest_zone(db, zone_id)


def update_forest_zone(db, zone_id, zone):
    return forest_zone_repository.update_forest_zone(
        db,
        zone_id,
        zone
    )


def delete_forest_zone(db, zone_id):
    return forest_zone_repository.delete_forest_zone(
        db,
        zone_id
    )


def get_resources_by_block(db, block_name):
    if block_name not in [block.value for block in ForestBlocks]:
        return None

    return forest_zone_repository.get_resources_by_block(
        db,
        block_name
    )


def get_available_resources_by_block(db, block_name):
    if block_name not in [block.value for block in ForestBlocks]:
        return None

    return forest_zone_repository.get_available_resources_by_block(
        db,
        block_name
    )


def update_resource_availability(
    db,
    block_name,
    resource_type,
    is_available,
    price
):
    if block_name not in [block.value for block in ForestBlocks]:
        return None

    if resource_type not in [resource.value for resource in ResourceTypes]:
        return None

    return forest_zone_repository.update_resource_availability(
        db,
        block_name,
        resource_type,
        is_available,
        price
    )