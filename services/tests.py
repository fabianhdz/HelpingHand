

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Language, Location, Post, Profile, Rating, Role, Service, Skill


class CommunityWorkflowTests(TestCase):
    """Exercise the workflows exposed by the refreshed templates."""

    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user(
            username='neighbor', password='Community-pass-761!',
            first_name='Alex', last_name='Rivera', email='alex@example.com',
        )
        cls.provider = User.objects.create_user(
            username='helper', password='Community-pass-762!',
            first_name='Sam', last_name='Lee', email='sam@example.com',
        )
        cls.location = Location.objects.create(
            street_address='123 Oak Street', city='Chicago', state='Illinois',
            postal_code='60601', country='USA',
        )
        for user in (cls.member, cls.provider):
            profile = Profile.objects.create(user=user, phone=3125550123, location=cls.location)
            profile.skills.add(Skill.objects.get_or_create(name='Gardening')[0])
            profile.languages.add(Language.objects.get_or_create(name='English')[0])
        cls.role = Role.objects.create(name='Provider')
        cls.service = Service.objects.create(name='Garden care')
        cls.post = cls.make_post(cls.provider)
        cls.own_post = cls.make_post(cls.member)
        cls.taken_post = cls.make_post(cls.provider, is_active=False)
        cls.appointment = Appointment.objects.create(user=cls.member, post=cls.taken_post)

    @classmethod
    def make_post(cls, user, **kwargs):
        return Post.objects.create(
            user=user, role=cls.role, service=cls.service, location=cls.location,
            date=timezone.now(), expiration_date=timezone.now() + timedelta(days=30),
            price_range=25, description='A little help caring for your garden.', **kwargs,
        )

    def setUp(self):
        self.client.force_login(self.member)

    def test_member_pages_render_with_real_data(self):
        routes = (
            ('home', []), ('posts_feed', []), ('create_post', []), ('my_posts', []),
            ('my_appointments', []), ('profile', []), ('post_detail', [self.post.pk]),
            ('appointment_confirmation', [self.appointment.pk]),
            ('complete_appointment', [self.appointment.pk]),
        )
        for name, args in routes:
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<main id="main-content"')

    def test_login_and_logout(self):
        self.client.logout()
        self.assertContains(self.client.get(reverse('home')), 'name="username"')
        response = self.client.post(reverse('home'), {
            'username': 'neighbor', 'password': 'Community-pass-761!',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.member.pk)
        self.assertRedirects(self.client.get(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_filters_keep_own_and_taken_posts_out_of_feed(self):
        response = self.client.get(reverse('posts_feed'), {
            'role': self.role.pk, 'service': self.service.pk, 'city': 'chicago',
            'state': 'Illinois', 'postal_code': '60601', 'country': 'USA',
        })
        self.assertEqual(list(response.context['posts']), [self.post])
        response = self.client.get(reverse('posts_feed'), {'city': 'No matching city'})
        self.assertContains(response, 'No matches just yet.')
        self.assertEqual(list(response.context['posts']), [])

    def test_post_creation_keeps_all_form_fields(self):
        response = self.client.post(reverse('create_post'), {
            'role': 'Provider', 'service': 'Tutoring', 'description': 'Math lessons nearby.',
            'price_range': '30', 'expiration_date': '2027-12-31',
            'street_address': '456 Elm Street', 'city': 'Chicago', 'state': 'Illinois',
            'postal_code': '60602', 'country': 'USA',
        })
        self.assertRedirects(response, reverse('home'))
        post = Post.objects.get(service__name='Tutoring')
        self.assertEqual(post.user, self.member)
        self.assertEqual(post.price_range, 30)
        self.assertEqual(post.location.postal_code, '60602')

    def test_invalid_post_renders_errors_and_keeps_entered_values(self):
        response = self.client.post(reverse('create_post'), {
            'role': 'Provider', 'service': 'Garden care', 'description': 'Keep this text.',
            'price_range': 'invalid', 'expiration_date': 'invalid',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keep this text.')
        self.assertContains(response, 'aria-invalid="true"')
        self.assertIn('price_range', response.context['form'].errors)

    def test_booking_and_cancellation_restore_post_availability(self):
        response = self.client.get(reverse('make_appointment', args=[self.post.pk]))
        appointment = Appointment.objects.get(user=self.member, post=self.post)
        self.assertRedirects(response, reverse('appointment_confirmation', args=[appointment.pk]))
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_active)
        response = self.client.post(reverse('my_appointments'), {
            'action': f'cancel_{appointment.pk}',
        })
        self.assertRedirects(response, reverse('posts_feed'))
        appointment.refresh_from_db()
        self.post.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')
        self.assertTrue(self.post.is_active)

    def test_completion_and_rating(self):
        response = self.client.post(reverse('my_appointments'), {
            'action': f'complete_{self.appointment.pk}',
        })
        self.assertRedirects(response, reverse('complete_appointment', args=[self.appointment.pk]))
        response = self.client.post(reverse('complete_appointment', args=[self.appointment.pk]), {
            'score': '5',
        })
        self.assertRedirects(response, reverse('posts_feed'))
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'completed')
        self.assertEqual(Rating.objects.get(appointment=self.appointment).score, 5)


class SignupWorkflowTests(TestCase):
    def test_two_step_signup(self):
        response = self.client.get(reverse('signup_user'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('signup_user'), {
            'username': 'newneighbor', 'first_name': 'Jamie', 'last_name': 'Park',
            'email': 'jamie@example.com',
            'password1': 'New-community-pass-963!', 'password2': 'New-community-pass-963!',
        })
        self.assertRedirects(response, reverse('signup_profile'))
        response = self.client.post(reverse('signup_profile'), {
            'phone': '3125550100', 'languages': 'English, Spanish', 'skills': 'Gardening, Math',
            'street_address': '789 Maple Street', 'city': 'Chicago', 'state': 'Illinois',
            'postal_code': '60603', 'country': 'USA',
        })
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='newneighbor')
        self.assertEqual(user.profile.languages.count(), 2)
        self.assertEqual(user.profile.skills.count(), 2)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_errors_are_visible_and_preserve_values(self):
        response = self.client.post(reverse('signup_user'), {
            'username': 'newneighbor', 'email': 'jamie@example.com',
            'password1': 'Some-password-12!', 'password2': 'Different-password-34!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'newneighbor')
        self.assertContains(response, 'aria-invalid="true"')
        self.assertIn('password2', response.context['user_form'].errors)
