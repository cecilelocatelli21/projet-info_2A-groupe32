"""Demo data used while Open Library / the backend is unavailable.

Everything in this module is FICTITIOUS or illustrative: ratings, review counts, reviews, the demo
user and the people around them are invented. Books carry ids prefixed with ``demo-`` so they can
never be confused with real Open Library work ids (``OL...W``).

Covers come from Open Library (by ISBN) when ``EXLIBRIS_DEMO_COVERS=remote``; the UI always
renders a generated cover underneath, so a missing cover never shows as a broken image.
"""

from __future__ import annotations

import zlib
from dataclasses import replace
from datetime import date, timedelta

from data.models import Book, LibraryEntry, Person, Profile, Review
from utils.settings import demo_covers_mode

DEMO_PREFIX = "demo-"

GENRE_SF = "Science Fiction"
GENRE_DYSTOPIA = "Dystopian"
GENRE_FANTASY = "Fantasy"
GENRE_CLASSICS = "Classics"
GENRE_CRIME = "Crime & Thriller"
GENRE_CONTEMPORARY = "Contemporary Fiction"
GENRE_YOUTH = "Young Readers"
GENRE_ESSAYS = "Essays & Society"
GENRE_ADVENTURE = "Adventure"

# slug, title, authors, year, genres, isbn13, pages, publisher, rating, ratings count, description
_RAW_BOOKS = [
    (
        "petit-prince", "Le Petit Prince", ("Antoine de Saint-Exupéry",), 1943,
        (GENRE_CLASSICS, GENRE_YOUTH), "9782070612758", 96, "Gallimard", 4.3, 18420,
        "An aviator stranded in the desert meets a little boy from another planet. "
        "A poetic tale about friendship, loss and what truly matters.",
    ),
    (
        "1984", "1984", ("George Orwell",), 1949, (GENRE_DYSTOPIA, GENRE_SF),
        "9780451524935", 328, "Signet Classics", 4.2, 25310,
        "In a world under constant surveillance, Winston tries to keep his thoughts free from "
        "a regime that rewrites the past. A chilling classic about truth and control.",
    ),
    (
        "dune", "Dune", ("Frank Herbert",), 1965, (GENRE_SF,),
        "9780441013593", 688, "Ace", 4.3, 21980,
        "On the desert planet Arrakis, the only source of the universe's most precious spice, "
        "young Paul Atreides sees his family dragged into a war of power "
        "and destiny.",
    ),
    (
        "fahrenheit-451", "Fahrenheit 451", ("Ray Bradbury",), 1953, (GENRE_DYSTOPIA,),
        "9781451673319", 249, "Simon & Schuster", 4.0, 12750,
        "Guy Montag is a fireman whose job is to burn books. Until the day he "
        "starts questioning what he is destroying.",
    ),
    (
        "brave-new-world", "Brave New World", ("Aldous Huxley",), 1932, (GENRE_DYSTOPIA,),
        "9780060850524", 288, "Harper Perennial", 3.9, 9840,
        "A society that looks stable and happy, built on conditioning and "
        "pleasure. An outsider reveals its price.",
    ),
    (
        "hobbit", "The Hobbit", ("J.R.R. Tolkien",), 1937, (GENRE_FANTASY, GENRE_ADVENTURE),
        "9780547928227", 300, "Mariner Books", 4.3, 19500,
        "Bilbo Baggins, a homebody hobbit, is swept away with thirteen dwarves and a wizard "
        "to reclaim a treasure guarded by a dragon.",
    ),
    (
        "name-of-the-wind", "The Name of the Wind", ("Patrick Rothfuss",), 2007,
        (GENRE_FANTASY,), "9780756404741", 662, "DAW Books", 4.5, 14200,
        "Kvothe, a quiet innkeeper, tells his own legend: the child prodigy, the troupe of "
        "travelling performers, the quest for the University and the name of the wind.",
    ),
    (
        "mistborn", "Mistborn: The Final Empire", ("Brandon Sanderson",), 2006,
        (GENRE_FANTASY,), "9780765311788", 541, "Tor Books", 4.4, 11780,
        "In an empire ruled for a thousand years by an immortal tyrant, a young thief "
        "discovers a strange power and joins a conspiracy to overthrow him.",
    ),
    (
        "game-of-thrones", "A Game of Thrones", ("George R. R. Martin",), 1996,
        (GENRE_FANTASY,), "9780553593716", 835, "Bantam", 4.3, 24100,
        "On the continent of Westeros, the great houses fight over the Iron Throne while "
        "an ancient threat awakens in the north.",
    ),
    (
        "hunger-games", "The Hunger Games", ("Suzanne Collins",), 2008,
        (GENRE_DYSTOPIA, GENRE_YOUTH), "9780439023528", 374, "Scholastic", 4.1, 28000,
        "In a country divided into districts, Katniss volunteers for a deadly televised game "
        "imposed by the Capitol. Surviving also means keeping your humanity.",
    ),
    (
        "harry-potter-1", "Harry Potter à l'école des sorciers", ("J.K. Rowling",), 1997,
        (GENRE_FANTASY, GENRE_YOUTH), "9782070518425", 308, "Gallimard Jeunesse", 4.5, 31200,
        "On his eleventh birthday, Harry learns he is a wizard and enters Hogwarts, where "
        "friendship, mysteries and a past he never knew await him.",
    ),
    (
        "neuromancer", "Neuromancer", ("William Gibson",), 1984, (GENRE_SF,),
        "9780441569595", 271, "Ace", 3.9, 7600,
        "Case, a washed-up hacker, is recruited for one last job in the matrix. "
        "The foundational novel of cyberpunk.",
    ),
    (
        "foundation", "Foundation", ("Isaac Asimov",), 1951, (GENRE_SF,),
        "9780553293357", 255, "Bantam Spectra", 4.2, 10300,
        "As the Galactic Empire collapses, a mathematician sets in motion a plan to "
        "shorten the coming centuries of chaos.",
    ),
    (
        "left-hand-of-darkness", "The Left Hand of Darkness", ("Ursula K. Le Guin",), 1969,
        (GENRE_SF,), "9780441478125", 304, "Ace", 4.1, 6400,
        "An envoy from Earth visits an icy planet whose inhabitants have no fixed gender. "
        "A reflection on otherness, loyalty and friendship.",
    ),
    (
        "martian", "The Martian", ("Andy Weir",), 2011, (GENRE_SF,),
        "9780553418026", 369, "Broadway Books", 4.4, 17900,
        "Alone on Mars after an accident, astronaut Mark Watney must rely on his "
        "resourcefulness and humor to survive until rescue.",
    ),
    (
        "project-hail-mary", "Project Hail Mary", ("Andy Weir",), 2021, (GENRE_SF,),
        "9780593135204", 476, "Ballantine Books", 4.6, 15200,
        "A teacher wakes up alone on a spaceship with no memory of his mission: save "
        "the Earth from a threat coming from the Sun.",
    ),
    (
        "pride-and-prejudice", "Pride and Prejudice", ("Jane Austen",), 1813,
        (GENRE_CLASSICS,), "9780141439518", 480, "Penguin Classics", 4.3, 21500,
        "Elizabeth Bennet and the proud Mr. Darcy: a push and pull of prejudice, irony and "
        "feelings in early nineteenth-century England.",
    ),
    (
        "jane-eyre", "Jane Eyre", ("Charlotte Brontë",), 1847, (GENRE_CLASSICS,),
        "9780141441146", 532, "Penguin Classics", 4.1, 11200,
        "A proud-spirited orphan, Jane becomes a governess at Thornfield Hall, where its "
        "master hides a heavy secret.",
    ),
    (
        "frankenstein", "Frankenstein", ("Mary Shelley",), 1818, (GENRE_CLASSICS, GENRE_SF),
        "9780141439471", 288, "Penguin Classics", 3.9, 10100,
        "Young Victor Frankenstein gives life to a creature he immediately abandons. A "
        "gothic tale about the creator's responsibility.",
    ),
    (
        "dracula", "Dracula", ("Bram Stoker",), 1897, (GENRE_CLASSICS,),
        "9780141439846", 488, "Penguin Classics", 4.0, 9300,
        "A young clerk travels to Transylvania to visit an enigmatic count. The novel that set "
        "the myth of the modern vampire.",
    ),
    (
        "great-gatsby", "The Great Gatsby", ("F. Scott Fitzgerald",), 1925, (GENRE_CLASSICS,),
        "9780743273565", 180, "Scribner", 3.9, 24600,
        "In Jazz Age America, a mysterious neighbor throws lavish parties "
        "to win back a lost love.",
    ),
    (
        "to-kill-a-mockingbird", "To Kill a Mockingbird", ("Harper Lee",), 1960,
        (GENRE_CLASSICS,), "9780061120084", 336, "Harper Perennial", 4.3, 27300,
        "In the American South of the 1930s, a little girl watches the trial of a "
        "Black man unjustly accused, defended by her father, a lawyer.",
    ),
    (
        "etranger", "L'Étranger", ("Albert Camus",), 1942, (GENRE_CLASSICS,),
        "9782070360024", 186, "Gallimard", 4.0, 15600,
        "Meursault buries his mother without tears, then commits an act that leads him before a "
        "court. A novel of the absurd, dry and luminous.",
    ),
    (
        "la-peste", "La Peste", ("Albert Camus",), 1947, (GENRE_CLASSICS,),
        "9782070360420", 336, "Gallimard", 4.1, 9100,
        "Oran is struck by a plague epidemic. A doctor and his companions each face "
        "this scourge in their own way.",
    ),
    (
        "hundred-years-of-solitude", "One Hundred Years of Solitude",
        ("Gabriel García Márquez",), 1967, (GENRE_CLASSICS,), "9780060883287", 417,
        "Harper Perennial", 4.1, 13900,
        "The story of the Buendía family and the imaginary village of Macondo, between the marvelous, "
        "solitude and the cycles of history.",
    ),
    (
        "alchemist", "The Alchemist", ("Paulo Coelho",), 1988, (GENRE_CONTEMPORARY,),
        "9780062315007", 208, "HarperOne", 3.9, 21800,
        "A young Andalusian shepherd sets off for the pyramids in search of a treasure and discovers "
        "his own personal legend.",
    ),
    (
        "gone-girl", "Gone Girl", ("Gillian Flynn",), 2012, (GENRE_CRIME,),
        "9780307588371", 415, "Crown", 4.1, 18900,
        "On their wedding anniversary, Amy disappears. Suspicion falls on her "
        "husband. A psychological thriller full of twists.",
    ),
    (
        "dragon-tattoo", "The Girl with the Dragon Tattoo", ("Stieg Larsson",), 2005,
        (GENRE_CRIME,), "9780307949486", 644, "Vintage Crime", 4.1, 14800,
        "A journalist and an extraordinary hacker investigate the disappearance, forty years "
        "earlier, of the heiress of a great industrial family.",
    ),
    (
        "and-then-there-were-none", "And Then There Were None", ("Agatha Christie",), 1939,
        (GENRE_CRIME, GENRE_CLASSICS), "9780062073488", 272, "William Morrow", 4.3, 17200,
        "Ten strangers are invited to an isolated island. One by one, they die following a "
        "macabre nursery rhyme. The definitive locked-room mystery.",
    ),
    (
        "orient-express", "Murder on the Orient Express", ("Agatha Christie",), 1934,
        (GENRE_CRIME,), "9780062693662", 288, "William Morrow", 4.2, 14100,
        "Snowbound, the luxury train sees a passenger murdered. Hercule Poirot must "
        "untangle the lies of every traveler.",
    ),
    (
        "midnight-library", "The Midnight Library", ("Matt Haig",), 2020, (GENRE_CONTEMPORARY,),
        "9780525559474", 304, "Viking", 4.0, 12600,
        "Between life and death, Nora discovers a library where every book is a life "
        "she could have lived.",
    ),
    (
        "circe", "Circe", ("Madeline Miller",), 2018, (GENRE_FANTASY, GENRE_CONTEMPORARY),
        "9780316556347", 393, "Little, Brown", 4.3, 11800,
        "The nymph Circe, banished to an island, learns witchcraft and crosses paths with figures of "
        "Greek mythology. An odyssey seen through the eyes of the one who gets forgotten.",
    ),
    (
        "normal-people", "Normal People", ("Sally Rooney",), 2018, (GENRE_CONTEMPORARY,),
        "9781984822178", 266, "Hogarth", 3.8, 9200,
        "Marianne and Connell, in high school and then at university, keep drifting together and apart. "
        "A story of love and social class.",
    ),
    (
        "sapiens", "Sapiens", ("Yuval Noah Harari",), 2011, (GENRE_ESSAYS,),
        "9780062316097", 464, "Harper", 4.4, 18300,
        "A history of humankind, from hunter-gatherers to our digital societies, that "
        "questions our collective beliefs.",
    ),
    (
        "educated", "Educated", ("Tara Westover",), 2018, (GENRE_ESSAYS,),
        "9780399590504", 352, "Random House", 4.5, 15500,
        "Raised in a survivalist family, Tara doesn't set foot in a classroom until she is seventeen. A "
        "memoir of emancipation through education.",
    ),
    (
        "atomic-habits", "Atomic Habits", ("James Clear",), 2018, (GENRE_ESSAYS,),
        "9780735211292", 320, "Avery", 4.4, 21400,
        "A practical method for building good habits and breaking bad ones "
        "through small, repeated changes.",
    ),
    (
        "catcher-in-the-rye", "The Catcher in the Rye", ("J.D. Salinger",), 1951,
        (GENRE_CLASSICS,), "9780316769488", 277, "Little, Brown", 3.8, 15100,
        "A few days of wandering through New York for Holden Caulfield, a teenager in revolt against the "
        "world of adults.",
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
    "Devourer of science fiction and classics. Always three books in progress, "
    "and a to-read pile that never shrinks."
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
        "A book that never ages. The ending left me speechless for several days: "
        "worth rereading every five years to see what has changed around us.",
    ),
    "petit-prince": (
        "I read it as a child and understood nothing. As an adult, every page hits home. "
        "Short, but you don't close it unscathed.",
    ),
    "pride-and-prejudice": (
        "The dialogue is incredibly sharp and Austen's irony hasn't aged a day. "
        "Darcy remains insufferable and then irresistible, as expected.",
    ),
    "martian": (
        "Efficient, funny and surprisingly educational. I read the last hundred pages in "
        "one sitting, on a Sunday.",
    ),
    "game-of-thrones": (
        "An impressive world, but too many characters for me at that point. "
        "I may try again later.",
    ),
}

