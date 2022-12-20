sky_condition_levels = [
    {
        "name": "jasno (obloha úplne bez oblačnosti)",
        "code": 1,
        "descriptive_words": ["jasno", "jas"],
    },
    {
        "name": "polojasno (veľká väčšina oblohy bez oblačnosti)",
        "code": 2,
        "descriptive_words": ["polojasno", "polojas"],
    },
    {
        "name": "polooblačno (asi polovica oblohy je pokrytá oblačnosťou)",
        "code": 3,
        "descriptive_words": ["polooblacno", "polooblac"],
    },
    {
        "name": "oblačno (väčšina oblohy je pokrytá oblačnosťou)",
        "code": 4,
        "descriptive_words": ["oblacno", "oblac"],
    },
    {
        "name": "zamračené (obloha je úplne pokrytá oblačnosťou)",
        "code": 5,
        "descriptive_words": ["zamracene", "zamrac"],
    },
    {
        "name": "hmla / zamračené nízkou inverznou oblačnosťou (na horách jasno)",
        "code": 6,
        "descriptive_words": ["hmla", "inverzia"],
    },
]

wind_levels = [
    {"name": "bezvetrie", "code": 1, "descriptive_words": ["bezvetrie", "bezv", "bwzv"]},
    {
        "name": "slabý vietor (vietor pohybuje iba listami na stromoch, ale nie konármi)",
        "code": 2,
        "descriptive_words": ["listy", "slaby vietor"],
    },
    {
        "name": "mierny vietor (vietor už pohybuje aj konármi stromov)",
        "code": 3,
        "descriptive_words": ["konare", "mierny vietor"],
    },
    {
        "name": "silný vietor (vietor pohybuje celým stromom, môže dochádzať k odlamovaniu konárov)",
        "code": 4,
        "descriptive_words": ["stromy", "silny vietor"],
    },
    {
        "name": "víchrica (na stromoch sa odlamujú veľké konáre, alebo sa vyvracajú celé stromy)",
        "code": 5,
        "descriptive_words": ["vichrica"],
    },
]

observation_characteristics = [
    {"name": "A0 - výskyt od 1.4. do 31.7.", "code": "19"},
    {"name": "B1 - vhodné prostredie v hniezdnej dobe", "code": "21"},
    {"name": "B2 - spievajúci samec", "code": "22"},
    {"name": "C3 - pár v hniezdnej dobe", "code": "23"},
    {"name": "C4 - opakované teritoriálne správanie", "code": "24"},
    {"name": "C5 - tok, imponovanie, párenie", "code": "25"},
    {"name": "C6 - hľadanie hniezdísk", "code": "26"},
    {"name": "C7 - varovné hlasy", "code": "27"},
    {"name": "C8 - hniezdne lysiny", "code": "28"},
    {"name": "C9 - stavba hniezda", "code": "29"},
    {"name": "D10 - odvádzanie pozornosti od hniezda", "code": "31"},
    {"name": "D11 - nález použitého hniezda alebo škrupín", "code": "1"},
    {"name": "D12 - vylietané mladé, resp. v prachovom perí", "code": "2"},
    {"name": "D13 - prílety na hniezdisko, sedenie na hniezde", "code": "3"},
    {"name": "D14 - prinášanie potravy, odnos trusu", "code": "4"},
    {"name": "D15 - hniezdo s násadou", "code": "5"},
    {"name": "D16 - hniezdo s mláďatami", "code": "6"},
    {"name": "M_MV - migrácia alebo výskyt v mimohniezdnom období", "code": "36"},
    {"name": "MUMIA - múmia", "code": "35"},
    {"name": "NEGAT - negatívny výsledok cielenej kontroly", "code": "37"},
    {"name": "NOCOVISKO - na nocovisku", "code": "38"},
    {"name": "ODCHYT - chytenie živého alebo usmrteného jedinca", "code": "40"},
    {"name": "SKELET TRUS - skelet v truse", "code": "47"},
    {"name": "SKELET VYVRZOK - skelet vo vývržku", "code": "48"},
    {"name": "STERNUM - určenie podľa prsnej kosti", "code": "50"},
    {"name": "UHYN - uhynutý jedinec", "code": "58"},
    {"name": "UHYN EL VEDENIE - živočích usmrtený elektrickým vedením", "code": "59"},
    {"name": "UHYN NA CESTE - živočích usmrtený na ceste", "code": "60"},
    {"name": "VYVRZOK - nález vývržku vtáka", "code": "66"},
    {"name": "ZASTREL - usmrtenie strelnou zbraňou", "code": "67"},
    {"name": "ZIMOVANIE - zimovanie", "code": "70"},
    {"name": "FOTOPASCA - Druh bol odfotený fotopascou", "code": "73"}
]

