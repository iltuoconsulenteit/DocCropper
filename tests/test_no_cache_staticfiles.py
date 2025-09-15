import asyncio
from pathlib import Path

# Extract NoCacheStaticFiles class source without importing heavy dependencies
source = Path('services/api/app.py').read_text().splitlines()
start = source.index('class NoCacheStaticFiles(StaticFiles):')
end = start + 1
for line in source[start + 1:]:
    if line and not line.startswith(' '):
        break
    end += 1
class_src = "\n".join(source[start:end])


class DummyHeaders(dict):
    def __delitem__(self, key):
        super().__delitem__(key)


class DummyResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = DummyHeaders({'X-Frame-Options': 'DENY'})


class StaticFiles:
    def __init__(self, *args, **kwargs):
        pass

    async def get_response(self, path, scope):
        return DummyResponse()


ns = {'StaticFiles': StaticFiles}
exec(class_src, ns)
NoCacheStaticFiles = ns['NoCacheStaticFiles']


def test_no_cache_staticfiles_headers():
    app = NoCacheStaticFiles(directory='.', html=True)

    async def run():
        return await app.get_response('index.html', {})

    resp = asyncio.run(run())
    assert resp.status_code == 200
    assert resp.headers['Cache-Control'] == 'no-store, max-age=0'
    assert 'X-Frame-Options' not in resp.headers
