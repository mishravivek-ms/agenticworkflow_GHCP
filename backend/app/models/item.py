"""
Pydantic models for the items resource.
"""
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., description="Name of the item", min_length=1)
    description: str | None = Field(None, description="Optional description")
    price: float = Field(..., description="Price of the item", gt=0)


class ItemCreate(ItemBase):
    """Schema used when creating a new item."""


class ItemUpdate(BaseModel):
    """Schema used when updating an existing item (all fields optional)."""
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    price: float | None = Field(None, gt=0)


class ItemResponse(ItemBase):
    """Schema returned to the client."""
    id: int

    model_config = {"from_attributes": True}
