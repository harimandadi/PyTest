user_profile = {
    "name" : "John",
    "age" : 30,
    "country" : "USA"
}

if "user_age" in user_profile:
    del user_profile ["user_age"]

print(user_profile)

print(user_profile.keys())
print(user_profile.values())