from fastapi import APIRouter, HTTPException
from models import OsariMapping
from services.osari_service import (
    create_mapping,
    get_mappings,
    update_mapping
)

router = APIRouter(prefix="/osari")


@router.post("/")
def add_mapping(mapping: OsariMapping):
    return create_mapping(mapping.dict())


@router.get("/")
def fetch_mappings():
    return get_mappings()


@router.put("/{mapping_id}")
def edit_mapping(mapping_id: str, mapping: OsariMapping):
    updated = update_mapping(mapping_id, mapping.dict())

    if not updated:
        raise HTTPException(status_code=404, detail="Mapping not found")

    return updated