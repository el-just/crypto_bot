def pass_if_empty(func):
    async def wrapped(self, *args, **kwargs):
        if args[0] is None:
            return None
        else:
            return await func(self, *args, **kwargs)

    return wrapped
