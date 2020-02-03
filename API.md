# API

## Admin users

### Creating an admin user

You need to create an admin user to manage the database and create normal users. Use the following command to do so:
```
python manage.py createsuperuser
```

Admins can access Django admin panel `/admin/`.

### Managing normal users

An admin can modify any user's money balance. This can be done by logging in via `/login/` and navigating to 
`/accounts/`.

### Managing products

An admin can modify existing products. This can be done by logging in and navigating to `/products/`.

### Searching for purchases

An admin can search for a specific purchase (made by any user) through various search filters. Navigate to 
`/purchases/all/` to do so.

## All users

### Making purchases

All users can buy products via the main page `/`. This action doesn't require a user to be logged in.

### Viewing purchases

Logged-in users can navigate to `/purchases/personal/` to view their past purchases. 

### Logging in and logging out

All users can log in `/login/` and log out `/logout/`.
