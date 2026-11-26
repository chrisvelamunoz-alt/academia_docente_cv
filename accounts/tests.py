from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsAuthFlowTests(TestCase):
    """Pruebas del flujo de registro, inicio de sesión, panel protegido y cierre."""

    def setUp(self):
        self.registro_url = reverse("accounts:registro")
        self.login_url = reverse("accounts:login")
        self.panel_url = reverse("accounts:panel")
        self.logout_url = reverse("accounts:logout")
        self.username_ficticio = "docente_prueba"
        self.password_valida = "ClaveDocente2026!"

    def test_registro_valido(self):
        """Un registro válido crea el usuario con hash y redirige a iniciar sesión."""
        response = self.client.post(
            self.registro_url,
            {
                "username": self.username_ficticio,
                "password1": self.password_valida,
                "password2": self.password_valida,
            },
        )

        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)
        self.assertEqual(User.objects.count(), 1)
        usuario = User.objects.get(username=self.username_ficticio)
        self.assertTrue(usuario.check_password(self.password_valida))
        self.assertNotEqual(usuario.password, self.password_valida)

    def test_registro_contrasenas_distintas_sin_crear_cuenta(self):
        """Contraseñas distintas en registro muestran error y no crean usuario."""
        response = self.client.post(
            self.registro_url,
            {
                "username": self.username_ficticio,
                "password1": self.password_valida,
                "password2": "OtraClaveDistinta99!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "password2",
            "The two password fields didn’t match.",
        )

    def test_visita_anonima_al_panel(self):
        """Una visita sin sesión a /panel/ redirige a /iniciar-sesion/."""
        response = self.client.get(self.panel_url)

        self.assertRedirects(
            response,
            f"{self.login_url}?next={self.panel_url}",
            fetch_redirect_response=False,
        )

    def test_inicio_sesion_usuario_inexistente(self):
        """Un usuario inexistente no inicia sesión y permanece en el formulario."""
        response = self.client.post(
            self.login_url,
            {
                "username": "usuario_que_no_existe",
                "password": self.password_valida,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTrue(response.context["form"].errors)

    def test_inicio_sesion_contrasena_incorrecta(self):
        """Una contraseña incorrecta rechaza el acceso sin autenticar sesión."""
        User.objects.create_user(
            username=self.username_ficticio,
            password=self.password_valida,
        )

        response = self.client.post(
            self.login_url,
            {
                "username": self.username_ficticio,
                "password": "PasswordErronea123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTrue(response.context["form"].errors)

    def test_acceso_valido_al_panel(self):
        """Credenciales válidas autentican y muestran el usuario en /panel/."""
        User.objects.create_user(
            username=self.username_ficticio,
            password=self.password_valida,
        )

        response = self.client.post(
            self.login_url,
            {
                "username": self.username_ficticio,
                "password": self.password_valida,
            },
            follow=True,
        )

        self.assertRedirects(response, self.panel_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, self.username_ficticio)
        self.assertContains(response, "Cerrar sesión")

    def test_cierre_sesion_y_nueva_visita_al_panel(self):
        """Tras cerrar sesión por POST, visitar /panel/ vuelve a pedir login."""
        User.objects.create_user(
            username=self.username_ficticio,
            password=self.password_valida,
        )
        self.client.login(
            username=self.username_ficticio,
            password=self.password_valida,
        )

        panel_autenticado = self.client.get(self.panel_url)
        self.assertEqual(panel_autenticado.status_code, 200)

        logout_response = self.client.post(self.logout_url)
        self.assertRedirects(
            logout_response,
            self.login_url,
            fetch_redirect_response=False,
        )

        panel_despues = self.client.get(self.panel_url)
        self.assertRedirects(
            panel_despues,
            f"{self.login_url}?next={self.panel_url}",
            fetch_redirect_response=False,
        )
