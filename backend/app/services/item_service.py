"""
In-memory service layer for items.
Replace the in-memory store with a real database in production.
"""
from app.models.item import ItemCreate, ItemResponse, ItemUpdate


# Simple in-memory store keyed by item ID
_store: dict[int, dict] = {}
_next_id: int = 1


def list_items() -> list[ItemResponse]:
    """Return all items."""
    return [ItemResponse(id=item_id, **data) for item_id, data in _store.items()]


def get_item(item_id: int) -> ItemResponse | None:
    """Return a single item by ID, or None if not found."""
    data = _store.get(item_id)
    if data is None:
        return None
    return ItemResponse(id=item_id, **data)


def create_item(payload: ItemCreate) -> ItemResponse:
    """Persist a new item and return the created resource."""
    global _next_id
    item_id = _next_id
    _store[item_id] = payload.model_dump()
    _next_id += 1
    return ItemResponse(id=item_id, **_store[item_id])


def update_item(item_id: int, payload: ItemUpdate) -> ItemResponse | None:
    """Apply a partial update to an existing item."""
    if item_id not in _store:
        return None
    updates = payload.model_dump(exclude_unset=True)
    _store[item_id].update(updates)
    return ItemResponse(id=item_id, **_store[item_id])


def delete_item(item_id: int) -> bool:
    """Remove an item; return True if it existed."""
    return _store.pop(item_id, None) is not None