observation_methods = [
    {"name": "ODCHYT - chytenie živého alebo usmrteného jedinca", "code": "2"},
    {"name": "SKELET TRUS - skelet v truse", "code": "5"},
    {"name": "SKELET VYVRZOK - skelet vo vývržku", "code": "6"},
    {"name": "ZASTREL - usmrtenie strelnou zbraňou", "code": "10"},
    {"name": "STOPOVANIE - stopovanie živočícha", "code": "13"},
    {"name": "FOTOPASCA - Druh bol odfotený fotopascou", "code": "14"},
    {"name": "AKUSTICKY MONITORING - akustický monitoring", "code": "15"},
    {"name": "VIZUAL - vizuálne pozorovanie", "code": "8"},
]

temperature_levels = [
    {"name": "35 – 40°C", "code": "8", "range": [35, 40]},
    {"name": "30 – 35°C", "code": "7", "range": [30, 35]},
    {"name": "25 – 30°C", "code": "6", "range": [25, 30]},
    {"name": "20 – 25°C", "code": "5", "range": [20, 25]},
    {"name": "15 – 20°C", "code": "4", "range": [15, 20]},
    {"name": "10 – 15°C", "code": "3", "range": [10, 15]},
    {"name": "5 – 10°C", "code": "2", "range": [5, 10]},
    {"name": "0 – 5°C", "code": "1", "range": [0, 5]},
    {"name": "0 – -5°C", "code": "14", "range": [0, -5]},
    {"name": "-5 – -10°C", "code": "13", "range": [-5, -10]},
    {"name": "-10 – -15°C", "code": "12", "range": [-10, -15]},
    {"name": "-15 – -20°C", "code": "11", "range": [-15, -20]},
    {"name": "-20 – -25°C", "code": "10", "range": [-20, -25]},
    {"name": "-25 – -30°C", "code": "9", "range": [-25, -30]},
]

