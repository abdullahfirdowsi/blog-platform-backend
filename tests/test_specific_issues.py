import asyncio
import aiohttp
import io

async def test_specific_issues():
    """Test specific issues found in the main test"""
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Investigating specific issues...\n")
        
        # First, login to get a valid token
        login_data = {
            "email": "testuser.profile@example.com",
            "password": "testpassword123"
        }
        
        async with session.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                login_result = await response.json()
                access_token = login_result["access_token"]
                user_info = login_result["user"]
                print(f"✅ Login successful")
                print(f"   User object keys: {list(user_info.keys())}")
                print(f"   User ID key 'id': {user_info.get('id', 'NOT FOUND')}")
            else:
                print(f"❌ Login failed: {response.status}")
                return
        
        print("\n" + "="*50)
        
        # Test 1: Unauthorized access
        print("\n1️⃣ Testing unauthorized access...")
        image_data = b'fake image data'
        data = aiohttp.FormData()
        data.add_field('image', io.BytesIO(image_data), filename='test.png', content_type='image/png')
        
        async with session.post(
            f"{base_url}/images/upload",
            data=data
        ) as response:
            status = response.status
            text = await response.text()
            print(f"   Status: {status}")
            print(f"   Response: {text}")
            if status in [401, 403]:
                print(f"   ✅ Authentication properly rejected (status {status})")
            else:
                print(f"   ❌ Expected 401/403, got {status}")
        
        # Test 2: Invalid image upload
        print("\n2️⃣ Testing invalid image upload...")
        text_data = b'This is not an image file'
        data = aiohttp.FormData()
        data.add_field('image', io.BytesIO(text_data), filename='test.txt', content_type='text/plain')
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with session.post(
            f"{base_url}/images/upload",
            data=data,
            headers=headers
        ) as response:
            status = response.status
            text = await response.text()
            print(f"   Status: {status}")
            print(f"   Response: {text}")
            if status == 400:
                print("   ✅ Invalid file correctly rejected")
            else:
                print(f"   ❌ Expected 400, got {status}")
        
        # Test 3: Get user by ID
        print("\n3️⃣ Testing get user by ID...")
        user_id = user_info.get('id')
        if user_id:
            async with session.get(
                f"{base_url}/auth/users/{user_id}",
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            ) as response:
                status = response.status
                if status == 200:
                    user_data = await response.json()
                    print(f"   ✅ User retrieved successfully")
                    print(f"   Username: {user_data['username']}")
                    print(f"   Profile picture: {user_data.get('profile_picture', 'None')}")
                else:
                    text = await response.text()
                    print(f"   ❌ Failed: {status} - {text}")
        else:
            print("   ❌ No user ID available")
        
        # Test 4: Test additional edge cases
        print("\n4️⃣ Testing edge cases...")
        
        # Test empty file
        print("   Testing empty file...")
        empty_data = b''
        data = aiohttp.FormData()
        data.add_field('image', io.BytesIO(empty_data), filename='empty.png', content_type='image/png')
        
        async with session.post(
            f"{base_url}/images/upload",
            data=data,
            headers=headers
        ) as response:
            status = response.status
            print(f"     Empty file status: {status}")
            if status == 400:
                print("     ✅ Empty file correctly rejected")

async def main():
    await test_specific_issues()

if __name__ == "__main__":
    asyncio.run(main())

