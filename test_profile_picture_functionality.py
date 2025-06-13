import asyncio
import aiohttp
import json
import io
from pathlib import Path
from typing import Dict, Optional

class ProfilePictureTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.test_user_data = {
            "username": "testuser_profile",
            "email": "testuser.profile@example.com",
            "password": "testpassword123"
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def register_test_user(self) -> bool:
        """Register a test user for profile picture testing"""
        print("\n🔵 Testing user registration...")
        try:
            async with self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User registered successfully: {data['message']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Registration failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False

    async def login_test_user(self) -> bool:
        """Login test user and get access token"""
        print("\n🔵 Testing user login...")
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    print(f"✅ User logged in successfully")
                    print(f"   User ID: {data['user']['id']}")
                    print(f"   Username: {data['user']['username']}")
                    print(f"   Current profile picture: {data['user'].get('profile_picture', 'None')}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Login failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    async def test_image_upload(self) -> Optional[str]:
        """Test image upload functionality"""
        print("\n🔵 Testing image upload...")
        try:
            # Create a dummy image file
            image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x1cIDATx\x9cc````\x00\x82\x06\x16\xa6\x01\x82\x06\x16\xa6\x01\x82\x06\x16\xa6\x01\x00\x00\x08\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Create form data
            data = aiohttp.FormData()
            data.add_field('image', io.BytesIO(image_data), filename='test-profile.png', content_type='image/png')

            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.post(
                f"{self.base_url}/images/upload",
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Image uploaded successfully")
                    print(f"   Image URL: {data['imageUrl']}")
                    return data['imageUrl']
                else:
                    text = await response.text()
                    print(f"❌ Image upload failed: {response.status} - {text}")
                    return None
        except Exception as e:
            print(f"❌ Image upload error: {str(e)}")
            return None

    async def test_list_images(self) -> bool:
        """Test listing uploaded images"""
        print("\n🔵 Testing image listing...")
        try:
            async with self.session.get(
                f"{self.base_url}/images/list",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Images listed successfully")
                    print(f"   Found {len(data['images'])} images")
                    for img in data['images'][:3]:  # Show first 3 images
                        print(f"   - {img['key']} ({img['size']} bytes)")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Image listing failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Image listing error: {str(e)}")
            return False

    async def test_update_profile_picture(self, image_url: str) -> bool:
        """Test updating user's profile picture"""
        print("\n🔵 Testing profile picture update...")
        try:
            update_data = {"profile_picture": image_url}
            async with self.session.put(
                f"{self.base_url}/auth/update-profile-picture",
                json=update_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Profile picture updated successfully")
                    print(f"   New profile picture: {data['profile_picture']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Profile picture update failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Profile picture update error: {str(e)}")
            return False

    async def test_get_current_user_profile(self) -> bool:
        """Test getting current user profile with profile picture"""
        print("\n🔵 Testing current user profile retrieval...")
        try:
            async with self.session.get(
                f"{self.base_url}/auth/me",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User profile retrieved successfully")
                    print(f"   Username: {data['username']}")
                    print(f"   Email: {data['email']}")
                    print(f"   Profile picture: {data.get('profile_picture', 'None')}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Profile retrieval failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Profile retrieval error: {str(e)}")
            return False

    async def test_get_user_by_id(self, user_id: str) -> bool:
        """Test getting user by ID (includes profile picture)"""
        print("\n🔵 Testing user retrieval by ID...")
        try:
            async with self.session.get(
                f"{self.base_url}/auth/users/{user_id}",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User retrieved by ID successfully")
                    print(f"   Username: {data['username']}")
                    print(f"   Profile picture: {data.get('profile_picture', 'None')}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ User retrieval by ID failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ User retrieval by ID error: {str(e)}")
            return False

    async def test_remove_profile_picture(self) -> bool:
        """Test removing profile picture (setting to null)"""
        print("\n🔵 Testing profile picture removal...")
        try:
            update_data = {"profile_picture": None}
            async with self.session.put(
                f"{self.base_url}/auth/update-profile-picture",
                json=update_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Profile picture removed successfully")
                    print(f"   Profile picture: {data.get('profile_picture', 'None')}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Profile picture removal failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Profile picture removal error: {str(e)}")
            return False

    async def test_invalid_image_upload(self) -> bool:
        """Test uploading invalid file types"""
        print("\n🔵 Testing invalid image upload...")
        try:
            # Create a dummy text file
            text_data = b'This is not an image file'
            
            data = aiohttp.FormData()
            data.add_field('image', io.BytesIO(text_data), filename='test.txt', content_type='text/plain')

            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.post(
                f"{self.base_url}/images/upload",
                data=data,
                headers=headers
            ) as response:
                if response.status == 400:
                    data = await response.json()
                    print(f"✅ Invalid file type correctly rejected: {data['detail']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Invalid file was accepted (should be rejected): {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Invalid image upload test error: {str(e)}")
            return False

    async def test_unauthorized_access(self) -> bool:
        """Test accessing profile picture endpoints without authentication"""
        print("\n🔵 Testing unauthorized access...")
        try:
            # Try to upload image without token
            image_data = b'fake image data'
            data = aiohttp.FormData()
            data.add_field('image', io.BytesIO(image_data), filename='test.png', content_type='image/png')

            async with self.session.post(
                f"{self.base_url}/images/upload",
                data=data
            ) as response:
                if response.status == 401:
                    print(f"✅ Upload correctly rejected without authentication")
                    return True
                else:
                    print(f"❌ Upload should require authentication: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Unauthorized access test error: {str(e)}")
            return False

    async def cleanup_test_user(self) -> bool:
        """Clean up test user (Note: This would require a delete endpoint)"""
        print("\n🔵 Cleanup note: Test user will remain in database")
        print(f"   Email: {self.test_user_data['email']}")
        print(f"   Username: {self.test_user_data['username']}")
        return True

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all profile picture functionality tests"""
        print("🚀 Starting Profile Picture Functionality Test Suite")
        print("=" * 60)
        
        results = {}
        user_id = None
        uploaded_image_url = None

        # Test user registration and login
        results["register"] = await self.register_test_user()
        if results["register"]:
            results["login"] = await self.login_test_user()
        else:
            # Try to login with existing user
            results["login"] = await self.login_test_user()

        if not results["login"]:
            print("❌ Cannot proceed without successful login")
            return results

        # Get user profile to extract user ID
        try:
            async with self.session.get(
                f"{self.base_url}/auth/me",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    user_id = user_data["id"]
        except Exception as e:
            print(f"⚠️ Could not get user ID: {str(e)}")

        # Test image functionality
        results["unauthorized_access"] = await self.test_unauthorized_access()
        results["invalid_image_upload"] = await self.test_invalid_image_upload()
        
        uploaded_image_url = await self.test_image_upload()
        results["image_upload"] = uploaded_image_url is not None
        
        results["list_images"] = await self.test_list_images()
        
        # Test profile picture functionality
        if uploaded_image_url:
            results["update_profile_picture"] = await self.test_update_profile_picture(uploaded_image_url)
        else:
            results["update_profile_picture"] = False
            print("⚠️ Skipping profile picture update (no uploaded image)")
        
        results["get_current_user"] = await self.test_get_current_user_profile()
        
        if user_id:
            results["get_user_by_id"] = await self.test_get_user_by_id(user_id)
        else:
            results["get_user_by_id"] = False
            print("⚠️ Skipping user by ID test (no user ID)")
        
        results["remove_profile_picture"] = await self.test_remove_profile_picture()
        results["get_user_after_removal"] = await self.test_get_current_user_profile()
        
        # Cleanup
        results["cleanup"] = await self.cleanup_test_user()

        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = 0
        
        for test_name, result in results.items():
            if test_name != "cleanup":
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name.replace('_', ' ').title():<25} {status}")
                if result:
                    passed += 1
                total += 1
        
        print("\n" + "=" * 60)
        print(f"OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 All profile picture functionality tests PASSED!")
        else:
            print(f"⚠️ {total-passed} test(s) failed. Please review the issues above.")
        
        return results


async def main():
    """Main function to run the test suite"""
    async with ProfilePictureTestSuite() as test_suite:
        await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