_FRIENDS = [
    Person("lea_p", 11, "Crime fiction reader, black tea and blankets."),
    Person("marc.lit", 12, "One novel a week, no exceptions."),
    Person("ines.reads", 13, "Fantasy, SF and reading journals."),
    Person("thomas_b", 14, "Classics first, everything else after."),
    Person("nora_pages", 15, "I rate everything. Absolutely everything."),
    Person("julien.k", 16, "Essays, history, a bit of comics."),
]

_ME = Person(DEMO_USERNAME, DEMO_USER_ID, DEMO_BIO)
PEOPLE: dict[int, Person] = {p.user_id: p for p in [_ME, *_FRIENDS]}
_BY_USERNAME = {p.username: p for p in PEOPLE.values()}

# who follows whom (usernames): the followers lists are derived from this, so they stay consistent
_FOLLOWS = {
    "camille.demo": {"lea_p", "marc.lit", "ines.reads", "julien.k"},
    "lea_p": {"camille.demo", "thomas_b", "nora_pages"},
    "marc.lit": {"ines.reads", "julien.k"},
    "ines.reads": {"camille.demo", "marc.lit", "nora_pages"},
    "thomas_b": {"camille.demo", "lea_p"},
    "nora_pages": {"camille.demo", "lea_p", "julien.k", "ines.reads"},
    "julien.k": {"marc.lit", "thomas_b"},
}

