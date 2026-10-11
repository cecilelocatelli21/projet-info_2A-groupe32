"""Demo data used while Open Library / the backend is unavailable.

Everything in this module is FICTITIOUS or illustrative: ratings, review counts, reviews, the demo
user and the people around them are invented. Books carry ids prefixed with ``demo-`` so they can
never be confused with real Open Library work ids (``OL...W``).

Covers come from Open Library (by ISBN) when ``EXLIBRIS_DEMO_COVERS=remote``; the UI always
renders a generated cover underneath, so a missing cover never shows as a broken image.
"""

from __future__ import annotations

import zlib
from datetime import date

from data.models import Book, LibraryEntry, Person, Profile, Review
from utils.settings import demo_covers_mode

DEMO_PREFIX = "demo-"

GENRE_SF = "Science-fiction"
GENRE_DYSTOPIA = "Dystopie"
GENRE_FANTASY = "Fantasy"
GENRE_CLASSICS = "Classiques"
GENRE_CRIME = "Policier & Thriller"
GENRE_CONTEMPORARY = "Roman contemporain"
GENRE_YOUTH = "Jeunesse"
GENRE_ESSAYS = "Essais & Société"
GENRE_ADVENTURE = "Aventure"

# slug, title, authors, year, genres, isbn13, pages, publisher, rating, ratings count, description
_RAW_BOOKS = [
    (
        "petit-prince", "Le Petit Prince", ("Antoine de Saint-Exupéry",), 1943,
        (GENRE_CLASSICS, GENRE_YOUTH), "9782070612758", 96, "Gallimard", 4.3, 18420,
        "Un aviateur échoué dans le désert rencontre un petit garçon venu d'une autre planète. "
        "Un conte poétique sur l'amitié, la perte et ce qui compte vraiment.",
    ),
    (
        "1984", "1984", ("George Orwell",), 1949, (GENRE_DYSTOPIA, GENRE_SF),
        "9780451524935", 328, "Signet Classics", 4.2, 25310,
        "Dans un monde surveillé en permanence, Winston tente de préserver sa pensée libre face à "
        "un pouvoir qui réécrit le passé. Un classique glaçant sur la vérité et le contrôle.",
    ),
    (
        "dune", "Dune", ("Frank Herbert",), 1965, (GENRE_SF,),
        "9780441013593", 688, "Ace", 4.3, 21980,
        "Sur la planète désertique Arrakis, seule source de l'épice la plus précieuse de "
        "l'univers, le jeune Paul Atréides voit sa famille entraînée dans une guerre de pouvoir "
        "et de destin.",
    ),
    (
        "fahrenheit-451", "Fahrenheit 451", ("Ray Bradbury",), 1953, (GENRE_DYSTOPIA,),
        "9781451673319", 249, "Simon & Schuster", 4.0, 12750,
        "Guy Montag est pompier : son métier consiste à brûler les livres. Jusqu'au jour où il "
        "commence à s'interroger sur ce qu'il détruit.",
    ),
    (
        "brave-new-world", "Brave New World", ("Aldous Huxley",), 1932, (GENRE_DYSTOPIA,),
        "9780060850524", 288, "Harper Perennial", 3.9, 9840,
        "Une société stable et heureuse en apparence, fondée sur le conditionnement et le "
        "plaisir. Un homme venu de l'extérieur en révèle le prix.",
    ),
    (
        "hobbit", "The Hobbit", ("J.R.R. Tolkien",), 1937, (GENRE_FANTASY, GENRE_ADVENTURE),
        "9780547928227", 300, "Mariner Books", 4.3, 19500,
        "Bilbon Sacquet, hobbit casanier, se retrouve embarqué avec treize nains et un magicien "
        "pour reconquérir un trésor gardé par un dragon.",
    ),
    (
        "name-of-the-wind", "The Name of the Wind", ("Patrick Rothfuss",), 2007,
        (GENRE_FANTASY,), "9780756404741", 662, "DAW Books", 4.5, 14200,
        "Kvothe, aubergiste discret, raconte sa propre légende : l'enfant prodige, la troupe de "
        "saltimbanques, la quête de l'Université et du nom du vent.",
    ),
    (
        "mistborn", "Mistborn: The Final Empire", ("Brandon Sanderson",), 2006,
        (GENRE_FANTASY,), "9780765311788", 541, "Tor Books", 4.4, 11780,
        "Dans un empire dominé depuis mille ans par un tyran immortel, une jeune voleuse "
        "découvre un pouvoir étrange et rejoint une conspiration pour le renverser.",
    ),
    (
        "game-of-thrones", "A Game of Thrones", ("George R. R. Martin",), 1996,
        (GENRE_FANTASY,), "9780553593716", 835, "Bantam", 4.3, 24100,
        "Sur le continent de Westeros, les grandes familles se disputent le Trône de fer tandis "
        "qu'une menace ancienne se réveille au nord.",
    ),
    (
        "hunger-games", "The Hunger Games", ("Suzanne Collins",), 2008,
        (GENRE_DYSTOPIA, GENRE_YOUTH), "9780439023528", 374, "Scholastic", 4.1, 28000,
        "Dans un pays divisé en districts, Katniss se porte volontaire pour un jeu télévisé "
        "mortel imposé par le Capitole. Survivre, c'est aussi garder son humanité.",
    ),
    (
        "harry-potter-1", "Harry Potter à l'école des sorciers", ("J.K. Rowling",), 1997,
        (GENRE_FANTASY, GENRE_YOUTH), "9782070518425", 308, "Gallimard Jeunesse", 4.5, 31200,
        "Le jour de ses onze ans, Harry apprend qu'il est un sorcier et entre à Poudlard, où "
        "l'attendent amitiés, mystères et un passé qu'il ignorait.",
    ),
    (
        "neuromancer", "Neuromancer", ("William Gibson",), 1984, (GENRE_SF,),
        "9780441569595", 271, "Ace", 3.9, 7600,
        "Case, pirate informatique déchu, est recruté pour une dernière mission dans la matrice. "
        "Le roman fondateur du cyberpunk.",
    ),
    (
        "foundation", "Foundation", ("Isaac Asimov",), 1951, (GENRE_SF,),
        "9780553293357", 255, "Bantam Spectra", 4.2, 10300,
        "Alors que l'Empire galactique s'effondre, un mathématicien met en place un plan pour "
        "réduire la durée des siècles de chaos à venir.",
    ),
    (
        "left-hand-of-darkness", "The Left Hand of Darkness", ("Ursula K. Le Guin",), 1969,
        (GENRE_SF,), "9780441478125", 304, "Ace", 4.1, 6400,
        "Un envoyé terrien visite une planète glacée où les habitants n'ont pas de genre fixe. "
        "Une réflexion sur l'altérité, la loyauté et l'amitié.",
    ),
    (
        "martian", "The Martian", ("Andy Weir",), 2011, (GENRE_SF,),
        "9780553418026", 369, "Broadway Books", 4.4, 17900,
        "Seul sur Mars après un accident, l'astronaute Mark Watney doit s'appuyer sur sa "
        "débrouillardise et son humour pour survivre jusqu'aux secours.",
    ),
    (
        "project-hail-mary", "Project Hail Mary", ("Andy Weir",), 2021, (GENRE_SF,),
        "9780593135204", 476, "Ballantine Books", 4.6, 15200,
        "Un professeur se réveille seul dans un vaisseau, sans souvenir de sa mission : sauver "
        "la Terre d'une menace venue du Soleil.",
    ),
    (
        "pride-and-prejudice", "Pride and Prejudice", ("Jane Austen",), 1813,
        (GENRE_CLASSICS,), "9780141439518", 480, "Penguin Classics", 4.3, 21500,
        "Elizabeth Bennet et le fier M. Darcy : un chassé-croisé de préjugés, d'ironie et de "
        "sentiments dans l'Angleterre du début du XIXe siècle.",
    ),
    (
        "jane-eyre", "Jane Eyre", ("Charlotte Brontë",), 1847, (GENRE_CLASSICS,),
        "9780141441146", 532, "Penguin Classics", 4.1, 11200,
        "Orpheline au caractère fier, Jane devient gouvernante à Thornfield Hall, où le maître "
        "des lieux cache un lourd secret.",
    ),
    (
        "frankenstein", "Frankenstein", ("Mary Shelley",), 1818, (GENRE_CLASSICS, GENRE_SF),
        "9780141439471", 288, "Penguin Classics", 3.9, 10100,
        "Le jeune Victor Frankenstein donne vie à une créature qu'il abandonne aussitôt. Un "
        "récit gothique sur la responsabilité du créateur.",
    ),
    (
        "dracula", "Dracula", ("Bram Stoker",), 1897, (GENRE_CLASSICS,),
        "9780141439846", 488, "Penguin Classics", 4.0, 9300,
        "Un jeune clerc se rend en Transylvanie chez un comte énigmatique. Le roman qui a fixé "
        "le mythe du vampire moderne.",
    ),
    (
        "great-gatsby", "The Great Gatsby", ("F. Scott Fitzgerald",), 1925, (GENRE_CLASSICS,),
        "9780743273565", 180, "Scribner", 3.9, 24600,
        "Dans l'Amérique des années folles, un voisin mystérieux organise des fêtes somptueuses "
        "pour retrouver un amour perdu.",
    ),
    (
        "to-kill-a-mockingbird", "To Kill a Mockingbird", ("Harper Lee",), 1960,
        (GENRE_CLASSICS,), "9780061120084", 336, "Harper Perennial", 4.3, 27300,
        "Dans le Sud des États-Unis des années 1930, une petite fille observe le procès d'un "
        "homme noir injustement accusé, défendu par son père avocat.",
    ),
    (
        "etranger", "L'Étranger", ("Albert Camus",), 1942, (GENRE_CLASSICS,),
        "9782070360024", 186, "Gallimard", 4.0, 15600,
        "Meursault enterre sa mère sans larmes, puis commet un acte qui le conduit devant un "
        "tribunal. Un roman de l'absurde, sec et lumineux.",
    ),
    (
        "la-peste", "La Peste", ("Albert Camus",), 1947, (GENRE_CLASSICS,),
        "9782070360420", 336, "Gallimard", 4.1, 9100,
        "Oran est frappée par une épidémie de peste. Un médecin et ses compagnons font face, "
        "chacun à sa manière, à ce fléau.",
    ),
    (
        "hundred-years-of-solitude", "One Hundred Years of Solitude",
        ("Gabriel García Márquez",), 1967, (GENRE_CLASSICS,), "9780060883287", 417,
        "Harper Perennial", 4.1, 13900,
        "L'histoire de la famille Buendía et du village imaginaire de Macondo, entre merveilleux, "
        "solitude et cycles de l'histoire.",
    ),
    (
        "alchemist", "The Alchemist", ("Paulo Coelho",), 1988, (GENRE_CONTEMPORARY,),
        "9780062315007", 208, "HarperOne", 3.9, 21800,
        "Un jeune berger andalou part vers les pyramides à la recherche d'un trésor et découvre "
        "sa propre légende personnelle.",
    ),
    (
        "gone-girl", "Gone Girl", ("Gillian Flynn",), 2012, (GENRE_CRIME,),
        "9780307588371", 415, "Crown", 4.1, 18900,
        "Le jour de leur anniversaire de mariage, Amy disparaît. Les soupçons se portent sur son "
        "mari. Un thriller psychologique aux revirements multiples.",
    ),
    (
        "dragon-tattoo", "The Girl with the Dragon Tattoo", ("Stieg Larsson",), 2005,
        (GENRE_CRIME,), "9780307949486", 644, "Vintage Crime", 4.1, 14800,
        "Un journaliste et une hackeuse hors norme enquêtent sur la disparition, quarante ans "
        "plus tôt, de l'héritière d'une grande famille industrielle.",
    ),
    (
        "and-then-there-were-none", "And Then There Were None", ("Agatha Christie",), 1939,
        (GENRE_CRIME, GENRE_CLASSICS), "9780062073488", 272, "William Morrow", 4.3, 17200,
        "Dix inconnus sont invités sur une île isolée. Un à un, ils disparaissent selon une "
        "comptine macabre. Le huis clos de référence.",
    ),
    (
        "orient-express", "Murder on the Orient Express", ("Agatha Christie",), 1934,
        (GENRE_CRIME,), "9780062693662", 288, "William Morrow", 4.2, 14100,
        "Bloqué par la neige, le train de luxe voit un passager assassiné. Hercule Poirot doit "
        "démêler les mensonges de tous les voyageurs.",
    ),
    (
        "midnight-library", "The Midnight Library", ("Matt Haig",), 2020, (GENRE_CONTEMPORARY,),
        "9780525559474", 304, "Viking", 4.0, 12600,
        "Entre la vie et la mort, Nora découvre une bibliothèque où chaque livre est une vie "
        "qu'elle aurait pu mener.",
    ),
    (
        "circe", "Circe", ("Madeline Miller",), 2018, (GENRE_FANTASY, GENRE_CONTEMPORARY),
        "9780316556347", 393, "Little, Brown", 4.3, 11800,
        "La nymphe Circé, reléguée sur une île, apprend la magie et croise des figures de la "
        "mythologie grecque. Une odyssée vue par celle qu'on oublie.",
    ),
    (
        "normal-people", "Normal People", ("Sally Rooney",), 2018, (GENRE_CONTEMPORARY,),
        "9781984822178", 266, "Hogarth", 3.8, 9200,
        "Marianne et Connell, au lycée puis à l'université, se rapprochent et s'éloignent sans "
        "cesse. Une histoire d'amour et de classe sociale.",
    ),
    (
        "sapiens", "Sapiens", ("Yuval Noah Harari",), 2011, (GENRE_ESSAYS,),
        "9780062316097", 464, "Harper", 4.4, 18300,
        "Une histoire de l'humanité, des chasseurs-cueilleurs à nos sociétés numériques, qui "
        "interroge nos croyances collectives.",
    ),
    (
        "educated", "Educated", ("Tara Westover",), 2018, (GENRE_ESSAYS,),
        "9780399590504", 352, "Random House", 4.5, 15500,
        "Élevée dans une famille survivaliste, Tara n'entre en classe qu'à dix-sept ans. Un "
        "récit d'émancipation par l'éducation.",
    ),
    (
        "atomic-habits", "Atomic Habits", ("James Clear",), 2018, (GENRE_ESSAYS,),
        "9780735211292", 320, "Avery", 4.4, 21400,
        "Une méthode concrète pour construire de bonnes habitudes et se défaire des mauvaises "
        "grâce à de petits changements répétés.",
    ),
    (
        "catcher-in-the-rye", "The Catcher in the Rye", ("J.D. Salinger",), 1951,
        (GENRE_CLASSICS,), "9780316769488", 277, "Little, Brown", 3.8, 15100,
        "Quelques jours d'errance à New York pour Holden Caulfield, adolescent révolté contre le "
        "monde des adultes.",
    ),
]

