"""Short content for the footer's info pages: slug -> (title, [paragraphs]).

Shopwise is a demo project, so this text is deliberately generic. Edit it freely.
"""

PAGES = {
    "contact-us": (
        "Contact Us",
        [
            "Questions about an order or a product? Email us at support@shopwise.example and we will get back to you.",
            "This is a demo store built for the CodeAlpha Full Stack Development internship, so replace these placeholder contact details with your own.",
        ],
    ),
    "about-us": (
        "About Us",
        [
            "Shopwise is a demo e-commerce store built with Django, HTML, CSS and JavaScript as Task 1 of the CodeAlpha Full Stack Development internship.",
            "It includes product browsing with categories and subcategories, a shopping cart, user accounts, checkout and order history.",
        ],
    ),
    "careers": (
        "Careers",
        ["We have no open positions right now. This page is a placeholder for a real careers listing."],
    ),
    "shopwise-stories": (
        "Shopwise Stories",
        ["Stories from our customers and sellers will appear here."],
    ),
    "press": (
        "Press",
        ["For media enquiries, write to press@shopwise.example."],
    ),
    "corporate-information": (
        "Corporate Information",
        [
            "Shopwise is a student demo project and is not a registered business.",
            "Add your company name, registration details and registered address here if you turn this into a real store.",
        ],
    ),
    "payments": (
        "Payments",
        [
            "Payment is simulated in this demo: when you place an order it is saved with the status Pending and no money is charged.",
            "The payment logos in the footer are for illustration only.",
        ],
    ),
    "shipping": (
        "Shipping",
        ["Orders are shipped to the address you enter at checkout. Shipping times and charges are placeholders in this demo."],
    ),
    "cancellation-returns": (
        "Cancellation & Returns",
        [
            "You can cancel an order before it ships. Returns are accepted for unused items in their original packaging.",
            "These policy details are placeholders. Write your own before using this store for real.",
        ],
    ),
    "faq": (
        "FAQ",
        [
            "How do I place an order? Add items to your cart, sign in or register, then go to checkout.",
            "Is my payment real? No. Payment is simulated in this demo.",
            "Where can I see my orders? Use the My orders link in the top bar once you are signed in.",
        ],
    ),
    "terms-of-use": (
        "Terms Of Use",
        ["This demo store is provided for learning purposes. Replace this text with your own terms before launching a real store."],
    ),
    "security": (
        "Security",
        ["Passwords are stored hashed by Django, and forms are protected against cross-site request forgery."],
    ),
    "privacy": (
        "Privacy",
        ["We only store the details needed to run your account and orders. Replace this text with your own privacy policy for a real store."],
    ),
    "sitemap": ("Sitemap", ["Browse every category and subcategory:"]),
    "grievance-redressal": (
        "Grievance Redressal",
        ["If you have a complaint, email grievance@shopwise.example with your order number and we will respond."],
    ),
    "become-a-seller": (
        "Become a Seller",
        ["Seller sign-up is not available in this demo. Products are managed by the store admin."],
    ),
    "advertise": (
        "Advertise",
        ["Advertising options are a placeholder in this demo."],
    ),
    "gift-cards": (
        "Gift Cards",
        ["Gift cards are a placeholder in this demo."],
    ),
    "help-center": (
        "Help Center",
        [
            "Start with our FAQ, or read about payments, shipping, and cancellation and returns from the footer links.",
            "Still stuck? Email support@shopwise.example.",
        ],
    ),
}
