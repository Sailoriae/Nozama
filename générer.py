#coding: utf-8

"""
ETAPE 1 : Construire notre BDD des alternatives à partir du CSV
"""
# Tableau contenant la liste des alternatives, rangées par catégories
# - tab : Catégorie
#   - string : ID de la catégorie
#   - tab : Liste d'alternatives
#     - tab : Alternative
#       - string : Nom
#       - string : URL
#       - string : ID de la catégorie (Oui, c'est redondant)
#       - string : Description
#     ...
# ...
alternatives = []

# Est ce que la catégorie existe déjà ?
# Si oui, retourne son index dans le tableau "alternatives"
def cat_existe ( idCategorie ) :
    for i in range( len(alternatives) ) :
        if alternatives[i][0] == idCategorie :
            return i
    return None

fichier = open( "base_de_données.csv" )
bdd = fichier.readlines()
fichier.close()

for ligne in bdd :
    ligne = ligne.replace("\n", "").split(';')
    indexCat = cat_existe( ligne[2] )
    
    if indexCat != None : # Si la catégorie existe déjà
        alternatives[indexCat][1].append( ligne )
    else : # Sinon, on la crée
        alternatives.append( [ ligne[2], [ ligne ] ] )

# Obtenir la catégorie dans le tableau "alternatives"
def obtenir_cat ( idCategorie ) :
    for cat in alternatives :
        if cat[0] == idCategorie :
         return cat


"""
ETAPE 2 : Construire notre liste des alternatives
"""
fichier = open( "catégories.csv" )
categories = fichier.readlines()
fichier.close()

for i in range(len(categories)) :
    categories[i] = categories[i].replace( "\n", "" ).split(';')

def obtenir_nom_cat ( idCategorie ) :
    for cat in categories :
        if cat[0] == idCategorie :
            return cat[1]


"""
ETAPE 3 : Construire le "menu"
"""
menu = ""

for i in range(len(alternatives)) :
    menu += "<a href=\"#cat-" + alternatives[i][0] + "\">" + obtenir_nom_cat( alternatives[i][0] ) + "</a>"
    if i < len(alternatives) - 1 :
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

for categorie in categories : # Pour afficher dans l'ordre donné dans "catégories.csv"
    cat = obtenir_cat( categorie[0] )
    if cat == None : # C'est que la catégorie n'est pas utilisée
        continue
    
    html_cat = ""
    
    for alt in cat[1] :
        temp = template_alt.replace( "{NOM_ALTERNATIVE}", alt[0] )
        if alt[1] != "" :
            temp = temp.replace( "{URL_ALTERNATIVE}", alt[1] )
        else :
            temp = temp.replace( "<a href=\"{URL_ALTERNATIVE}\" target=\"_blank\">", "" ).replace( "</a>", "" )
        temp = temp.replace( "{DESCRIPTION_ALTERNATIVE}", alt[3] )
        temp = temp.replace( "{DESCRIPTION_SUR_LEUR_PAGE}", get_page_desc( alt[1] ) )
        html_cat += temp
        
    temp = template_cat.replace( "{CATEGORIE}", obtenir_nom_cat( cat[0] ) )
    temp = temp.replace( "{ID_CATEGORIE}", "cat-" + cat[0] )
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