# Books highlighted in the home banner, in rotation order
FEATURED_SLUGS = ("dune", "project-hail-mary", "pride-and-prejudice", "circe")


def _cover_url(isbn: str | None) -> str | None:
    if not isbn or demo_covers_mode() == "generated":
        return None
    # default=false -> HTTP 404 instead of a blank 1x1 image when Open Library has no cover
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"


def _build_books() -> dict[str, Book]:
    books: dict[str, Book] = {}
    for slug, title, authors, year, genres, isbn, pages, publisher, rating, count, desc in _RAW_BOOKS:
        work_id = f"{DEMO_PREFIX}{slug}"
        books[work_id] = Book(
            work_id=work_id,
            title=title,
            authors=authors,
            cover_url=_cover_url(isbn),
            description=desc,
            genres=genres,
            rating=rating,
            ratings_count=count,
            published=year,
            pages=pages,
            publisher=publisher,
            isbn=isbn,
            is_demo=True,
        )
    return books


def books() -> dict[str, Book]:
    """The demo catalogue, keyed by work_id (rebuilt each call so env switches apply)."""
    return _build_books()


def is_demo_work_id(work_id: str) -> bool:
    return work_id.startswith(DEMO_PREFIX)


def wid(slug: str) -> str:
    return f"{DEMO_PREFIX}{slug}"


