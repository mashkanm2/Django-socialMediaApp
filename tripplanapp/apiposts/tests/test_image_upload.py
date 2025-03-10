from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from tripplanapp.apiposts.models import PostModel

class ImageUploadTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_image_upload(self):
        # Create a sample image file
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        
        # Make a POST request to the image upload endpoint
        response = self.client.post('/api/upload-image/', {'image': image})
        
        # Check that the response is 202 Accepted
        self.assertEqual(response.status_code, 202)
        
        # Check that the task ID is returned
        self.assertIn('task_id', response.data)

        # Verify that the image URL and location are saved in the PostModel
        post = PostModel.objects.last()
        self.assertIsNotNone(post.image_url)
        self.assertIsNotNone(post.location)

if __name__ == '__main__':
    unittest.main()
