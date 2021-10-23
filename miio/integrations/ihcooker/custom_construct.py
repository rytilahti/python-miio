import construct as c


class ArrayDefault(c.Array):
    r"""
    Homogenous array of elements, similar to C# generic T[].

    Parses into a ListContainer (a list). Parsing and building processes an exact amount of elements. If given list has less than count elements, the array is padded with the default element. More elements raises RangeError. Size is defined as count multiplied by subcon size, but only if subcon is fixed size.

    Operator [] can be used to make Array instances (recommended syntax).

    :param count: integer or context lambda, strict amount of elements
    :param subcon: Construct instance, subcon to process individual elements
    :param default: default element to pad array with.
    :param discard: optional, bool, if set then parsing returns empty list

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises RangeError: specified count is not valid
    :raises RangeError: given object has different length than specified count

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        >>> d = ArrayDefault(5, Byte, 0) or Byte[5]
        >>> d.build(range(3))
        b'\x00\x01\x02\x00\x00'
        >>> d.parse(_)
        [0, 1, 2, 0, 0]
    """

    def __init__(self, count, subcon, default, discard=False):
        super(ArrayDefault, self).__init__(count, subcon, discard)
        self.default = default

    def _build(self, obj, stream, context, path):
        count = self.count
        if callable(count):
            count = count(context)
        if not 0 <= count:
            raise c.RangeError("invalid count %s" % (count,), path=path)
        if len(obj) > count:
            raise c.RangeError(
                "expected %d elements, found %d" % (count, len(obj)), path=path
            )
        retlist = c.ListContainer()

        for i, e in enumerate(obj):
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)
            retlist.append(buildret)
        for i in range(len(obj), count):
            context._index = i
            buildret = self.subcon._build(self.default, stream, context, path)
            retlist.append(buildret)
        return retlist


class RebuildStream(c.Rebuild):
    r"""
    Field where building does not require a value, because the value gets recomputed when needed. Comes handy when building a Struct from a dict with missing keys. Useful for length and count fields when :class:`~construct.core.Prefixed` and :class:`~construct.core.PrefixedArray` cannot be used.

    Parsing defers to subcon. Building is defered to subcon, but it builds from a value provided by the stream until now. Size is the same as subcon, unless it raises SizeofError.

    Difference between Rebuild and RebuildStream, is that RebuildStream provides the current datastream to func.

    :param subcon: Construct instance
    :param func: lambda that works with streamed bytes up to this point.

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.
    """

    def __init__(self, subcon, func):
        super(RebuildStream, self).__init__(subcon, func)

    def _build(self, obj, stream, context, path):
        fallback = c.stream_tell(stream, path)
        c.stream_seek(stream, 0, 0, path)
        data = stream.read(fallback)
        obj = self.func(data) if callable(self.func) else self.func
        ret = self.subcon._build(obj, stream, context, path)
        return ret