_FRIEND_SINCE = {
    "lea_p": date(2025, 1, 20),
    "marc.lit": date(2024, 11, 5),
    "ines.reads": date(2025, 2, 9),
    "thomas_b": date(2024, 9, 14),
    "nora_pages": date(2025, 5, 30),
    "julien.k": date(2025, 7, 2),
}

# Books of the fictitious readers besides the ones they reviewed (those are always "read"):
# username -> [(slug, status, date_added, date_read, rating)]
_FRIEND_EXTRAS = {
    "lea_p": [
        ("dragon-tattoo", "read", date(2026, 2, 1), date(2026, 2, 12), 4),
        ("orient-express", "read", date(2026, 4, 3), date(2026, 4, 8), 5),
        ("and-then-there-were-none", "to read", date(2026, 8, 2), None, None),
        ("dracula", "in progress", date(2026, 9, 20), None, None),
        ("la-peste", "abandoned", date(2025, 10, 5), date(2025, 10, 30), 2),
    ],
    "marc.lit": [
        ("atomic-habits", "read", date(2026, 1, 3), date(2026, 1, 20), 4),
        ("hobbit", "read", date(2025, 12, 1), date(2025, 12, 14), 5),
        ("foundation", "in progress", date(2026, 9, 12), None, None),
        ("neuromancer", "to read", date(2026, 8, 18), None, None),
    ],
    "ines.reads": [
        ("mistborn", "read", date(2026, 1, 15), date(2026, 2, 20), 5),
        ("harry-potter-1", "read", date(2025, 11, 1), date(2025, 11, 9), 5),
        ("fahrenheit-451", "in progress", date(2026, 10, 2), None, None),
        ("left-hand-of-darkness", "to read", date(2026, 7, 22), None, None),
        ("game-of-thrones", "abandoned", date(2025, 6, 1), date(2025, 6, 28), 2),
    ],
    "thomas_b": [
        ("la-peste", "read", date(2026, 2, 3), date(2026, 2, 17), 4),
        ("great-gatsby", "read", date(2025, 10, 11), date(2025, 10, 15), 3),
        ("jane-eyre", "in progress", date(2026, 9, 25), None, None),
        ("brave-new-world", "to read", date(2026, 8, 30), None, None),
        ("catcher-in-the-rye", "abandoned", date(2025, 8, 12), date(2025, 8, 25), 2),
    ],
    "nora_pages": [
        ("normal-people", "read", date(2026, 3, 1), date(2026, 3, 11), 4),
        ("hunger-games", "read", date(2025, 12, 20), date(2025, 12, 28), 3),
        ("atomic-habits", "in progress", date(2026, 9, 29), None, None),
        ("educated", "to read", date(2026, 7, 9), None, None),
        ("hundred-years-of-solitude", "abandoned", date(2025, 9, 1), date(2025, 9, 30), 2),
    ],
    "julien.k": [
        ("educated", "read", date(2026, 2, 8), date(2026, 3, 1), 5),
        ("atomic-habits", "read", date(2025, 12, 5), date(2025, 12, 22), 4),
        ("dracula", "in progress", date(2026, 9, 18), None, None),
        ("frankenstein", "to read", date(2026, 8, 7), None, None),
        ("alchemist", "abandoned", date(2025, 7, 7), date(2025, 7, 20), 2),
    ],
}

