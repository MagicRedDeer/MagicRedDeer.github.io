from pelican.plugins import seafoam

AUTHOR = "Talha Ahmed"
SITENAME = "Talha Ahmed"
SITEURL = ""

PATH = "content"

TIMEZONE = "Asia/Karachi"
THEME = seafoam.get_path()

STATIC_PATHS = ["images", "files"]

DEFAULT_LANG = "en"

AVATAR = "images/photo.jpg"
ABOUT_ME = "I am the awesomest guy"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
SITESUBTITLE = "Developer, Technical Artist, and Technology Enthusiast"
DISPLAY_TAGS_ON_SIDEBAR = False

# Blogroll
LINKS = (
    ("Github Pages", "https://magicreddeer.github.io"),
    ("LinkedIn", "https://www.linkedin.com/in/talha-ahmed-lazyleopard"),
    ("Github", "https://github.com/magicreddeer"),
    ("Github Ice Animations", "https://github.com/iceanimations"),
    ("IMDB", "https://www.imdb.com/name/nm7491833/"),
    ("BitBucket", "https://bitbucket.org/nebulapipeline/workspace/repositories"),
    ("Ranai.pk", "https://ranai.pk/"),
    (
        "Nebula Toolbox",
        "https://nebula-pipeline-toolbox-docs.readthedocs.io/en/master/00_intro.html",
    ),
)

# Social widget
SOCIAL = (
    ("Github", "https://github.com/magicreddeer"),
    ("LinkedIn", "https://www.linkedin.com/in/talha-ahmed-lazyleopard"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
