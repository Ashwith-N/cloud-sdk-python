"""Unit tests for BaseODataClient — covers the abstract contract."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sap_cloud_sdk.core.dpi_ng.auth import AuthProvider
from sap_cloud_sdk.core.dpi_ng.config import BaseCapabilityConfig
from sap_cloud_sdk.core.dpi_ng.odata_client import BaseODataClient


def _make_config():
    auth = MagicMock(spec=AuthProvider)
    return BaseCapabilityConfig(base_url="https://example.com", auth=auth)


class _ConcreteClient(BaseODataClient):
    def _get_entity_factories(self):
        return {}


@patch("sap_cloud_sdk.core.dpi_ng.odata_client.requests.Session")
class TestBaseODataClientAbstract:
    def test_cannot_instantiate_base_directly(self, _):
        with pytest.raises(TypeError):
            BaseODataClient(_make_config())  # type: ignore[abstract]

    def test_concrete_subclass_instantiates(self, mock_session_cls):
        mock_session_cls.return_value = MagicMock()
        client = _ConcreteClient(_make_config())
        assert client._factories == {}
