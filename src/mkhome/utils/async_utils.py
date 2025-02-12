import asyncio
import threading
import typing as _t
from queue import Queue


type _Coro[T] = _t.Coroutine[_t.Any, _t.Any, T]


def async_wraps[**P, T](
    _: _t.Callable[P, T],
) -> _t.Callable[..., _t.Callable[P, _t.Coroutine[None, None, T]]]:
    def wrapper(func):
        return func

    return wrapper  # type: ignore


def run_sync[T](coroutine: _Coro[T]) -> T:
    def run(coroutine: _Coro, queue: Queue[tuple[T, Exception | None]]) -> None:
        try:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(coroutine)
        except BaseException as exc:
            queue.put_nowait((None, exc))  # type: ignore
        else:
            queue.put_nowait((result, None))

    queue: Queue[tuple[T, Exception | None]] = Queue(1)
    t = threading.Thread(target=run, args=(coroutine, queue))
    t.start()
    t.join()
    rv, err = queue.get_nowait()
    if err is not None:
        raise err
    return rv