# Reviews by other (fictional) readers: slug -> [(author, rating, text, likes, date)]
_OTHER_REVIEWS = {
    "dune": [
        ("ines.reads", 5, "Total immersion. The world is so dense you come out dazzled and "
         "a little lost, in the best way.", 24, date(2026, 5, 2)),
        ("marc.lit", 4, "Slow to start, impossible to put down after that. The passages on "
         "ecology are brilliant.", 11, date(2026, 3, 18)),
    ],
    "1984": [
        ("thomas_b", 5, "Essential. Newspeak is the most terrifying idea in "
         "twentieth-century literature.", 31, date(2026, 1, 9)),
        ("lea_p", 4, "Dark, of course, but with a clarity that hurts.", 8, date(2025, 11, 4)),
    ],
    "project-hail-mary": [
        ("nora_pages", 5, "My book of the year. I won't say more so as not to spoil "
         "the joy of discovery.", 42, date(2026, 6, 21)),
        ("julien.k", 5, "Funny, moving, smart. A real lesson in friendship.", 17,
         date(2026, 7, 1)),
    ],
    "pride-and-prejudice": [
        ("lea_p", 5, "Every reread reveals a new touch of humor.", 14,
         date(2026, 2, 12)),
        ("thomas_b", 4, "A monument, but above all a really good read.", 6,
         date(2025, 12, 2)),
    ],
    "circe": [
        ("ines.reads", 5, "Sensual, patient writing. I went back to my old mythology "
         "textbook right after.", 19, date(2026, 4, 8)),
        ("nora_pages", 4, "Beautiful, a bit long in the middle but so well carried.", 5,
         date(2026, 4, 30)),
    ],
    "martian": [
        ("marc.lit", 5, "Suspense with equations. Who would have thought?", 13, date(2025, 10, 7)),
        ("julien.k", 4, "Very entertaining. The hero's sarcastic tone is perfect.", 4,
         date(2025, 12, 28)),
    ],
    "etranger": [
        ("thomas_b", 4, "Short and unsettling. The beach remains one of the strangest "
         "scenes I have ever read.", 9, date(2026, 3, 3)),
    ],
    "gone-girl": [
        ("lea_p", 4, "The twists are well crafted, the atmosphere chilling.", 10,
         date(2025, 9, 14)),
        ("nora_pages", 3, "Effective but I didn't like a single character, which was surely "
         "intentional.", 3, date(2025, 10, 1)),
    ],
    "sapiens": [
        ("julien.k", 5, "It makes you want to reread history differently. A few "
         "shortcuts, but very stimulating.", 22, date(2026, 2, 2)),
    ],
    "name-of-the-wind": [
        ("ines.reads", 5, "The music of the prose, plain and simple.", 27, date(2026, 5, 22)),
        ("marc.lit", 4, "A masterful opening. Can't wait for the sequel... someday.", 12,
         date(2026, 6, 9)),
    ],
    "hobbit": [
        ("thomas_b", 5, "Perfect for getting into fantasy, a comfort read.", 15,
         date(2026, 1, 26)),
    ],
    "foundation": [
        ("julien.k", 4, "Brilliant ideas, characters a bit in the background. Still "
         "very good.", 7, date(2026, 4, 14)),
    ],
    "midnight-library": [
        ("nora_pages", 4, "Gentle and comforting, perfect for a gray day.", 9,
         date(2026, 2, 19)),
    ],
    "educated": [
        ("lea_p", 5, "Heartbreaking and very well told. I have gifted it three times.", 18,
         date(2026, 3, 27)),
    ],
}


