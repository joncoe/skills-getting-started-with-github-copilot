"""
Tests for static file serving and root redirect.
Uses the Arrange-Act-Assert (AAA) pattern.
"""
import pytest


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client, reset_activities):
        """
        Arrange: client is ready
        Act: GET / (with redirect following disabled)
        Assert: response is 307/308 redirect to /static/index.html
        """
        # Arrange
        # (client fixture is set up)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in (307, 308)  # Temporary redirect
        assert "/static/index.html" in response.headers.get("location", "")

    def test_root_redirect_follows_to_index_html(self, client, reset_activities):
        """
        Arrange: client is ready to follow redirects
        Act: GET / (with redirect following enabled)
        Assert: response is 200 and contains HTML content
        """
        # Arrange
        # (client fixture is set up with follow_redirects default)

        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "Mergington High School" in response.text or "activities" in response.text.lower()
