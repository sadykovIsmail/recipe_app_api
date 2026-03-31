"""
Management command: python manage.py seed_data

Creates realistic demo users, profiles, recipes, follows, and likes so the
Discover / Feed pages have content out of the box.

Safe to re-run — uses get_or_create everywhere, so it won't duplicate data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import (
    UserProfile, Recipe, Tag, Ingredient, Follow, RecipeLike, RecipeComment,
)

User = get_user_model()


# ── Seed data ─────────────────────────────────────────────────────────────────

USERS = [
    {
        'email':    'chef.marco@example.com',
        'name':     'Chef Marco',
        'password': 'pass1234!',
        'bio':      'Italian home cook. Pasta from scratch, always.',
        'location': 'Rome, Italy',
        'website':  'https://chefmarco.example.com',
    },
    {
        'email':    'priya.kitchen@example.com',
        'name':     'Priya Kitchen',
        'password': 'pass1234!',
        'bio':      'Bringing authentic Indian flavours to your weeknight dinner.',
        'location': 'Mumbai, India',
        'website':  '',
    },
    {
        'email':    'healthy.tom@example.com',
        'name':     'Tom Eats Clean',
        'password': 'pass1234!',
        'bio':      'Fitness-focused recipes under 500 kcal.',
        'location': 'Austin, TX',
        'website':  '',
    },
    {
        'email':    'baking.sarah@example.com',
        'name':     'Sarah Bakes',
        'password': 'pass1234!',
        'bio':      'Weekend baker obsessed with sourdough and layer cakes.',
        'location': 'London, UK',
        'website':  '',
    },
]

RECIPES = [
    # ── Marco — Italian ───────────────────────────────────────────────────────
    {
        'author': 'chef.marco@example.com',
        'title': 'Spaghetti Carbonara',
        'description': (
            'The real Roman carbonara — no cream, just eggs, Pecorino Romano, '
            'guanciale and freshly cracked black pepper. The silky sauce comes '
            'entirely from emulsifying the egg-cheese mixture off the heat.'
        ),
        'time_minutes': 25,
        'price': '8.00',
        'link': '',
        'tags': ['Italian', 'Pasta', 'Quick'],
        'ingredients': ['spaghetti', 'guanciale', 'eggs', 'Pecorino Romano', 'black pepper'],
    },
    {
        'author': 'chef.marco@example.com',
        'title': 'Cacio e Pepe',
        'description': (
            'Three ingredients, infinite technique. Toasted black pepper bloom, '
            'starchy pasta water and aged Pecorino Romano create a sauce that '
            'coats every strand without a single drop of cream.'
        ),
        'time_minutes': 20,
        'price': '6.00',
        'link': '',
        'tags': ['Italian', 'Pasta', 'Vegetarian'],
        'ingredients': ['tonnarelli', 'Pecorino Romano', 'black pepper', 'pasta water'],
    },
    {
        'author': 'chef.marco@example.com',
        'title': 'Osso Buco alla Milanese',
        'description': (
            'Slow-braised veal shanks in white wine with a bright gremolata '
            'of lemon zest, garlic and parsley stirred in at the last moment. '
            'Traditionally served with saffron risotto.'
        ),
        'time_minutes': 120,
        'price': '22.00',
        'link': '',
        'tags': ['Italian', 'Slow Cook', 'Dinner'],
        'ingredients': ['veal shanks', 'white wine', 'onion', 'carrot', 'celery',
                        'tomato paste', 'lemon zest', 'garlic', 'parsley'],
    },
    {
        'author': 'chef.marco@example.com',
        'title': 'Margherita Pizza',
        'description': (
            'Neapolitan-style dough cold-fermented for 48 hours, San Marzano '
            'tomato sauce, fresh mozzarella and basil. Cooked at maximum oven '
            'temperature on a preheated steel for a blistered leopard crust.'
        ),
        'time_minutes': 90,
        'price': '10.00',
        'link': '',
        'tags': ['Italian', 'Pizza', 'Vegetarian'],
        'ingredients': ['00 flour', 'San Marzano tomatoes', 'fresh mozzarella',
                        'fresh basil', 'olive oil', 'sea salt', 'yeast'],
    },
    # ── Priya — Indian ────────────────────────────────────────────────────────
    {
        'author': 'priya.kitchen@example.com',
        'title': 'Chicken Tikka Masala',
        'description': (
            'Charred, smoky chicken tikka simmered in a rich tomato-cream masala. '
            'The key is the overnight yoghurt marinade and cooking the chicken '
            'under the broiler before it goes into the sauce.'
        ),
        'time_minutes': 60,
        'price': '12.00',
        'link': '',
        'tags': ['Indian', 'Chicken', 'Dinner'],
        'ingredients': ['chicken thighs', 'plain yoghurt', 'garam masala', 'cumin',
                        'coriander', 'turmeric', 'tomato passata', 'heavy cream',
                        'onion', 'ginger', 'garlic', 'butter'],
    },
    {
        'author': 'priya.kitchen@example.com',
        'title': 'Dal Makhani',
        'description': (
            'Black lentils and kidney beans slow-cooked overnight until buttery '
            'soft, then enriched with cream and finished with a smoky tempering '
            'of dried chillies, cumin and asafoetida.'
        ),
        'time_minutes': 480,
        'price': '5.00',
        'link': '',
        'tags': ['Indian', 'Vegetarian', 'Slow Cook'],
        'ingredients': ['black lentils', 'kidney beans', 'butter', 'cream',
                        'tomato', 'onion', 'ginger', 'garlic', 'cumin', 'asafoetida'],
    },
    {
        'author': 'priya.kitchen@example.com',
        'title': 'Palak Paneer',
        'description': (
            'Blanched spinach purée spiced with cumin, ginger and green chilli, '
            'folded through golden paneer cubes. Ready in 30 minutes and '
            'naturally gluten-free.'
        ),
        'time_minutes': 30,
        'price': '8.00',
        'link': '',
        'tags': ['Indian', 'Vegetarian', 'Quick'],
        'ingredients': ['spinach', 'paneer', 'onion', 'tomato', 'green chilli',
                        'ginger', 'garlic', 'cumin', 'garam masala', 'cream'],
    },
    {
        'author': 'priya.kitchen@example.com',
        'title': 'Biryani — Hyderabadi Style',
        'description': (
            'Dum-style layered biryani with marinated chicken, half-cooked '
            'basmati, caramelised onions and saffron milk sealed under dough '
            'and slow-cooked to let the steam do the work.'
        ),
        'time_minutes': 150,
        'price': '15.00',
        'link': '',
        'tags': ['Indian', 'Rice', 'Dinner'],
        'ingredients': ['basmati rice', 'chicken', 'yoghurt', 'fried onions',
                        'saffron', 'whole spices', 'mint', 'ghee', 'rose water'],
    },
    # ── Tom — Healthy ─────────────────────────────────────────────────────────
    {
        'author': 'healthy.tom@example.com',
        'title': 'Greek Chicken Power Bowl',
        'description': (
            'Lemon-oregano marinated grilled chicken over quinoa with cucumber, '
            'cherry tomatoes, kalamata olives, red onion and a drizzle of tzatziki. '
            'Meal-preppable for 4 days.'
        ),
        'time_minutes': 35,
        'price': '9.00',
        'link': '',
        'tags': ['Healthy', 'High Protein', 'Meal Prep'],
        'ingredients': ['chicken breast', 'quinoa', 'cucumber', 'cherry tomatoes',
                        'kalamata olives', 'red onion', 'Greek yoghurt', 'lemon',
                        'oregano', 'olive oil'],
    },
    {
        'author': 'healthy.tom@example.com',
        'title': 'Salmon & Avocado Rice Bowl',
        'description': (
            'Sesame-glazed baked salmon over brown rice with sliced avocado, '
            'edamame, pickled ginger and a sriracha-lime drizzle. '
            'Under 450 kcal and packed with omega-3.'
        ),
        'time_minutes': 30,
        'price': '14.00',
        'link': '',
        'tags': ['Healthy', 'Seafood', 'High Protein'],
        'ingredients': ['salmon fillet', 'brown rice', 'avocado', 'edamame',
                        'sesame oil', 'soy sauce', 'sriracha', 'lime', 'pickled ginger'],
    },
    {
        'author': 'healthy.tom@example.com',
        'title': 'Chickpea & Spinach Stew',
        'description': (
            'One-pan vegan stew with canned chickpeas, baby spinach, diced '
            'tomatoes and smoked paprika. Done in 20 minutes, high in fibre '
            'and protein, under $5 per serving.'
        ),
        'time_minutes': 20,
        'price': '4.50',
        'link': '',
        'tags': ['Vegan', 'Healthy', 'Quick', 'Budget'],
        'ingredients': ['chickpeas', 'spinach', 'tomatoes', 'onion', 'garlic',
                        'smoked paprika', 'cumin', 'vegetable stock'],
    },
    {
        'author': 'healthy.tom@example.com',
        'title': 'Turkey Lettuce Wraps',
        'description': (
            'Seasoned ground turkey with water chestnuts, shiitake mushrooms and '
            'hoisin served in butter lettuce cups. Low-carb, high-protein and '
            'ready in under 25 minutes.'
        ),
        'time_minutes': 22,
        'price': '10.00',
        'link': '',
        'tags': ['Healthy', 'Low Carb', 'Quick'],
        'ingredients': ['ground turkey', 'butter lettuce', 'water chestnuts',
                        'shiitake mushrooms', 'hoisin sauce', 'soy sauce',
                        'sesame oil', 'green onion', 'ginger'],
    },
    # ── Sarah — Baking ────────────────────────────────────────────────────────
    {
        'author': 'baking.sarah@example.com',
        'title': 'Classic Sourdough Bread',
        'description': (
            'Country-style sourdough with an open crumb and crackling crust. '
            'Cold-proofed overnight in the fridge, baked in a Dutch oven to '
            'trap steam for the first 20 minutes. Uses an active 100% hydration starter.'
        ),
        'time_minutes': 1440,
        'price': '3.00',
        'link': '',
        'tags': ['Baking', 'Bread', 'Vegetarian'],
        'ingredients': ['bread flour', 'whole wheat flour', 'water', 'sourdough starter', 'salt'],
    },
    {
        'author': 'baking.sarah@example.com',
        'title': 'Chocolate Lava Cakes',
        'description': (
            'Dark chocolate fondant with a molten centre — batter made ahead '
            'and refrigerated until needed, then baked for exactly 12 minutes. '
            'The ultimate dinner-party dessert that always impresses.'
        ),
        'time_minutes': 30,
        'price': '7.00',
        'link': '',
        'tags': ['Baking', 'Dessert', 'Quick'],
        'ingredients': ['dark chocolate', 'butter', 'eggs', 'caster sugar',
                        'plain flour', 'cocoa powder', 'vanilla extract'],
    },
    {
        'author': 'baking.sarah@example.com',
        'title': 'Lemon Drizzle Cake',
        'description': (
            'Light, zesty loaf soaked twice — first with hot lemon syrup while '
            'still warm, then drizzled with a sharp lemon glaze once cooled. '
            'Uses both zest and juice for maximum lemony punch.'
        ),
        'time_minutes': 60,
        'price': '6.00',
        'link': '',
        'tags': ['Baking', 'Dessert', 'Vegetarian'],
        'ingredients': ['self-raising flour', 'butter', 'caster sugar', 'eggs',
                        'lemon zest', 'lemon juice', 'icing sugar'],
    },
    {
        'author': 'baking.sarah@example.com',
        'title': 'Banana Bread',
        'description': (
            'Moist, one-bowl banana bread with three very ripe bananas, brown '
            'butter and a generous handful of walnuts. No mixer needed — just '
            'a fork and two bowls.'
        ),
        'time_minutes': 75,
        'price': '4.00',
        'link': '',
        'tags': ['Baking', 'Breakfast', 'Quick'],
        'ingredients': ['ripe bananas', 'brown butter', 'brown sugar', 'eggs',
                        'plain flour', 'baking soda', 'salt', 'walnuts'],
    },
]

# Who follows whom: (follower_email, following_email)
FOLLOWS = [
    ('chef.marco@example.com',    'priya.kitchen@example.com'),
    ('chef.marco@example.com',    'baking.sarah@example.com'),
    ('priya.kitchen@example.com', 'chef.marco@example.com'),
    ('priya.kitchen@example.com', 'healthy.tom@example.com'),
    ('healthy.tom@example.com',   'priya.kitchen@example.com'),
    ('healthy.tom@example.com',   'baking.sarah@example.com'),
    ('baking.sarah@example.com',  'chef.marco@example.com'),
    ('baking.sarah@example.com',  'healthy.tom@example.com'),
]

# Which users like which recipe titles
LIKES = [
    ('priya.kitchen@example.com', 'Spaghetti Carbonara'),
    ('healthy.tom@example.com',   'Spaghetti Carbonara'),
    ('baking.sarah@example.com',  'Spaghetti Carbonara'),
    ('chef.marco@example.com',    'Chicken Tikka Masala'),
    ('baking.sarah@example.com',  'Chicken Tikka Masala'),
    ('healthy.tom@example.com',   'Chicken Tikka Masala'),
    ('chef.marco@example.com',    'Salmon & Avocado Rice Bowl'),
    ('priya.kitchen@example.com', 'Salmon & Avocado Rice Bowl'),
    ('baking.sarah@example.com',  'Classic Sourdough Bread'),
    ('healthy.tom@example.com',   'Classic Sourdough Bread'),
    ('chef.marco@example.com',    'Classic Sourdough Bread'),
    ('priya.kitchen@example.com', 'Chocolate Lava Cakes'),
    ('chef.marco@example.com',    'Chocolate Lava Cakes'),
    ('healthy.tom@example.com',   'Palak Paneer'),
    ('baking.sarah@example.com',  'Palak Paneer'),
    ('chef.marco@example.com',    'Biryani — Hyderabadi Style'),
    ('baking.sarah@example.com',  'Margherita Pizza'),
    ('priya.kitchen@example.com', 'Margherita Pizza'),
    ('healthy.tom@example.com',   'Cacio e Pepe'),
    ('priya.kitchen@example.com', 'Turkey Lettuce Wraps'),
    ('chef.marco@example.com',    'Chickpea & Spinach Stew'),
    ('baking.sarah@example.com',  'Banana Bread'),
    ('priya.kitchen@example.com', 'Banana Bread'),
    ('chef.marco@example.com',    'Lemon Drizzle Cake'),
]

COMMENTS = [
    ('priya.kitchen@example.com', 'Spaghetti Carbonara',
     'This is exactly how my Italian neighbour makes it. The guanciale makes all the difference!'),
    ('healthy.tom@example.com', 'Spaghetti Carbonara',
     'Tried this last night — perfect. Went slightly over on the pepper and it was even better.'),
    ('chef.marco@example.com', 'Chicken Tikka Masala',
     'The overnight marinade tip is gold. Never going back to a quick marinade again.'),
    ('baking.sarah@example.com', 'Chicken Tikka Masala',
     'Made this for a dinner party — everyone asked for the recipe!'),
    ('chef.marco@example.com', 'Classic Sourdough Bread',
     'That open crumb is incredible. What hydration do you run your starter at?'),
    ('healthy.tom@example.com', 'Classic Sourdough Bread',
     'My first successful sourdough thanks to this recipe. Life-changing.'),
    ('priya.kitchen@example.com', 'Chocolate Lava Cakes',
     'Made these for Valentine\'s Day — my partner was blown away. 12 minutes exactly is the key.'),
    ('chef.marco@example.com', 'Salmon & Avocado Rice Bowl',
     'Love the sriracha-lime drizzle. Added some furikake on top too — highly recommend.'),
    ('baking.sarah@example.com', 'Banana Bread',
     'Brown butter is a genius addition. I\'ve been making banana bread for years and never thought of it.'),
    ('healthy.tom@example.com', 'Margherita Pizza',
     'The 48-hour cold ferment really does make a difference to the flavour. Worth the wait.'),
]


class Command(BaseCommand):
    help = 'Seed the database with realistic demo users and recipes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all seed users and their data before re-seeding.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            emails = [u['email'] for u in USERS]
            deleted, _ = User.objects.filter(email__in=emails).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing seed records.'))

        # 1. Create users + profiles
        user_map = {}
        for u in USERS:
            user_obj, created = User.objects.get_or_create(
                email=u['email'],
                defaults={'name': u['name']},
            )
            if created:
                user_obj.set_password(u['password'])
                user_obj.save()
            profile, _ = UserProfile.objects.get_or_create(user=user_obj)
            profile.bio = u['bio']
            profile.location = u['location']
            profile.website = u['website']
            profile.save()
            user_map[u['email']] = user_obj
            status = 'created' if created else 'exists'
            self.stdout.write(f'  user {u["email"]} ({status})')

        # 2. Create recipes
        recipe_map = {}
        for r in RECIPES:
            author = user_map[r['author']]
            recipe, created = Recipe.objects.get_or_create(
                user=author,
                title=r['title'],
                defaults={
                    'description': r['description'],
                    'time_minutes': r['time_minutes'],
                    'price':        r['price'],
                    'link':         r['link'],
                },
            )
            if not created:
                # Update description in case it changed
                Recipe.objects.filter(pk=recipe.pk).update(
                    description=r['description'],
                    time_minutes=r['time_minutes'],
                    price=r['price'],
                )

            # Tags
            for tag_name in r['tags']:
                tag, _ = Tag.objects.get_or_create(user=author, name=tag_name)
                recipe.tags.add(tag)

            # Ingredients
            for ing_name in r['ingredients']:
                ing, _ = Ingredient.objects.get_or_create(user=author, name=ing_name)
                recipe.ingredients.add(ing)

            recipe_map[r['title']] = recipe
            status = 'created' if created else 'exists'
            self.stdout.write(f'  recipe "{r["title"]}" ({status})')

        # 3. Follows
        for follower_email, following_email in FOLLOWS:
            Follow.objects.get_or_create(
                follower=user_map[follower_email],
                following=user_map[following_email],
            )
        self.stdout.write(f'  {len(FOLLOWS)} follow relationships ensured')

        # 4. Likes
        for liker_email, recipe_title in LIKES:
            if recipe_title in recipe_map:
                RecipeLike.objects.get_or_create(
                    user=user_map[liker_email],
                    recipe=recipe_map[recipe_title],
                )
        self.stdout.write(f'  {len(LIKES)} likes ensured')

        # 5. Comments
        for commenter_email, recipe_title, text in COMMENTS:
            if recipe_title in recipe_map:
                recipe = recipe_map[recipe_title]
                commenter = user_map[commenter_email]
                exists = RecipeComment.objects.filter(
                    user=commenter, recipe=recipe, text=text
                ).exists()
                if not exists:
                    RecipeComment.objects.create(user=commenter, recipe=recipe, text=text)
        self.stdout.write(f'  {len(COMMENTS)} comments ensured')

        self.stdout.write(self.style.SUCCESS(
            '\nSeed complete! Demo accounts (password: pass1234!):\n'
            '  chef.marco@example.com\n'
            '  priya.kitchen@example.com\n'
            '  healthy.tom@example.com\n'
            '  baking.sarah@example.com\n'
        ))
