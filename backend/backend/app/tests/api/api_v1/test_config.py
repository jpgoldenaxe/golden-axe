from app.core.config import settings
from app.crud.config import CRUDConfig


def test_create_config_success(test_app, monkeypatch):
    test_request_data = {
        "name": "golden-axe.vcenter.example.com",
        "host": "192.168.10.100",
        "user": "administrator@vsphere.local",
        "password": "VMware123!",
    }
    expected_response_data = {
        "_id": "666f6f2d6261722d71757578",
        "name": "golden-axe.vcenter.example.com",
        "host": "192.168.10.100",
        "user": "administrator@vsphere.local",
        "password": "VMware123!",
    }
    expected_response_code = 200

    async def insert_config_dummy(self, db, config):
        return expected_response_data

    monkeypatch.setattr(CRUDConfig, "insert_config", insert_config_dummy)

    response = test_app.post(
        f"{settings.API_V1_PREFIX}/configs/", json=test_request_data
    )
    assert response.status_code == expected_response_code
    content = response.json()
    assert content["name"] == expected_response_data["name"]
    assert content["host"] == expected_response_data["host"]
    assert content["user"] == expected_response_data["user"]
    assert content["password"] == expected_response_data["password"]


def test_create_config_faild(test_app, monkeypatch):
    test_request_data = {  # missing name's entry
        "host": "192.168.10.100",
        "user": "administrator@vsphere.local",
        "password": "VMware123!",
    }
    test_response_data = {}
    expected_response_code = 422

    async def insert_config_dummy(self, db, config):
        return test_response_data

    monkeypatch.setattr(CRUDConfig, "insert_config", insert_config_dummy)

    response = test_app.post(
        f"{settings.API_V1_PREFIX}/configs/", json=test_request_data
    )
    assert response.status_code == expected_response_code


def test_replace_config_success(test_app, monkeypatch):
    test_request_id = "666f6f2d6261722d71757578"
    test_request_data = {
        "name": "golden-axe.vcenter.example.com",
        "host": "192.168.10.100",
        "user": "administrator@vsphere.local",
        "password": "VMware123!",
    }
    expected_response_code = 204

    async def replace_config_dummy(self, db, id, config):
        return 1

    monkeypatch.setattr(CRUDConfig, "replace_config", replace_config_dummy)

    response = test_app.put(
        f"{settings.API_V1_PREFIX}/configs/{test_request_id}", json=test_request_data
    )
    assert response.status_code == expected_response_code


def test_replace_config_fail(test_app, monkeypatch):
    test_request_id = "666f6f2d6261722d71757578"
    test_request_data = {
        "name": "golden-axe.vcenter.example.com",
        "host": "192.168.10.100",
        "user": "administrator@vsphere.local",
        "password": "VMware123!",
    }
    expected_response_code = 404

    async def replace_config_dummy(self, db, id, config):
        return 0

    monkeypatch.setattr(CRUDConfig, "replace_config", replace_config_dummy)

    response = test_app.put(
        f"{settings.API_V1_PREFIX}/configs/{test_request_id}", json=test_request_data
    )
    assert response.status_code == expected_response_code


def test_get_configs_success(test_app, monkeypatch):
    test_response_data = [
        {
            "id": "666f6f2d6261722d71757578",
            "name": "golden-axe.vcenter.example.com",
            "host": "192.168.10.100",
            "user": "administrator@vsphere.local",
            "password": "VMware123!",
        },
        {
            "id": "666f6f2d6261722d71757578",
            "name": "golden-axe.nsx-t.example.com",
            "host": "192.168.10.101",
            "user": "admin",
            "password": "VMware123!VMware123!",
        },
    ]
    expected_response_code = 200

    async def list_configs_dummy(self, db, limit):
        return test_response_data

    monkeypatch.setattr(CRUDConfig, "list_configs", list_configs_dummy)

    response = test_app.get(f"{settings.API_V1_PREFIX}/configs/")
    assert response.status_code == expected_response_code


def test_get_configs_with_id_success(test_app, monkeypatch):
    test_request_id = "666f6f2d6261722d71757578"
    test_response_data = {
        "id": "666f6f2d6261722d71757578",
        "name": "golden-axe.vcenter.example.com",
        "host": "192.168.10.100",
        "user": "administrator@vsphere.local",
        "password": "VMware123!",
    }
    expected_response_code = 200

    async def get_config_dummy(self, db, id):
        return test_response_data

    monkeypatch.setattr(CRUDConfig, "get_config", get_config_dummy)

    response = test_app.get(f"{settings.API_V1_PREFIX}/configs/{test_request_id}")
    assert response.status_code == expected_response_code


def test_get_configs_with_id_fail(test_app, monkeypatch):
    test_request_id = "666f6f2d6261722d71757578"
    test_response_data = None
    expected_response_code = 404

    async def get_config_dummy(self, db, id):
        return test_response_data

    monkeypatch.setattr(CRUDConfig, "get_config", get_config_dummy)

    response = test_app.get(f"{settings.API_V1_PREFIX}/configs/{test_request_id}")
    assert response.status_code == expected_response_code


def test_delete_config_success(test_app, monkeypatch):
    test_request_id = "666f6f2d6261722d71757578"
    expected_response_code = 204

    async def delete_config_dummy(self, db, id):
        return 1

    monkeypatch.setattr(CRUDConfig, "delete_config", delete_config_dummy)

    response = test_app.delete(f"{settings.API_V1_PREFIX}/configs/{test_request_id}")
    assert response.status_code == expected_response_code


def test_delete_config_fail(test_app, monkeypatch):
    test_request_id = "666f6f2d6261722d71757578"
    expected_response_code = 404

    async def delete_config_dummy(self, db, id):
        return 0

    monkeypatch.setattr(CRUDConfig, "delete_config", delete_config_dummy)

    response = test_app.delete(f"{settings.API_V1_PREFIX}/configs/{test_request_id}")
    assert response.status_code == expected_response_code
