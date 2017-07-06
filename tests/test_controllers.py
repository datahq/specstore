import jwt
import pytest
from datapackage_pipelines_sourcespec_registry.registry import SourceSpecRegistry
from werkzeug.exceptions import NotFound

from specstore.controllers import status, upload

private_key = open('tests/private.pem').read()
public_key = open('tests/public.pem').read()
spec = {'meta': {'id': 'id', 'owner': 'me'}}
spec2 = {'meta': {'id': 'id2', 'owner': 'me2'}}
spec_unauth = {'meta': {'id': 'id', 'owner': 'me2'}}
bad_spec = {'meta': {'id': 'id', 'owner': 'me', 'version': 'one'}}

def generate_token(owner):
    ret = {
        'userid': owner,
        'permissions': {},
        'service': ''
    }
    token = jwt.encode(ret, private_key, algorithm='RS256').decode('ascii')
    return token


@pytest.fixture
def empty_registry():
    r = SourceSpecRegistry('sqlite://')
    return r


@pytest.fixture
def full_registry():
    r = SourceSpecRegistry('sqlite://')
    r.put_source_spec('me', 'assembler', spec, uuid='id')
    return r

# STATUS

def test_status_not_found(empty_registry):
    with pytest.raises(NotFound):
        status('id', empty_registry)


def test_status_found(full_registry):
    ret = status('id', full_registry)
    assert ret == {
        "state": "loaded"
    }


# UPLOAD

def test_upload_no_contents(empty_registry):
    token = generate_token('me')
    ret = upload(token, None, empty_registry, public_key)
    assert not ret['success']
    assert ret['id'] is None
    assert ret['errors'] == ['Received empty contents (make sure your content-type is correct)']


def test_upload_bad_contents(empty_registry):
    token = generate_token('me')
    ret = upload(token, {}, empty_registry, public_key)
    assert not ret['success']
    assert ret['id'] is None
    assert ret['errors'] == ['Missing owner in spec']


def test_upload_no_token(empty_registry):
    ret = upload(None, spec, empty_registry, public_key)
    assert not ret['success']
    assert ret['id'] is None
    assert ret['errors'] == ['No token or token not authorised for owner']


def test_upload_bad_token(empty_registry):
    token = generate_token('mee')
    ret = upload(token, spec, empty_registry, public_key)
    assert not ret['success']
    assert ret['id'] is None
    assert ret['errors'] == ['No token or token not authorised for owner']


def test_upload_invalid_contents(empty_registry):
    token = generate_token('me')
    ret = upload(token, bad_spec, empty_registry, public_key)
    assert not ret['success']
    assert ret['id'] is None
    assert ret['errors'] == ['Validation failed for contents']


def test_upload_new(empty_registry: SourceSpecRegistry):
    token = generate_token('me')
    ret = upload(token, spec, empty_registry, public_key)
    assert ret['success']
    assert ret['id'] == 'id'
    assert ret['errors'] == []
    specs = list(empty_registry.list_source_specs())
    assert len(specs) == 1
    first = specs[0]
    assert first.owner == 'me'
    assert first.uuid == 'id'
    assert first.contents == spec


def test_upload_existing(full_registry):
    token = generate_token('me')
    ret = upload(token, spec, full_registry, public_key)
    assert ret['success']
    assert ret['id'] == 'id'
    assert ret['errors'] == []
    specs = list(full_registry.list_source_specs())
    assert len(specs) == 1
    first = specs[0]
    assert first.owner == 'me'
    assert first.uuid == 'id'
    assert first.contents == spec


def test_upload_append(full_registry):
    token = generate_token('me2')
    ret = upload(token, spec2, full_registry, public_key)
    assert ret['success']
    assert ret['id'] == 'id2'
    assert ret['errors'] == []
    specs = list(full_registry.list_source_specs())
    assert len(specs) == 2
    first = specs[0]
    assert first.owner == 'me'
    assert first.uuid == 'id'
    assert first.contents == spec
    second = specs[1]
    assert second.owner == 'me2'
    assert second.uuid == 'id2'
    assert second.contents == spec2


def test_unauthorized_replace(full_registry):
    token = generate_token('me2')
    ret = upload(token, spec_unauth, full_registry, public_key)
    assert not ret['success']
    assert ret['id'] is None
    assert ret['errors'] == ['Unauthorized to update spec']
    specs = list(full_registry.list_source_specs())
    assert len(specs) == 1
    first = specs[0]
    assert first.owner == 'me'
    assert first.uuid == 'id'
    assert first.contents == spec
