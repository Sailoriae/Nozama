#coding: utf-8

"""
ETAPE 1 : Construire notre BDD des alternatives à partir du CSV
"""
# Tableau contenant la liste des alternatives, rangées par catégories
# - tab : Catégorie
#   - string : Code de la catégorie
#   - tab : Liste d'alternatives
#     - tab : Alternative
#       - string : Nom
#       - string : URL
#       - string : Code catégorie, DOIT CORRESPONDRE AU NUMERO DE LIGNE DANS "catégories.csv"
#       - string : Description
#     ...
# ...
alternatives = []

# Est ce que la catégorie existe déjà ?
# Si oui, retourne son index dans le tableau "alternatives"
def cat_existe ( codeCategorie ) :
    for i in range( len(alternatives) ) :
        if alternatives[i][0] == codeCategorie :
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


"""
ETAPE 2 : Construire notre liste des alternatives
"""
fichier = open( "catégories.csv" )
categories = fichier.readlines()
fichier.close()

for i in range(len(categories)) :
    categories[i] = categories[i].replace( "\n", "" )


"""
ETAPE 3 : Construire le "menu"
"""
menu = ""

for i in range(len(alternatives)) :
    menu += "<a href=\"#cat-" + alternatives[i][0] + "\">" + categories[ int(alternatives[i][0]) - 1 ] + "</a>"
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

for cat in alternatives :
    html_cat = ""
    
    for alt in cat[1] :
        temp = template_alt.replace( "{NOM_ALTERNATIVE}", alt[0] )
        temp = temp.replace( "{URL_ALTERNATIVE}", alt[1] )
        temp = temp.replace( "{DESCRIPTION_ALTERNATIVE}", alt[3] )
        temp = temp.replace( "{DESCRIPTION_SUR_LEUR_PAGE}", get_page_desc( alt[1] ) )
        html_cat += temp
        
    temp = template_cat.replace( "{CATEGORIE}", categories[ int(cat[0]) - 1 ] )
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
