"""Unit tests for BaseCapabilityConfig — shared fields and tenant_id validation."""

import pytest
from unittest.mock import MagicMock

from sap_cloud_sdk.core.dpi_ng.auth import AuthProvider, ClientCertificateAuth
from sap_cloud_sdk.core.dpi_ng.config import BaseCapabilityConfig


def valid_auth():
    return MagicMock(spec=AuthProvider)


class TestValidConstruction:
    def test_https_url_accepted(self):
        cfg = BaseCapabilityConfig(base_url="https://example.com", auth=valid_auth())
        assert cfg.base_url == "https://example.com"

    def test_http_url_accepted(self):
        cfg = BaseCapabilityConfig(base_url="http://example.com", auth=valid_auth())
        assert cfg.base_url == "http://example.com"

    def test_trailing_slash_stripped(self):
        cfg = BaseCapabilityConfig(base_url="https://example.com/", auth=valid_auth())
        assert cfg.base_url == "https://example.com"

    def test_multiple_trailing_slashes_stripped(self):
        cfg = BaseCapabilityConfig(base_url="https://example.com///", auth=valid_auth())
        assert cfg.base_url == "https://example.com"

    def test_auth_stored(self):
        auth = valid_auth()
        cfg = BaseCapabilityConfig(base_url="https://example.com", auth=auth)
        assert cfg.auth is auth


class TestDefaults:
    def test_timeout_default(self):
        cfg = BaseCapabilityConfig(base_url="https://example.com", auth=valid_auth())
        assert cfg.timeout == 30.0

    def test_verify_ssl_default(self):
        cfg = BaseCapabilityConfig(base_url="https://example.com", auth=valid_auth())
        assert cfg.verify_ssl is True

    def test_tenant_id_default_is_none(self):
        cfg = BaseCapabilityConfig(base_url="https://example.com", auth=valid_auth())
        assert cfg.tenant_id is None


class TestInvalidBaseUrl:
    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="base_url must be a valid HTTP"):
            BaseCapabilityConfig(base_url="", auth=valid_auth())

    def test_plain_string_raises(self):
        with pytest.raises(ValueError, match="base_url must be a valid HTTP"):
            BaseCapabilityConfig(base_url="not-a-url", auth=valid_auth())

    def test_ftp_scheme_raises(self):
        with pytest.raises(ValueError, match="base_url must be a valid HTTP"):
            BaseCapabilityConfig(base_url="ftp://example.com", auth=valid_auth())

    def test_missing_scheme_raises(self):
        with pytest.raises(ValueError, match="base_url must be a valid HTTP"):
            BaseCapabilityConfig(base_url="example.com", auth=valid_auth())


class TestInvalidAuth:
    def test_none_auth_raises(self):
        with pytest.raises(ValueError, match="auth must be an AuthProvider"):
            BaseCapabilityConfig(base_url="https://example.com", auth=None)  # ty: ignore[invalid-argument-type]

    def test_string_auth_raises(self):
        with pytest.raises(ValueError, match="auth must be an AuthProvider"):
            BaseCapabilityConfig(base_url="https://example.com", auth="Bearer token")  # ty: ignore[invalid-argument-type]


class TestTenantId:
    def test_cert_auth_without_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id is required"):
            BaseCapabilityConfig(
                base_url="https://example.com",
                auth=ClientCertificateAuth(cert_file="cert.pem", key_file="key.pem"),
            )

    def test_non_cert_auth_with_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id must not be set"):
            BaseCapabilityConfig(
                base_url="https://example.com",
                auth=valid_auth(),
                tenant_id="tenant-123",
            )

    def test_cert_auth_with_tenant_id_stored(self):
        cfg = BaseCapabilityConfig(
            base_url="https://example.com",
            auth=ClientCertificateAuth(cert_file="cert.pem", key_file="key.pem"),
            tenant_id="tenant-abc",
        )
        assert cfg.tenant_id == "tenant-abc"
