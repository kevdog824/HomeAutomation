import asyncio

import requests
from requests.auth import AuthBase
from requests import PreparedRequest

from mkhome.utils import async_utils


@async_utils.async_wraps(requests.get)
async def get(*args, **kwargs):
    return await asyncio.to_thread(requests.get, *args, **kwargs)


@async_utils.async_wraps(requests.post)
async def post(*args, **kwargs):
    return await asyncio.to_thread(requests.post, *args, **kwargs)


@async_utils.async_wraps(requests.put)
async def put(*args, **kwargs):
    return await asyncio.to_thread(requests.put, *args, **kwargs)


@async_utils.async_wraps(requests.patch)
async def patch(*args, **kwargs):
    return await asyncio.to_thread(requests.patch, *args, **kwargs)


@async_utils.async_wraps(requests.request)
async def request(*args, **kwargs):
    return await asyncio.to_thread(requests.request, *args, **kwargs)


__all__ = ["get", "post", "put", "request", "AuthBase", "PreparedRequest"]