# ---------------------------------------------------------------------------------------------
# Demo user, their library, reviews and social graph
# ---------------------------------------------------------------------------------------------

DEMO_USER_ID = 0
DEMO_USERNAME = "camille.demo"
DEMO_DISPLAY_NAME = "Camille"
DEMO_BIO = (
    "Dévoreuse de science-fiction et de classiques. Toujours trois livres en cours, "
    "une pile à lire qui ne diminue jamais."
)
DEMO_MEMBER_SINCE = date(2025, 3, 14)

# (slug, status, date_added, date_read, rating)
_DEMO_LIBRARY = [
    ("1984", "read", date(2025, 4, 2), date(2025, 4, 20), 5),
    ("petit-prince", "read", date(2025, 4, 5), date(2025, 4, 6), 5),
    ("pride-and-prejudice", "read", date(2025, 6, 11), date(2025, 7, 3), 4),
    ("martian", "read", date(2025, 8, 1), date(2025, 8, 15), 4),
    ("etranger", "read", date(2025, 9, 9), date(2025, 9, 12), 4),
    ("gone-girl", "read", date(2025, 11, 2), date(2025, 11, 20), 3),
    ("sapiens", "read", date(2026, 1, 8), date(2026, 2, 14), 5),
    ("dune", "in progress", date(2026, 8, 20), None, None),
    ("circe", "in progress", date(2026, 9, 3), None, None),
    ("name-of-the-wind", "in progress", date(2026, 9, 28), None, None),
    ("project-hail-mary", "to read", date(2026, 7, 14), None, None),
    ("hobbit", "to read", date(2026, 7, 30), None, None),
    ("midnight-library", "to read", date(2026, 8, 9), None, None),
    ("foundation", "to read", date(2026, 9, 15), None, None),
    ("educated", "to read", date(2026, 10, 1), None, None),
    ("game-of-thrones", "abandoned", date(2025, 12, 1), date(2026, 1, 5), 2),
]

