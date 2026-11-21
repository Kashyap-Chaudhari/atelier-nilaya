import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_FILE = os.path.join(BASE_DIR, 'templates', 'components', 'mobile_menu.html')

with open(MOBILE_FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# Replace search action
c = c.replace('action="{% url \'campaigns:hero\' %}"', 'action="{% url \'campaigns:vault\' %}"')
c = c.replace('name=""', 'name="q"')
c = c.replace('class="aaranya-mobile-input"', 'name="q" class="aaranya-mobile-input"')

# New & Featured
c = c.replace('href="{% url \'campaigns:hero\' %}#new-arrivals"', 'href="{% url \'campaigns:vault\' %}?filter=new"')
c = c.replace('href="{% url \'campaigns:hero\' %}#bestsellers"', 'href="{% url \'campaigns:vault\' %}?filter=bestseller"')
c = c.replace('href="{% url \'campaigns:hero\' %}#festive"', 'href="{% url \'campaigns:vault\' %}?style=festive"')
c = c.replace('href="{% url \'campaigns:hero\' %}#wedding"', 'href="{% url \'campaigns:category_products\' slug=\'bridal-jewellery\' %}"')
c = c.replace('href="{% url \'campaigns:hero\' %}#bridal-edit"', 'href="{% url \'campaigns:category_products\' slug=\'bridal-jewellery\' %}"')

# Necklaces
c = c.replace('href="{% url \'campaigns:hero\' %}#necklaces-gold"', 'href="{% url \'campaigns:category_products\' slug=\'necklaces\' %}?metal=gold"')
c = c.replace('href="{% url \'campaigns:hero\' %}#necklaces-diamond"', 'href="{% url \'campaigns:category_products\' slug=\'necklaces\' %}?metal=diamond"')
c = c.replace('href="{% url \'campaigns:hero\' %}#necklaces-choker"', 'href="{% url \'campaigns:category_products\' slug=\'necklaces\' %}?sub=choker"')
c = c.replace('href="{% url \'campaigns:hero\' %}#necklaces-temple"', 'href="{% url \'campaigns:category_products\' slug=\'necklaces\' %}?sub=temple"')
c = c.replace('href="{% url \'campaigns:hero\' %}#necklaces-long"', 'href="{% url \'campaigns:category_products\' slug=\'necklaces\' %}?sub=haar"')

# Earrings
c = c.replace('href="{% url \'campaigns:hero\' %}#earrings-jhumkas"', 'href="{% url \'campaigns:category_products\' slug=\'earrings\' %}?sub=jhumka"')
c = c.replace('href="{% url \'campaigns:hero\' %}#earrings-studs"', 'href="{% url \'campaigns:category_products\' slug=\'earrings\' %}?sub=stud"')
c = c.replace('href="{% url \'campaigns:hero\' %}#earrings-chandbalis"', 'href="{% url \'campaigns:category_products\' slug=\'earrings\' %}?sub=chandbali"')
c = c.replace('href="{% url \'campaigns:hero\' %}#earrings-drops"', 'href="{% url \'campaigns:category_products\' slug=\'earrings\' %}?sub=drop"')

# Rings
c = c.replace('href="{% url \'campaigns:hero\' %}#rings-engagement"', 'href="{% url \'campaigns:category_products\' slug=\'rings\' %}?sub=engagement"')
c = c.replace('href="{% url \'campaigns:hero\' %}#rings-diamond"', 'href="{% url \'campaigns:category_products\' slug=\'rings\' %}?sub=diamond"')
c = c.replace('href="{% url \'campaigns:hero\' %}#rings-cocktail"', 'href="{% url \'campaigns:category_products\' slug=\'rings\' %}?sub=cocktail"')

# Bangles
c = c.replace('href="{% url \'campaigns:hero\' %}#bangles-kadas"', 'href="{% url \'campaigns:category_products\' slug=\'bangles\' %}?sub=kada"')
c = c.replace('href="{% url \'campaigns:hero\' %}#bangles-gold"', 'href="{% url \'campaigns:category_products\' slug=\'bangles\' %}?metal=gold"')

# Temple
c = re.sub(r'href="{% url \'campaigns:hero\' %}#temple-[^"]*"', 'href="{% url \'campaigns:category_products\' slug=\'temple-jewellery\' %}"', c)

# Diamond
c = re.sub(r'href="{% url \'campaigns:hero\' %}#dia-[^"]*"', 'href="{% url \'campaigns:category_products\' slug=\'diamond-jewellery\' %}"', c)

# Men
c = re.sub(r'href="{% url \'campaigns:hero\' %}#men-[^"]*"', 'href="{% url \'campaigns:vault\' %}?sub=men"', c)

# Gifts
c = re.sub(r'href="{% url \'campaigns:hero\' %}#gift-[^"]*"', 'href="{% url \'campaigns:vault\' %}?style=gift"', c)

# General leftovers
c = re.sub(r'href="{% url \'campaigns:hero\' %}#[^"]*"', 'href="{% url \'campaigns:vault\' %}"', c)

with open(MOBILE_FILE, 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated mobile_menu.html successfully!")