genera = {
    "slovak": [
        "bažant",
        "belorítka",
        "bernikla",
        "bocian",
        "brehuľa",
        "brehár",
        "brhlík",
        "bučiak",
        "bučiačik",
        "chavkoš",
        "chochlačka",
        "chochláč",
        "chrapkáč",
        "chriašteľ",
        "cíbik",
        "drop",
        "drozd",
        "dudok",
        "dážďovník",
        "fúzatka",
        "glezg",
        "hadiar",
        "haja",
        "havran",
        "hlaholka",
        "holub",
        "hrdlička",
        "hrdzavka",
        "hus",
        "hvizdák",
        "húska",
        "hýľ",
        "ibis",
        "jarabica",
        "jariabok",
        "jastrab",
        "kajka",
        "kalužiak",
        "kamenár",
        "kanárik",
        "kavka",
        "kazarka",
        "kačica",
        "kaňa",
        "kolibkárik",
        "kormorán",
        "krahuľa",
        "krakľa",
        "krivonos",
        "krkavec",
        "krutihlav",
        "králiček",
        "kršiak",
        "kukavica",
        "kukučka",
        "kulík",
        "kuvik",
        "kuvičok",
        "kôrovník",
        "kúdelníčka",
        "labuť",
        "lastovička",
        "lastúrničiar",
        "lelek",
        "ležiak",
        "lyska",
        "lyskonoh",
        "lyžičiar",
        "mlynárka",
        "močiarnica",
        "muchár",
        "muchárik",
        "murárik",
        "myšiak",
        "myšiarka",
        "orešnica",
        "oriešok",
        "orliak",
        "orol",
        "pelikán",
        "penica",
        "pinka",
        "pipíška",
        "plameniak",
        "plamienka",
        "pobrežník",
        "pomorník",
        "potápač",
        "potápka",
        "potáplica",
        "potápnica",
        "prepelica",
        "prieložník",
        "pôtik",
        "pŕhľaviar",
        "rybár",
        "rybárik",
        "sedmohlások",
        "skaliar",
        "skaliarik",
        "sliepočka",
        "sluka",
        "slávik",
        "snehárka",
        "sojka",
        "sokol",
        "sova",
        "stehlík",
        "stepiar",
        "straka",
        "strakoš",
        "strnádka",
        "sup",
        "svrčiak",
        "sýkorka",
        "tesár",
        "tetrov",
        "trasochvost",
        "trsteniarik",
        "turpan",
        "vlha",
        "vodnár",
        "volavka",
        "vrabec",
        "vrana",
        "vrchárka",
        "výr",
        "výrik",
        "včelár",
        "včelárik",
        "čajka",
        "čaplička",
        "čavka",
        "čorík",
        "ďateľ",
        "ľabtuška",
        "šabliarka",
        "šišila",
        "škorec",
        "škovránok",
        "žeriav",
        "žlna",
        "žltochvost",
    ],
    "latin": [
        "Accipiter",
        "Acrocephalus",
        "Actitis",
        "Aegithalos",
        "Aegolius",
        "Aegypius",
        "Alauda",
        "Alcedo",
        "Alopochen",
        "Anas",
        "Anser",
        "Anthropoides",
        "Anthus",
        "Apus",
        "Aquila",
        "Ardea",
        "Ardeola",
        "Arenaria",
        "Asio",
        "Athene",
        "Aythya",
        "Bombycilla",
        "Bonasa",
        "Botaurus",
        "Branta",
        "Bubo",
        "Bubulcus",
        "Bucephala",
        "Burhinus",
        "Buteo",
        "Calandrella",
        "Calcarius",
        "Calidris",
        "Caprimulgus",
        "Carduelis",
        "Carpodacus",
        "Certhia",
        "Charadrius",
        "Chettusia",
        "Chlamydotis",
        "Chlidonias",
        "Ciconia",
        "Cinclus",
        "Circaetus",
        "Circus",
        "Clamator",
        "Clangula",
        "Coccothraustes",
        "Columba",
        "Coracias",
        "Corvus",
        "Coturnix",
        "Crex",
        "Cuculus",
        "Cygnus",
        "Delichon",
        "Dendrocopos",
        "Dryocopus",
        "Egretta",
        "Emberiza",
        "Eremophila",
        "Erithacus",
        "Falco",
        "Ficedula",
        "Fringilla",
        "Fulica",
        "Galerida",
        "Gallinago",
        "Gallinula",
        "Garrulus",
        "Gavia",
        "Gelochelidon",
        "Glareola",
        "Glaucidium",
        "Grus",
        "Gyps",
        "Haematopus",
        "Haliaeetus",
        "Hieraaetus",
        "Himantopus",
        "Hippolais",
        "Hirundo",
        "Histrionicus",
        "Ixobrychus",
        "Jynx",
        "Lanius",
        "Larus",
        "Limicola",
        "Limosa",
        "Locustella",
        "Loxia",
        "Lullula",
        "Luscinia",
        "Lymnocryptes",
        "Melanitta",
        "Mergellus",
        "Mergus",
        "Merops",
        "Milvus",
        "Monticola",
        "Montifringilla",
        "Motacilla",
        "Muscicapa",
        "Neophron",
        "Netta",
        "Nucifraga",
        "Numenius",
        "Nyctea",
        "Nycticorax",
        "Oenanthe",
        "Oriolus",
        "Otis",
        "Otus",
        "Oxyura",
        "Pandion",
        "Panurus",
        "Parus",
        "Passer",
        "Pelecanus",
        "Perdix",
        "Perisoreus",
        "Pernis",
        "Phalacrocorax",
        "Phalaropus",
        "Phasianus",
        "Philomachus",
        "Phoenicopterus",
        "Phoenicurus",
        "Phylloscopus",
        "Pica",
        "Picoides",
        "Picus",
        "Pinicola",
        "Platalea",
        "Plectrophenax",
        "Plegadis",
        "Pluvialis",
        "Podiceps",
        "Porzana",
        "Prunella",
        "Pyrrhocorax",
        "Pyrrhula",
        "Rallus",
        "Recurvirostra",
        "Regulus",
        "Remiz",
        "Riparia",
        "Rissa",
        "Saxicola",
        "Scolopax",
        "Serinus",
        "Sitta",
        "Somateria",
        "Stercorarius",
        "Sterna",
        "Streptopelia",
        "Strix",
        "Sturnus",
        "Surnia",
        "Sylvia",
        "Syrrhaptes",
        "Tachybaptus",
        "Tadorna",
        "Tetrao",
        "Tetrax",
        "Tichodroma",
        "Tringa",
        "Troglodytes",
        "Turdus",
        "Tyto",
        "Upupa",
        "Vanellus",
        "Xenus",
    ],
}