# Reviews written by the demo user: slug -> text
_DEMO_MY_REVIEWS = {
    "1984": (
        "Un livre qui ne vieillit pas. La fin m'a laissée sans voix pendant plusieurs jours : "
        "à relire tous les cinq ans pour voir ce qui a changé autour de nous."
    ),
    "petit-prince": (
        "Je l'avais lu enfant sans rien comprendre. Adulte, chaque page frappe juste. "
        "Court, mais on ne le referme pas indemne."
    ),
    "pride-and-prejudice": (
        "Les dialogues sont d'une finesse incroyable et l'ironie d'Austen n'a pas pris une "
        "ride. Darcy reste insupportable puis irrésistible, comme prévu."
    ),
    "martian": (
        "Efficace, drôle et étonnamment pédagogue. J'ai lu les cent dernières pages d'une "
        "traite, un dimanche."
    ),
    "game-of-thrones": (
        "Univers impressionnant mais trop de personnages pour moi à ce moment-là. "
        "Je réessaierai peut-être plus tard."
    ),
}

_FRIENDS = [
    Person("lea_p", 11, "Lectrice de polars, thé noir et plaids."),
    Person("marc.lit", 12, "Un roman par semaine, sans exception."),
    Person("ines.reads", 13, "Fantasy, SF et chroniques de lecture."),
    Person("thomas_b", 14, "Classiques d'abord, le reste ensuite."),
    Person("nora_pages", 15, "Je note tout. Absolument tout."),
    Person("julien.k", 16, "Essais, histoire, un peu de BD."),
]

