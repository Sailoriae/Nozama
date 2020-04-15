#coding: utf-8

"""
ETAPE 1 : Définition des objets
"""

# Objet représentant une alternative à Amazon
class Alternative :
    def __init__ ( self, nom, URL, ID_cat, desc ) :
        self.nom = nom
        self.URL = URL
        self.ID_cat = ID_cat
        self.desc = desc


# Objet représentant une catégorie, qui contient un tableau d'objets Alternative
class Categorie :
    def __init__ ( self, nom, ID ) :
        self.nom = nom
        self.ID = ID
        self.alternatives = [] # Tableau contenant des objets Alternative
    
    def add_alternative ( self, alternative ) :
        self.alternatives.append( alternative )


# Objet général
# Contient deux tableaux intéressants :
# - tableau : Tableau d'objets Catégories, construit à partie de "base_de_données.csv"
# - categories : Tableau de correspondance entre le nom des catégories et leur ID, construit à partie de "catégories.csv"
#                Sert pour construire le premier tableau, ainsi qu'à l'ordre de placement des catégories lors de la construction du HTML (ETAPE 3)
class Alternatives :
    def __init__ ( self ) :
        self.tableau = [] # Tableau d'objets Catégorie
        
        # Permet de trouver les noms des catégories
        fichier = open( "catégories.csv" )
        self.categories = fichier.readlines()
        fichier.close()
        
        for i in range(len(self.categories)) :
            self.categories[i] = self.categories[i].replace( "\n", "" ).split(';')
        
        # On remplie notre tableau d'alternatives
        fichier = open( "base_de_données.csv" )
        bdd = fichier.readlines()
        fichier.close()
        
        for ligne in bdd :
            ligne = ligne.replace("\n", "").split(';')
            self.ajouter_alternative( Alternative( ligne[0], ligne[1], ligne[2], ligne[3] ) )
    
    def obtenir_nom_cat ( self, id_categorie ) :
        for cat in self.categories :
            if cat[0] == id_categorie :
                return cat[1]
    
    """
    Est ce que la catégorie existe déjà ?
    @return Si oui, retourne son index dans self.tableau
    @param id_categorie String étant l'ID de la catégorie
    """
    def cat_existe ( self, id_categorie ) :
        for i in range( len( self.tableau ) ) :
            if self.tableau[i].ID == id_categorie :
                return i
        return None
    
    """
    @param nom String
    @param ID String
    @return Son index dans self.tableau
    """
    def ajouter_categorie( self, nom, ID ) :
        self.tableau.append( Categorie( nom, ID ) )
        return -1
    
    """
    @param alternative Objet Alternative
    """
    def ajouter_alternative( self, alternative ) :
        index_cat = self.cat_existe( alternative.ID_cat )
        
        if index_cat != None : # Si la catégorie existe déjà
            self.tableau[index_cat].add_alternative( alternative )
        else : # Sinon, on la crée
            index_cat = self.ajouter_categorie( self.obtenir_nom_cat( alternative.ID_cat ), alternative.ID_cat )
            self.tableau[index_cat].add_alternative( alternative )
    
    """
    Obtenir l'objet Categorie grace à son ID
    @param id_categorie String
    """
    def obtenir_cat ( self, id_categorie ) :
        for cat in self.tableau :
            if cat.ID == id_categorie :
             return cat


"""
ETAPE 2 : Construire notre BDD des alternatives à partir du CSV
"""
alternatives = Alternatives() # On instancie la class Alternatives une seule fois


"""
ETAPE 3 : Construire le "menu"
"""
menu = ""

for i in range(len(alternatives.categories)) :
    if alternatives.cat_existe( alternatives.categories[i][0] ) != None : # Si la catégorie est utilisée, sinon ça ne sert à rien
        menu += "<a href=\"#cat-" + alternatives.categories[i][0] + "\">" + alternatives.categories[i][1] + "</a>"
        if i < len(alternatives.categories) - 1 :
            menu += " &bull; "


"""
ETAPE 3 : Construire le coeur de notre fichier HTML
"""
import requests
from bs4 import BeautifulSoup

# Converstion des accents et caractères spéciaux en entités HTML
import html as htmllib
table = {k: '&{};'.format(v) for k, v in htmllib.entities.codepoint2name.items()}

# Source : https://stackoverflow.com/questions/38009787/how-to-extract-meta-description-from-urls-using-python
def get_page_desc ( URL ) :
    if URL == "" :
        return ""
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, features="html.parser")
    metas = soup.find_all('meta')
    desc = [ meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
    if len(desc) > 0 :
        return desc[0].translate(table)
    else :
        return ""

fichier = open( "template_categorie.html" )
template_cat = fichier.read()
fichier.close()

fichier = open( "template_alternative.html" )
template_alt = fichier.read()
fichier.close()

html = ""

for categorie in alternatives.categories : # Pour afficher dans l'ordre donné dans "catégories.csv"
    cat = alternatives.obtenir_cat( categorie[0] )
    if cat == None : # C'est que la catégorie n'est pas utilisée
        continue
    
    html_cat = ""
    
    for alt in cat.alternatives :
        temp = template_alt.replace( "{NOM_ALTERNATIVE}", alt.nom )
        if alt.URL != "" :
            temp = temp.replace( "{URL_ALTERNATIVE}", alt.URL )
        else :
            temp = temp.replace( "<a href=\"{URL_ALTERNATIVE}\" target=\"_blank\">", "" ).replace( "</a>", "" )
        temp = temp.replace( "{DESCRIPTION_ALTERNATIVE}", alt.desc )
        temp = temp.replace( "{DESCRIPTION_SUR_LEUR_PAGE}", get_page_desc( alt.URL ) )
        html_cat += temp
        
    temp = template_cat.replace( "{CATEGORIE}", cat.nom )
    temp = temp.replace( "{ID_CATEGORIE}", "cat-" + cat.ID )
    temp = temp.replace( "{INSERER_ICI_LES_ALTERNATIVES}", html_cat )
    
    html += temp


"""
ETAPE 4 : Sortir le fichier HTML final
"""
fichier = open( "template_index.html" )
html_out = fichier.read()
fichier.close()

html_out = html_out.replace( "{INSERER_LIENS_VERS_CATEGORIES}", menu )

# Insérer le coeur du fichier
html_out = html_out.replace( "{INSERER_ICI_LE_COEUR}", html )

fichier = open( "index.html", "w" )
fichier.write( html_out )
fichier.close()
