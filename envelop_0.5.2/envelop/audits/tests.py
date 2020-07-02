from django.test import TestCase
#from setuptools.tests import fixtures
#from audits.models import 
# Create your tests here.

class AuditsViewsTestCase(TestCase):
    fixtures = ['initial_data.json']
    
    def test_index(self):
        resp = self.client.get('/audits/', data=None, follow=False)
        self.assertEqual(resp.status_code, 302, "should get a redirect")
        
    def test_index_follow(self):
        resp = self.client.get('/audits/', data=None, follow=True)
        self.assertEqual(resp.status_code, 200, "should get a redirect")