REVIEWED_SLUGS = tuple(_OTHER_REVIEWS)


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
            author_id=DEMO_USER_ID,
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
            author_id=_BY_USERNAME[author].user_id,
        )
        for author, rating, text, likes, created in items
    ]


def person(user_id: int) -> Person | None:
    return PEOPLE.get(user_id)


def initial_following() -> set[int]:
    """User ids followed by the demo user at the start of a session."""
    return {_BY_USERNAME[u].user_id for u in _FOLLOWS[DEMO_USERNAME]}


def _following_usernames(user_id: int, my_following: set[int]) -> set[str]:
    if user_id == DEMO_USER_ID:
        return {PEOPLE[i].username for i in my_following if i in PEOPLE}
    return _FOLLOWS.get(PEOPLE[user_id].username, set())


def followers_of(user_id: int, my_following: set[int]) -> tuple[Person, ...]:
    name = PEOPLE[user_id].username
    return tuple(
        p for p in PEOPLE.values() if name in _following_usernames(p.user_id, my_following)
    )


def following_of(user_id: int, my_following: set[int]) -> tuple[Person, ...]:
    return tuple(_BY_USERNAME[n] for n in sorted(_following_usernames(user_id, my_following)))


def user_profile(user_id: int, my_following: set[int]) -> Profile | None:
    """Public profile of a demo user (the demo user included); None if unknown."""
    p = PEOPLE.get(user_id)
    if p is None:
        return None
    is_me = user_id == DEMO_USER_ID
    return Profile(
        user_id=user_id,
        username=p.username,
        display_name=DEMO_DISPLAY_NAME if is_me else p.username,
        bio=p.bio,
        member_since=DEMO_MEMBER_SINCE if is_me else _FRIEND_SINCE[p.username],
        followers=followers_of(user_id, my_following),
        following=following_of(user_id, my_following),
    )