_FOLLOWERS = (_FRIENDS[0], _FRIENDS[2], _FRIENDS[3], _FRIENDS[4])
_FOLLOWING = (_FRIENDS[0], _FRIENDS[1], _FRIENDS[2], _FRIENDS[5])

# Reviews by other (fictional) readers: slug -> [(author, rating, text, likes, date)]
_OTHER_REVIEWS = {
    "dune": [
        ("ines.reads", 5, "Une immersion totale. Le monde est si dense qu'on en sort ébloui et "
         "un peu perdu, dans le bon sens.", 24, date(2026, 5, 2)),
        ("marc.lit", 4, "Lent à démarrer, impossible à lâcher ensuite. Les passages sur "
         "l'écologie sont brillants.", 11, date(2026, 3, 18)),
    ],
    "1984": [
        ("thomas_b", 5, "Indispensable. La novlangue est l'idée la plus terrifiante de la "
         "littérature du XXe siècle.", 31, date(2026, 1, 9)),
        ("lea_p", 4, "Sombre, bien sûr, mais d'une lucidité qui fait mal.", 8, date(2025, 11, 4)),
    ],
    "project-hail-mary": [
        ("nora_pages", 5, "Mon livre de l'année. Je n'en dis rien de plus pour ne pas gâcher "
         "le plaisir de la découverte.", 42, date(2026, 6, 21)),
        ("julien.k", 5, "Drôle, émouvant, intelligent. Une vraie leçon d'amitié.", 17,
         date(2026, 7, 1)),
    ],
    "pride-and-prejudice": [
        ("lea_p", 5, "Chaque relecture me révèle un nouveau trait d'humour.", 14,
         date(2026, 2, 12)),
        ("thomas_b", 4, "Un monument, mais surtout un très bon moment de lecture.", 6,
         date(2025, 12, 2)),
    ],
    "circe": [
        ("ines.reads", 5, "Une écriture sensuelle et patiente. J'ai relu mon vieux manuel de "
         "mythologie juste après.", 19, date(2026, 4, 8)),
        ("nora_pages", 4, "Beau, un peu long au milieu mais tellement bien porté.", 5,
         date(2026, 4, 30)),
    ],
    "martian": [
        ("marc.lit", 5, "Du suspense avec des équations. Qui l'eût cru ?", 13, date(2025, 10, 7)),
        ("julien.k", 4, "Très divertissant. Le ton sarcastique du héros est parfait.", 4,
         date(2025, 12, 28)),
    ],
    "etranger": [
        ("thomas_b", 4, "Court et dérangeant. La plage reste une des scènes les plus "
         "étranges que j'aie lues.", 9, date(2026, 3, 3)),
    ],
    "gone-girl": [
        ("lea_p", 4, "Les revirements sont bien ficelés, l'ambiance glaçante.", 10,
         date(2025, 9, 14)),
        ("nora_pages", 3, "Efficace mais je n'ai aimé aucun personnage, ce qui était sûrement "
         "voulu.", 3, date(2025, 10, 1)),
    ],
    "sapiens": [
        ("julien.k", 5, "Ça donne envie de relire l'histoire autrement. Quelques "
         "raccourcis, mais très stimulant.", 22, date(2026, 2, 2)),
    ],
    "name-of-the-wind": [
        ("ines.reads", 5, "La musique de la prose, tout simplement.", 27, date(2026, 5, 22)),
        ("marc.lit", 4, "Un début magistral. Vivement la suite… un jour.", 12,
         date(2026, 6, 9)),
    ],
    "hobbit": [
        ("thomas_b", 5, "Parfait pour commencer la fantasy, un livre-refuge.", 15,
         date(2026, 1, 26)),
    ],
    "foundation": [
        ("julien.k", 4, "Des idées géniales, des personnages un peu en retrait. Très "
         "bon quand même.", 7, date(2026, 4, 14)),
    ],
    "midnight-library": [
        ("nora_pages", 4, "Doux et réconfortant, parfait pour une journée grise.", 9,
         date(2026, 2, 19)),
    ],
    "educated": [
        ("lea_p", 5, "Bouleversant et très bien raconté. Je l'ai offert trois fois.", 18,
         date(2026, 3, 27)),
    ],
}


