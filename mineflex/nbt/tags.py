"""Named Binary Tag (NBT) data structures for Minecraft."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, ClassVar, Iterator, Mapping, MutableMapping, Sequence, Union


class TagType(IntEnum):
    """NBT tag type identifiers."""

    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10
    INT_ARRAY = 11
    LONG_ARRAY = 12


class NBTTag:
    """Base class for all NBT tags."""

    tag_type: ClassVar[TagType] = TagType.END

    @property
    def value(self) -> Any:
        raise NotImplementedError


@dataclass
class TagByte(NBTTag):
    val: int = 0
    tag_type: ClassVar[TagType] = TagType.BYTE

    @property
    def value(self) -> int:
        return self.val


@dataclass
class TagShort(NBTTag):
    val: int = 0
    tag_type: ClassVar[TagType] = TagType.SHORT

    @property
    def value(self) -> int:
        return self.val


@dataclass
class TagInt(NBTTag):
    val: int = 0
    tag_type: ClassVar[TagType] = TagType.INT

    @property
    def value(self) -> int:
        return self.val


@dataclass
class TagLong(NBTTag):
    val: int = 0
    tag_type: ClassVar[TagType] = TagType.LONG

    @property
    def value(self) -> int:
        return self.val


@dataclass
class TagFloat(NBTTag):
    val: float = 0.0
    tag_type: ClassVar[TagType] = TagType.FLOAT

    @property
    def value(self) -> float:
        return self.val


@dataclass
class TagDouble(NBTTag):
    val: float = 0.0
    tag_type: ClassVar[TagType] = TagType.DOUBLE

    @property
    def value(self) -> float:
        return self.val


@dataclass
class TagByteArray(NBTTag):
    val: bytes = b""
    tag_type: ClassVar[TagType] = TagType.BYTE_ARRAY

    @property
    def value(self) -> bytes:
        return self.val


@dataclass
class TagString(NBTTag):
    val: str = ""
    tag_type: ClassVar[TagType] = TagType.STRING

    @property
    def value(self) -> str:
        return self.val


class TagList(NBTTag, Sequence[Any]):
    tag_type: ClassVar[TagType] = TagType.LIST

    def __init__(
        self, item_type: TagType = TagType.END, items: Sequence[Any] | None = None
    ) -> None:
        self.item_type = item_type
        self._items: list[Any] = list(items or [])

    @property
    def value(self) -> list[Any]:
        return [item.value if isinstance(item, NBTTag) else item for item in self._items]

    def append(self, item: Any) -> None:
        self._items.append(item)

    def __getitem__(self, index: Union[int, slice]) -> Any:
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"TagList(type={self.item_type.name}, count={len(self._items)})"


class TagCompound(NBTTag, MutableMapping[str, Any]):
    tag_type: ClassVar[TagType] = TagType.COMPOUND

    def __init__(self, mapping: Mapping[str, Any] | None = None) -> None:
        self._tags: dict[str, Any] = dict(mapping or {})

    @property
    def value(self) -> dict[str, Any]:
        return {k: v.value if isinstance(v, NBTTag) else v for k, v in self._tags.items()}

    def __getitem__(self, key: str) -> Any:
        return self._tags[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._tags[key] = value

    def __delitem__(self, key: str) -> None:
        del self._tags[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._tags)

    def __len__(self) -> int:
        return len(self._tags)

    def __contains__(self, key: object) -> bool:
        return key in self._tags

    def __repr__(self) -> str:
        return f"TagCompound({self._tags})"


@dataclass
class TagIntArray(NBTTag):
    val: list[int] | tuple[int, ...] = ()
    tag_type: ClassVar[TagType] = TagType.INT_ARRAY

    @property
    def value(self) -> list[int]:
        return list(self.val)


@dataclass
class TagLongArray(NBTTag):
    val: list[int] | tuple[int, ...] = ()
    tag_type: ClassVar[TagType] = TagType.LONG_ARRAY

    @property
    def value(self) -> list[int]:
        return list(self.val)
