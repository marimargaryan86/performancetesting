import builtins

Primitive = builtins.bool | builtins.int | builtins.float | builtins.str
NestedPrimitive = Primitive | list["NestedPrimitive"] | dict[str, "NestedPrimitive"]
PrimitiveMapping = dict[str, NestedPrimitive]
PrimitiveSequence = list[NestedPrimitive]