def initial_library() -> dict[str, LibraryEntry]:
    """The demo user's starting library, keyed by work_id."""
    catalog = books()
    entries: dict[str, LibraryEntry] = {}
    for i, (slug, status, added, read_on, rating) in enumerate(_DEMO_LIBRARY, start=1):
        work_id = wid(slug)
        entries[work_id] = LibraryEntry(
            reading_id=i,
            book=catalog[work_id],
            status=status,
            date_added=added,
            date_read=read_on,
            rating=rating,
        )
    return entries


def initial_my_reviews() -> dict[str, Review]:
    """The demo user's reviews, keyed by work_id."""
    catalog = books()
    lib = {slug: (status, read_on, rating) for slug, status, _, read_on, rating in _DEMO_LIBRARY}
    reviews: dict[str, Review] = {}
    for n, (slug, text) in enumerate(_DEMO_MY_REVIEWS.items(), start=1):
        _, read_on, rating = lib[slug]
        work_id = wid(slug)
        reviews[work_id] = Review(
            review_id=1000 + n,
            work_id=work_id,
            author=DEMO_DISPLAY_NAME,
            text=text,
            rating=rating,
            created=read_on,
            likes=n * 3 % 7 + 1,
            book_title=catalog[work_id].title,
            is_mine=True,
        )
    return reviews


def other_reviews(work_id: str) -> list[Review]:
    """Reviews written by the fictitious other readers for a given demo book."""
    slug = work_id.removeprefix(DEMO_PREFIX)
    items = _OTHER_REVIEWS.get(slug, [])
    return [
        Review(
            review_id=2000 + zlib.crc32(f"{slug}:{author}".encode()) % 10000,
            work_id=work_id,
            author=author,
            text=text,
            rating=rating,
            created=created,
            likes=likes,
        )
        for author, rating, text, likes, created in items
    ]


def demo_profile() -> Profile:
    return Profile(
        username=DEMO_USERNAME,
        display_name=DEMO_DISPLAY_NAME,
        bio=DEMO_BIO,
        member_since=DEMO_MEMBER_SINCE,
        followers=_FOLLOWERS,
        following=_FOLLOWING,
    )
