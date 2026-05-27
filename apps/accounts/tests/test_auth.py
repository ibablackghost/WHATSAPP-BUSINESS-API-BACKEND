import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAuth:
    def test_register(self, api_client):
        response = api_client.post(
            reverse("auth-register"),
            {
                "email": "new@whatbot.pro",
                "username": "newuser",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert response.status_code == 201

    def test_login(self, api_client, admin_user):
        response = api_client.post(
            reverse("auth-login"),
            {"email": "test@whatbot.pro", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "tokens" in response.data

    def test_me_authenticated(self, auth_client, admin_user):
        response = auth_client.get(reverse("auth-me"))
        assert response.status_code == 200
        assert response.data["email"] == admin_user.email
