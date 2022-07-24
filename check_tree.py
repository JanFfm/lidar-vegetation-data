"""
This is a script to categorize tree species 
into four cathegories: 
Species that are very well adapted to dryness, 
those that are well adjusted to a dry location,
those that are moderately well adapted to dryness, 
and those that are unfit for dry locations.
First species name in latin, followd by species name in german. 
As always, very open for additions :)
"""

# list of all trees that cause no danger (not more than usual)
very_well_adapted_dryness = ["Acer campestre", "Feldarhorn", "Acer platanoides", "Spitzahorn", "Betula pendula", "Hängebirke", "Carpinus betulus", "Hainbuche",
    "Pinus nigra", "Schwarzkiefer", "Pinus strobus", "Strobe", "Weymouth-Kiefer", "Pinus sylvestris", "Waldkiefer", "Populus tremula", "Espe", "Zitterpappel", "Aspe",
    "Prunus avium", "Vogelkirsche", "Quercus petraea", "Traubeneiche","Robinia pseudoacacia","Robinie","Weiße Robinie", "Sorbus aria", "Mehlbeere", 
    "Sorbus domestica", "Speierling", "Sorbus torminalis", "Elsbeere", "Tilia cordata", "Winterlinde", "Föhre"]

# list of all trees that cause a little danger
well_adapted_dryness = ["Abies grandis", "Küstentanne", "Acer pseudoplatanus","Bergahorn", "Buxus sempervirens", "Buchsbaum", "Castanea sativa", "Edelkastanie", 
    "Fraxinus ornus","Manna-Esche", "Juglans regia", "Echte Walnuss", "Walnuss", "Larix decidua", "Lärche", "Malus sylvestris", "Holzapfel", 
    "Pyrus pyraster", "Waldbirne", "Quercus cerris",  "Zerreiche","Quercus pubescens", "Flaumeiche", "Quercus robur", "Stieleiche", "Roteiche", "Lamiales", 
    "Quercus rubra", "Sorbus aucuparia", "Vogelbeere", "Taxus baccata", "Europäische Eibe",  
        "Tilia platyphyllos", "Sommerlinde", "Ulmus glabra" "Bergulme", "Quercus", "Eiche","Acer", "Ahorn", "Kirsche", "Pflaume","Kirschbaum", 3, "Ginkgoopsida", "Birke", 
         1, "Magnoliopsida", "Bedecktsamer", "Lignum deciduum", 
        "Rosales"]

# list of trees that cause danger 
moderately_well_adapted_dryness = ["Alnus incana", "Grauerle", "Betula pubescens", "Moorbirke", "Fagus sylvatica", "Rotbuche", 
    "Fraxinus excelsior", "Gemeine Esche", "Ilex aquifolium", "Europäische Stechpalme",  "Pinus cembra","Zirbelkiefer", "Prunus padus", "Traubenkirsche",
    "Pseudotsuga menziesii", "Gewöhnliche Doiuglasie", "Douglasie", "Ulmus laevis", "Flatterulme", "Ulmus minor", "Feldulme", 2, "Coniferopsida","Coniferales", "Rosskastanien"]

# list of trees that cause most danger 
not_adapted_dryness = ["Abies alba", "Weißtanne", "Alnus glutinosa", "Schwarzerle", "Picea abies", "Gemeine Fichte", "Fichte", 
"Populus nigra", "Schwarz-Pappel", "Salix alba", "Silberweide", "Tanne"]

