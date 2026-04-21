"""
Integration tests for API route endpoints.
Tests the root route redirect and general routing behavior.
"""

import pytest


class TestRootRoute:
    """Tests for the root endpoint GET /"""
    
    def test_root_redirect_to_index(self, client):
        """Test that GET / returns a redirect response to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        # Should return a redirect status code (3xx)
        assert response.status_code in [301, 302, 303, 307, 308]
    
    def test_root_redirect_location_header(self, client):
        """Test that the redirect Location header points to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        # Check the Location header contains the correct path
        assert "location" in response.headers
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_follow_redirects(self, client):
        """Test that following redirects from / works (static file should exist or 404)"""
        response = client.get("/", follow_redirects=True)
        
        # The redirect should complete (either 200 if file exists, or 404 if not)
        # We're just verifying the redirect chain works without errors
        assert response.status_code in [200, 404]
