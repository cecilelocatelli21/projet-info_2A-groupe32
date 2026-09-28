INSERT INTO player(username, password, elo, email, pokemon_fan) VALUES
('admin',     '0000',  null,  'admin@project.io',     null),
('a',         'a',     1200,  'a@ensai.fr',           true),
('maurice',   '1234',  1000,  'maurice@ensai.fr',     true),
('batricia',  '9876',  1500,  'bat@project.io',       false),
('miguel',    'abcd',  1300,  'miguel@project.io',    true),
('gilbert',   'toto',  1100,  'gilbert@project.io',   false),
('junior',    'aaaa',  1200,  'junior@project.io',    true);

INSERT INTO book(work_id, title, authors) VALUES
('OL10263W', 'le petit prince', 'Antoine de Saint-Exupéry'),
('OL30053009W', 'Du côté de chez Swann', 'Marcel Proust'),
('OL29549062W', 'À l''ombre des jeunes filles en fleurs', 'Marcel Proust');

INSERT INTO user_table(username, email, password_hash) VALUES
('Moussa', 'moussa.soulama@eleve.ensai.fr', '1234'),
('Cécile', 'cecile.locatelli@eleve.ensai.fr', '1234'),
('Paul', 'paul.fourcade@eleve.ensai.fr', '1234'),
('Axel', 'axel.leclercq@eleve.ensai.fr', '1234'),
('Anne-Camille', 'anne-camille.tampe@eleve.ensai.fr', '1234'),
('Arnaud', 'arnaud.bichon@eleve.ensai.fr', '1234');