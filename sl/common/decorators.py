import inspect
import asyncio

from common import Logger

def __pass(method):
    Logger.log_info('pass')
    def wrapped(*args, **kwargs):
        Logger.log_info('pass wrap')
        Logger.log_info(inspect.getsource(method))
        return method(*args, **kwargs)

    return wrapped


def __could_be_async(parent_method):
    if inspect.iscoroutinefunction(parent_method):
        return asyncio.coroutine
    else:
        return __pass

def validate(*v_args, **v_kwargs):
    Logger.log_info('in')
    def validator(method):
        Logger.log_info('in validator')

        def wrapped(*args, **kwargs):
            Logger.log_info('in wrapped')
            bad_args = []
            args_start = 1 if hasattr(method, '__self__') else 0
            if len(v_args) > args_start:
                for idx in range(args_start,len(args)):
                    if idx < len(v_args) and v_args[idx] is not None:
                        if inspect.isfunction(v_args[idx]):
                            if not v_args[idx](args[idx]):
                                bad_args.append(idx)
                        elif not isinstance(args[idx], v_args[idx]):
                            bad_args.append(idx)

            bad_kwargs = []
            if len(v_kwargs) > 0:
                for key in kwargs.keys():
                    if key in v_kwargs and v_kwargs[key] is not None:
                        if inspect.isfunction(v_kwargs[key]):
                            if not v_kwargs[key](kwargs[key]):
                                bad_kwargs.append(key)
                        elif not isinstance(kwargs[key], v_kwargs[key]):
                            bad_kwargs.append(key)

            if len(bad_args) > 0 or len(bad_kwargs):
                raise Warning(*[str(bad_args)+' | '+str(bad_kwargs)]*2)

            method_result = None
            if inspect.iscoroutinefunction(method):
                method_result = yield from method(*args, **kwargs)
            else:
                method_result = method(*args, **kwargs)

            return method_result

        return wrapped

    return validator
