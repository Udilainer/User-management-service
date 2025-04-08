import user_service

user1 = user_service.User(15, 'Karl Sholz', 'karlsholz52@mail.com')
user2 = user_service.User(17, 'John Yorih', 'johnyor2@mail.com')

user_service = user_service.UserService()
user_service.add_user(user1)
user_service.add_user(user2)

def main():
    print(user_service)

    user_service.remove_user_by_id(15)

    print(user_service)

if __name__ == '__main__':
    main()