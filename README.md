# travelmate
Creating a social media for sharing trips images and experience as well as accessing traveler and tour leader information.



Django-socialMediaApp is a Django-based web application that allows users to share and discover travel experiences, find similar posts, and vote on posts to tailor user preferences. Users can create trips, add locations, and access information about services available at different locations.

## Features

1. **Custom User Model with SMS OTP Activation**: Secure user registration and authentication using SMS OTP codes.
2. **Post and Comment Management**: Create and manage posts, comments, and replies.
3. **Location Model**: Save all travel locations, allowing users to plan trips.
4. **Similarity Analysis**: Find similar posts using graph models based on locations and features.
5. **PostVote**: Discover user preferences and styles based on post votes.
6. **Trip Planning**: Create trips, add multiple locations, and define start and end dates.
7. **Location-Based Post Discovery**: Find posts related to specific travel locations and view votes.
8. **Service Users**: Users can be designated as services (e.g., restaurants, motels, etc.).


## Usage

1. Access the web application at `http://127.0.0.1:8000/`.
2. Register a new user and activate the account using the SMS OTP code.
3. Log in and start creating posts, comments, and trips.
4. Explore locations and discover similar posts.
5. Vote on posts to help tailor your preferences.
6. View services available at various locations.

## Models

- **CustomUser**: Custom user model with SMS OTP activation.
- **Post**: Model to save posts and manage comments and replies.
- **Comment**: Model for comments related to posts.
- **Reply**: Model for replies to comments.
- **Location**: Model to save travel locations.
- **PostVote**: Model to save user votes on posts.
- **Trip**: Model to create trips with multiple locations.
- **Service**: Model to designate users as services (e.g., restaurants, motels).

## Acknowledgements

- Django for providing the web framework.
- Setup styleguide using cookiecutter from [amirbahador-hub](https://github.com/amirbahador-hub/django_style_guide)
- The Django community for extensive documentation and support.


## project setup

1- compelete cookiecutter workflow (recommendation: leave project_slug empty) and go inside the project
```
cd Django-socialMediaApp
```

2- SetUp venv
```
virtualenv -p python3.13 venv
source venv/bin/activate
```

3- install Dependencies
```
pip install -r requirements_dev.txt
pip install -r requirements.txt
```

4- create your env
```
cp .env.example .env
```

5- Create tables
```
python manage.py migrate
```

6- spin off docker compose
```
docker compose -f docker-compose.dev.yml up -d
```

7- run the project
```
python manage.py runserver
```

## TaskList
- [x] Create a user api (model,services,selectors,tests)
- [x] Create a post api (model,services,selectors,tests)
- [ ] Create a explore api (model,services,selectors,tests)
- [ ] Create a services api (model,services,selectors,tests)
- [ ] Optimization DB connectin (Redis and Cache)
- [ ] Celery and asynchrone Tasks
- [ ] Graph DB and datamining



## Contact

For any questions or inquiries, please contact [mashkanm2@gmail.com].