def reviews_by_author(user_id: int) -> list[Review]:
    """Reviews written by a fictitious reader (the demo user's own are kept in the session)."""
    p = PEOPLE.get(user_id)
    if p is None or user_id == DEMO_USER_ID:
        return []
    catalog = books()
    found = []
    for slug in _OTHER_REVIEWS:
        for review in other_reviews(wid(slug)):
            if review.author_id == user_id:
                found.append(replace(review, book_title=catalog[review.work_id].title))
    return sorted(found, key=lambda r: r.created or date.min, reverse=True)


def user_library(user_id: int) -> list[LibraryEntry]:
    """Library of a fictitious reader: the books they reviewed (read) plus a few others."""
    p = PEOPLE.get(user_id)
    if p is None or user_id == DEMO_USER_ID:
        return []
    catalog = books()
    entries: dict[str, LibraryEntry] = {}
    for n, review in enumerate(reviews_by_author(user_id), start=1):
        entries[review.work_id] = LibraryEntry(
            reading_id=user_id * 100 + n,
            book=catalog[review.work_id],
            status="read",
            date_added=(review.created or date(2026, 1, 1)) - timedelta(days=14),
            date_read=review.created,
            rating=review.rating,
        )
    for n, (slug, status, added, read_on, rating) in enumerate(
        _FRIEND_EXTRAS.get(p.username, []), start=50
    ):
        work_id = wid(slug)
        if work_id not in entries:
            entries[work_id] = LibraryEntry(
                user_id * 100 + n, catalog[work_id], status, added, read_on, rating
            )
    return sorted(entries.values(), key=lambda e: e.date_added, reverse=True)


def demo_profile() -> Profile:
    return user_profile(DEMO_USER_ID, initial_following())
