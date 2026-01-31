from django.test import TestCase

# Create your tests here.
# myapp/tests.py
from django.test import SimpleTestCase
from myapp.utils import remove_duplicates  # function to test

class UtilsTests(SimpleTestCase):
    def test_remove_duplicates(self):
        # Setup
        sample_list = [1, 2, 2, 3, 4, 5, 5]
        
        # Execute
        result = remove_duplicates(sample_list)
        
        # Assert
        self.assertEqual(result, [1, 2, 3, 4, 5])
