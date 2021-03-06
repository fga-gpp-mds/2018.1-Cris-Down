from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from test_plus.test import TestCase
from django.contrib.messages import get_messages
from django.test.client import Client
from ..models.model_curves import Curves
from ..views.view_curves import CurveDataParser
from drdown.users.models.model_patient import Patient
from drdown.users.models.model_health_team import HealthTeam
from django.urls import reverse
from django.db import transaction
from django.utils.translation import ugettext_lazy as _


class TestModelRequest(TestCase):

    WEIGHT = 10
    HEIGHT = 123
    CEPHALIC_PERIMETER = 30
    AGE = 1

    def setUp(self):
        """
        This method will run before any test case.
        """

        self.client = Client()

        self.user = self.make_user()

        self.patient = Patient.objects.create(
            ses="1234567",
            user=self.user,
            mother_name="Mãe",
            father_name="Pai",
            ethnicity=3,
            sus_number="12345678911",
            civil_registry_of_birth="12345678911",
        )

        self.user2 = self.make_user(username='user2')

        self.health_team = HealthTeam.objects.create(
            cpf="057.641.271-65",
            user=self.user2,
            speciality=HealthTeam.NEUROLOGY,
            council_acronym=HealthTeam.CRM,
            register_number="1234567",
            registration_state=HealthTeam.DF,
        )

        self.curve = Curves.objects.create(
            patient=self.patient,
            weight=self.WEIGHT,
            height=self.HEIGHT,
            cephalic_perimeter=self.CEPHALIC_PERIMETER,
            age=self.AGE,
        )

        Curves.objects.create(
            patient=self.patient,
            weight=self.WEIGHT,
            height=self.HEIGHT,
            cephalic_perimeter=self.CEPHALIC_PERIMETER,
            age=45,
        )

    def test_curves_form_valid_create_view(self):
        """
        Test if create form is valid with all required fields
        """
        self.client.force_login(user=self.health_team.user)

        data = {
            'height': self.HEIGHT,
            'weight': self.WEIGHT,
            'age': 12,
            'cephalic_perimeter': self.CEPHALIC_PERIMETER,
        }

        response = self.client.post(
            path=reverse(
                'medicalrecords:create_curve',
                kwargs={'username': self.patient.user.username}
            ),
            data=data,
            follow=True
        )

        self.assertEquals(response.status_code, 200)

    def test_data_parse_curves_height(self):

        self.client.force_login(user=self.user2)
        self.client.request()

        response = self.client.get(
            path=reverse(
                viewname='medicalrecords:curve_ajax',

            ),
            follow=True,
            data={'username': self.patient.user.username, 'data_type': 'height','time_frame': 'months' }
        )

        self.assertEquals(response.status_code, 200)

        response = self.client.get(
            path=reverse(
                viewname='medicalrecords:curve_ajax',

            ),
            follow=True,
            data={'username': self.patient.user.username, 'data_type': 'height','time_frame': 'years' }
        )

        self.assertEquals(response.status_code, 200)

    def test_data_parse_curves_weight(self):

        self.client.force_login(user=self.user2)
        self.client.request()

        response = self.client.get(
            path=reverse(
                viewname='medicalrecords:curve_ajax',
            ),
            follow=True,
            data={'username': self.patient.user.username, 'data_type': 'weight','time_frame': 'months' }
        )

        self.assertEquals(response.status_code, 200)

        response = self.client.get(
            path=reverse(
                viewname='medicalrecords:curve_ajax',
            ),
            follow=True,
            data={'username': self.patient.user.username, 'data_type': 'weight','time_frame': 'years' }
        )

        self.assertEquals(response.status_code, 200)

    def test_data_parse_curves_bmi(self):

        self.client.force_login(user=self.user2)
        self.client.request()

        self.patient.user.gender = 'Female'
        self.patient.user.save()

        response = self.client.get(
            path=reverse(
                viewname='medicalrecords:curve_ajax',
            ),
            follow=True,
            data={'username': self.patient.user.username, 'data_type': 'bmi', 'time_frame': 'years' }
        )

        self.assertEquals(response.status_code, 200)

    def test_api_gender(self):
        curve_api = CurveDataParser()

        curve_api.patient = self.patient

        self.patient.user.gender = 'Male'
        self.patient.user.save()

        self.assertEquals(curve_api.api_gender(), 'male')

        self.patient.user.gender = 'Female'
        self.patient.user.save()

        self.assertEquals(self.patient.user.gender, 'Female')
        self.assertEquals(curve_api.api_gender(), 'female')

    def test_data_parse_curves_cephalic_perimeter(self):

        self.client.force_login(user=self.user2)
        self.client.request()

        response = self.client.get(
            path=reverse(
                viewname='medicalrecords:curve_ajax',
            ),
            follow=True,
            data={'username': self.patient.user.username, 'data_type': 'cephalic_perimeter', }
        )

        self.assertEquals(response.status_code, 200)

    def test_curves_form_invalid_create_view(self):
        """
        Test if create form is invalid with unique together
        """
        self.client.force_login(user=self.health_team.user)

        data = {
            'height': self.HEIGHT,
            'weight': self.WEIGHT,
            'age': self.AGE,
            'cephalic_perimeter': self.CEPHALIC_PERIMETER,
        }

        response = self.client.post(
            path=reverse(
                'medicalrecords:create_curve',
                kwargs={'username': self.user.username}
            ),
            data=data,
            follow=True
        )

        self.assertEquals(response.status_code, 200)


        response2 = self.client.post(
            path=reverse(
                'medicalrecords:create_curve',
                kwargs={'username': self.user.username}
            ),
            data=data,
            follow=True
        )

        self.assertEquals(response2.status_code, 200)

    def test_curves_validation(self):
        """
        Test if curves age validation is ok
        """
        self.curve_test = Curves.objects.create(
            patient=self.patient,
            weight=self.WEIGHT,
            height=self.HEIGHT,
            cephalic_perimeter=self.CEPHALIC_PERIMETER,
            age=233,
        )
        self.curve_test.save()
        self.curve_test.refresh_from_db()

        self.assertEquals(self.curve_test.cephalic_perimeter, 0)

