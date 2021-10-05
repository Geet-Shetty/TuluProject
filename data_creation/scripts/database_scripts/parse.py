# coding=utf8

from bs4 import BeautifulSoup
import re
import csv

'''
TODO:
- missing a few words, check new codes 
- think about how to store the hyper link for sub header in meanings and store the sup
- fix the word object to do more work inside the class using proper methods 
- create return dict func for word, meanings and variations so that the json converter can work 


issues:
- current there is an issue of how to represent ೞ in tulu
- fix the image tag issue 
- check 
'''
def trim(string): # could flesh this out later, currently just trims extra spaces on both ends
    start = 0
    end = 0

    for index in range(0,len(string)):
        if(string[index] != ' '):
            start = index
            break

    for index in range(len(string)-1,-1,-1):
        if(string[index] != ' '):
            end = index
            break

    return string[start:end+1]

def read_keys(path):
    with open(path,'r',encoding="utf-8") as f:
        d = dict(filter(None, csv.reader(f)))

    # add all special characters
    # add ! to @ on ascii table
    for i in range(32,65):
        d[chr(i)] = chr(i)
    # add [ to ` on ascii table
    for i in range(91,96):
        d[chr(i)] = chr(i)
    # add { to ~ on ascii table
    for i in range(123,126):
        d[chr(i)] = chr(i)
    return d

keylist = read_keys('D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\keylist.csv')

def convert_unicode(kannada_word, keylist): # converts the kannada unicode into the malayalam unicode
    tulu_word = ''
    for char in kannada_word:
        # tulu_word.__add__(keylist[char]) # had to do tulu_word =
        tulu_word += keylist[char]
    return tulu_word
    # return ''

class Variations:

    def __init__(self):
        self.dialects = {} # could also be the context of the word, like medicinal instead of Lexical categories

    def create(self, table):
        td_elements = table.findAll('td')
        current_dialect = ''
        current_words = []
        td_elements = td_elements[1:len(td_elements)] # remove first td that is just the title VARIATIONS (Region/Caste wise)
        for td in td_elements:
            if td.has_attr('colspan'): # and not td.has_attr('class')
                if len(current_dialect) != 0 and len(current_words) > 0:
                    self.dialects[current_dialect] = current_words
                    current_words = []
                current_dialect = td.text
            else:
                supobj = td.find('sup')
                links = td.findAll('a')
                text = re.findall('\(.*?\)', td.text) # english words stored as plain text between parathesises
                counter = 0
                for link in links:
                    word = trim(link.text.replace("\n",''))
                    current_words.append({'kannda': word, 'english_tulu': text[counter][1:len(text[counter])-1], 'tulu': convert_unicode(word,keylist), 'id':  int(supobj.text) if supobj and supobj.text.isdigit() else 0})
                    counter+=1
        self.dialects[current_dialect] = current_words

class Meanings:

    def __init__(self):
        self.contexts={}

    def create(self,table):
        tr_elements = table.findAll('tr')
        current_context = ''
        current_definitions = []
        tr_elements = tr_elements[1:len(tr_elements)]  # remove first td that is just the title MEANINGS

        for tr in tr_elements:
            td = tr.find('td')
            if td.has_attr('colspan'):
                if len(current_context) != 0 and len(current_definitions) > 0:
                    self.contexts[current_context] = current_definitions
                    current_definitions = []
                current_context = td.text
            else:
                td_elements = tr.findAll('td')
                td_elements = td_elements[1:len(td_elements)] # get rid of empty td element, so the list should be length of 2
                if len(td_elements) == 2:
                    current_definitions.append({'kannada': td_elements[0].text.split(';'), 'english': td_elements[1].text.split(';')})
                elif len(td_elements) == 1:
                    if td_elements[0].text.isascii():
                        current_definitions.append({'kannada': [], 'english': td_elements[0].text.split(';')})
                    else:
                        current_definitions.append({'kannada': td_elements[0].text.split(';'), 'english': []})



        self.contexts[current_context] = current_definitions

class Word:

    def __init__(self, kannada, english, tulu, origin, id=0):
        self.word ={'kannada': kannada, 'english': english, 'tulu': tulu,'origin': origin, 'id':  id }
        # sometimes instead of dialect it is a source origin or type origin like noun or verb
        # seperate id needed because some words have the same spelling but different meaning and need a way to differentiate between them

def parse_html(html):

    # create soup object and find the needed tags
    html_soup = BeautifulSoup(html,'html.parser')
    header = html_soup.findAll('center') # center is only used in word and origin display at the top
    word_text = header[0].find('b').text

    table_list = html_soup.findAll('table')
    supobj = table_list[0].find('sup')
    #print(supobj.text.isdigit())
    table_list = table_list[1:len(table_list)] # all table objects except the first one with main word

    meanings = Meanings()
    variations = Variations()
    for table in table_list:
        header_rows = table.findAll('td')
        for row in header_rows:
            if row.has_attr('class') and row['class'][0] == 'tblhead':
                # print(row.parent.parent)
                #print('table title', row.text)
                if row.text == 'VARIATIONS (Region/Caste wise)':
                    variations.create(row.parent.parent)
                elif row.text == 'MEANINGS':
                    meanings.create(row.parent.parent)


            # elif row.has_attr('colspan') and not row.has_attr('class'):
            #     print('section title', row.text)
       # print(table.prettify())

    # website used  and image instead of '್' so this is just to add the actual unicode
    word_html = str(header[0].find('b'))
    img_html = '<img src="images/EBig.JPG"/>'
    index = word_html.find(img_html)
    if(index != -1):
        word_html = word_html[:index] + u'್' + word_html[index+len(img_html):]
        word_soup = BeautifulSoup(word_html,'html.parser')
        word_text = word_soup.text

    # split kannada and english and trim spaces from left and right
    words = []
    if word_text.__contains__('\xa0\xa0\n'):
        words = word_text.split('\xa0\xa0\n')
    elif word_text.__contains__('\xa0\xa0\\n'):
        words = word_text.split('\xa0\xa0\\n')
    words[1] = trim(words[1])

    # remove english O in kannada word
    if words[0].__contains__("o"):
        words[0] = words[0].replace("o",u"ಂ")

    # remove random commas in words (only specially for one fucken word lmao)
    words[0] = words[0].replace(",","")
    words[1] = words[1].replace(",", "")
    words[0] = words[0].replace("( ","(")
    words[1] = words[1].replace("( ", "(")

    return {'word':Word(words[0], words[1], convert_unicode(words[0],keylist), trim(header[1].text.replace(u"\xa0", u"")), int(supobj.text) if supobj.text.isdigit() else 0), 'meanings':meanings, 'variations':variations}  # Kannada, English, Origin
    #return {Word(words[0], words[1], convert_unicode(words[0],keylist), trim(header[1].text.replace(u"\xa0", u"")), int(supobj.text) if supobj.text.isdigit() else 0), meanings, variations}

# test_html = '<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅತಿಯುಕ್ತಿ ( ಕುಳು),&nbsp;&nbsp;\n    atiyukti ( kuḷu),    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ವಿವಿಧ ಯುಕ್ತಿಗಳು</TD><TD valign=top>Varieties of means and devices</TD></TR>      </TABLE><br></BODY>\n</html>'

# word = parse_html(test_html)
# print(word.kannada)
# print(word.english)
# print(word.origin)


# raw_html_data = open('D:\projects\Pythonnnn\TuluProject\data_creation\data\\raw_html_data.txt',
#                      'r',
#                      encoding="utf-8")
#
# def create_word_dump():
#     words = open(
#         f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\dump.txt",
#         "w",
#         encoding="utf-8")
#
#     count = 0
#     for html_line in raw_html_data:
#         if not html_line.replace("\n","").isdigit() and not html_line == "\n":
#             count += 1
#             try:
#                 # if count == 699: # 803
#                 #     print(html_line)
#                 word = parse_html(html_line)
#                 data = f'{word.kannada},{word.english},{word.origin}\n'
#                 words.write(data)
#             except (AttributeError,IndexError):
#                 print("testsstttt", html_line)
#
# def empty_pages(num):
#     page0 = open(
#         f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page.html",
#         "w",
#         encoding="utf-8")
#
#     page1 = open(
#         f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page1.html",
#         "w",
#         encoding="utf-8")
#
#     count = 0
#     for html_line in raw_html_data:
#         if not html_line.replace("\n","").isdigit() and not html_line == "\n":
#             count += 1
#             try:
#                 if count == num:
#                     page0.write(html_line)
#                     page1.write(raw_html_data.readline())
#                     return
#             except (AttributeError,IndexError):
#                 print("testsstttt", html_line)
#
# # empty_pages(12721) #403, 699, 803,
# #


# word = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಸಾತ್ತಿರ&nbsp;&nbsp;\n    saattira    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Paaddana, Tulu folk literature. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಶಾಸ್ತ್ರ;ಕಟ್ಟುಪಾಡು;ನಿಯಮ;ಪದ್ಧತಿ</TD><TD valign=top>Law;System;Rule;Custom</TD></TR><TR><TD valign=top></TD><TD valign=top>ಶುಭಾಶುಭಕಾರ್ಯಗಳಲ್ಲಿ ರೂಢಿಗತವಾಗಿರುವ ಆಚರಣೆ</TD><TD valign=top>Customary rites;Traditionally accepted rituals</TD></TR><TR><TD valign=top></TD><TD valign=top>ಭಾಷೆ, ಛಂದಸ್ಸು, ಸಂಪ್ರದಾಯ ಮೊದಲಾದುವುಗಳ ಕುರಿತಾದ ನಿಯಮಗಳನ್ನು ತಿಳಿಸುವ ವಿಜ್ಞಾನ</TD><TD valign=top>Science which tells about language, metre, tradition etc</TD></TR><TR><TD valign=top></TD><TD valign=top>ಧರ್ಮ, ವಿಜ್ಞಾನ ಮೊದಲಾದುವುಗಳ ಬಗೆಗೆ ತಿಳಿಸುವ ಗ್ರಂಥ;ಶಾಸ್ತ್ರಗ್ರಂಥ</TD><TD valign=top>Any work of literature or science which deals with religion;A treatise on religion or science</TD></TR><TR><TD valign=top></TD><TD valign=top>ಮುಂದಾಗುವ ಘಟನೆಗಳನ್ನು ತಿಳಿಸುವ ವಿಜ್ಞಾನ;ಭವಿಷ್ಯ</TD><TD valign=top>Sooth saying;Prediction</TD></TR><TR><TD colspan=3><b><i>Figurative, Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಪರಂಪರಾಗತ ಪದ್ಧತಿಯ ಅಲ್ಪಾನುಸರಣೆ</TD><TD valign=top>Perfunctory work;Following the customary rites without interest</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Mandaara Raamaayana (by Mandara Keshava Bhatta)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000020");\'>\n                ಸಾತ್ರ</a>\n                &nbsp;(saatra).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Northen Dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000015");\'>\n                ಶಾಸ್ತ್ರ</a>\n                &nbsp;(śaastra).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South brahmin dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000016");\'>\n                ಶಾಸ್ತ್ರೊ</a>\n                &nbsp;(śaastro).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South Common dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000017");\'>\n                ಸಾಸ್ತ್ರೊ</a>\n                &nbsp;(saastro).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("28420000000018");\'>\n                ಸಾತ್ರೊ</a>\n                &nbsp;(saatro).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("28420000000019");\'>\n                ಸಾಸ್ರೊ</a>\n                &nbsp;(saasro).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South harijan tribal dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000021");\'>\n                ಚಾತ್ರೊ</a>\n                &nbsp;(caatro).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(1.2.25,17)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಧರೆಟ್ ಸರ್ವಪುರಾಣ ಶಾಸ್ತ್ರೊಮಿ ವ್ಯಾಸರೂಪುಟ್ ನಿರ್ಮಿತ್.&nbsp;dhareṭụ sarvapuraaṇa śaastromi vyaasaruupuṭụ nirmitụ.&nbsp;ಭೂಮಿಯಲ್ಲಿ ವ್ಯಾಸರೂಪದಲ್ಲಿ ಬಂದು ಎಲ್ಲ ಪುರಾಣಶಾಸ್ತ್ರಗಳನ್ನು ಸೃಷ್ಟಿಮಾಡಿ.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Proverb</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಓದುನೆ<img src=images/EBig.JPG width=10 height=13 /> ಶಾಸ್ತ್ರೊ ಪಾಡುನೆ<img src=images/EBig.JPG width=10 height=13 /> ಗಾಳೊ.&nbsp;oodunϵ śaastro paaḍunϵ gaaḷo.&nbsp;ಓದುವುದು ಶಾಸ್ತ್ರ ಇಕ್ಕುವುದು ಗಾಳ.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Skt.śaastra.<br/></TD></TR></TABLE><br></BODY>\n</html>'
# )

# word2 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>1</font></sup><font size=+3><b>ಉದಿಪನ&nbsp;&nbsp;\n    udipana    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Paaddana, Tulu folk literature. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಜನನ;ಸೃಷ್ಟಿ</TD><TD valign=top>Birth;Creation</TD></TR><TR><TD valign=top></TD><TD valign=top>ಪ್ರಾರ೦ಭ</TD><TD valign=top>Beginning</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Northen Dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("3610000000010");\'>\n                ಉತ್ಪನ್ನ</a>\n                &nbsp;(utpanna).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("3610000000011");\'>\n                ಉದ್ಪನ್ನ</a>\n                &nbsp;(udpanna).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Southern dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3610000000012");\'>\n                ಉತ್ಪನ್ನೊ</a>\n                &nbsp;(utpanno).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("3610000000013");\'>\n                ಉದ್ಪನ್ನೊ</a>\n                &nbsp;(udpanno).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Srii Bhagavato (Ed. Venktataraja Puninchattaya)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3610000000014");\'>\n                ಉತ್ಪನ್ನೊ</a>\n                &nbsp;(utpanno).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(3.13.8,313)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಉತ್ಪನ್ನೊಂಟುಂದುವಿಂಚ ಜೇವಪ ಮುಪ್ಪುತಾನಿಕ್ ಜಾಗತೀ.&nbsp;utpannoṇṭunduviñca jeevapa mupputaanikụ jaagatii.&nbsp;ಪ್ರಾರ೦ಭದಲ್ಲೇ ಇದು ಹೀಗೆ ಹೆಚ್ಚಾಗಲು ಮುಪ್ಪಿನಲ್ಲಿ ಏನು ಗತಿ?<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Paaddana, Tulu folk literature</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಪಚ್ಚಡೆ<img src=images/EBig.JPG width=10 height=13 /> ಸಿರೆಂಗ್<img src=images/E.JPG width=0 />ಡ್ ಗಂದ ಪುರ್ಪಾದ್ ಉದಿಪನ ಆಯಿ ಮಗಳಾಳ್.&nbsp;paccaḍϵ sireṅgụḍụ ganda purpaadụ udipana aayi magaḷaaḷụ.&nbsp;ಹಚ್ಚಡದ ಸೆರಗಿನಲ್ಲಿ ಗ೦ಧ ಪುಷ್ಪವಾಗಿ ಜನನವಾದ ಮಗಳವಳು.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Skt.utpanna.<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
#
# word3 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಕಟ್ಟಳೆ<img src=images/EBig.JPG /> ಕಂದಾಚಾರ&nbsp;&nbsp;\n    kaṭṭaḷϵ kandaacaara    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Kissanwar Glossary of Kannada words (by Ullal Narasinga Rao). &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>Customary ceremonies</TD></TR>      </TABLE><br></BODY>\n</html>\n')
# word4 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅೞಿ&nbsp;&nbsp;\n    aḻi    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Verb neuter</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಲಯವಾಗು (?)</TD><TD valign=top>Be saturated(?)</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(3.21.21;367)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಕರೊಸ್ಟ್ ಕರಣೇಂದ್ರಿಯೊ ಭಕ್ತಿಸುಖೊಂಟೞಿಸ್ಟೀ ವರ ಚಿತ್ತೊಂಟೊರೊ ಪಾರ್ಪನೆ.&nbsp;karosṭụụ karaṇeendriyo bhaktisukhoṇṭaḻisṭii vara cittoṇṭoro paarpane.&nbsp;ಭಕ್ತಿ ಸುಖದಲ್ಲಿ ಕರಣೇಂದ್ರಿಯಗಳು ಕರಗಿ ಲಯವಾಗಿ (?) ಪವಿತ್ರವಾದ ಚಿತ್ತದಲ್ಲಿ ಒಮ್ಮೆಯೂ ಚಲಿಸದೆ.<br></TD></TR></TABLE><br></BODY>\n</html>\n')
# word5 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>2</font></sup><font size=+3><b>ಅಣಿಲೆ<img src=images/EBig.JPG />&nbsp;&nbsp;\n    aṇilϵ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಭತ್ತದ ಮೊಳಕೆ</TD><TD valign=top>Germ of paddy seed</TD></TR><TR><TD valign=top></TD><TD valign=top>ಭತ್ತದ ಮೊಳಕೆಯೊಡೆಯುವ ತುದಿ</TD><TD valign=top>Germinating point of paddy seed</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>All</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("770000000048");\'>\n                ಅನಿಲೆ<img src=images/E.JPG height=13 width=10 BoRDER=0 /></a>\n                &nbsp;(anilϵ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
word6 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>8</font></sup><font size=+3><b>ಆಯ&nbsp;&nbsp;\n    aaya    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Postposition</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಸಾಮಾನ್ಯವಾಗಿ ಶಿವಳ್ಳಿ ಬ್ರಾಹ್ಮಣ ಕುಲನಾಮಗಳ ಅಂತ್ಯದಲ್ಲಿ ಬರುವ ಪರಸರ್ಗ;<sup>1</sup><b>ಆಯೆ</b> \'ಅವನು\' ಎಂಬುದರ ರೂಪಭೇದ</TD><TD valign=top>The postposition appended usually in a shivalli Brahmin’s surname;A variant of <sup>1</sup><b>aaye</b> \'he’</TD></TR>      </TABLE><br></BODY>\n</html>')
word7 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>-ಒಲು&nbsp;&nbsp;\n    -olu    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;North common harijan tribal jain dialect. &nbsp;Pancavati Raamaayana Vaali Sugreevera Kaalago (by Sankayya Bhagavatha; Ed. T. Keshava Bhatta). &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Suffix</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಕ್ರಿಯಾ ರೂಪಗಳ ಪ್ರಥಮ ಪುರುಷ ಸ್ತ್ರೀಲಿಂಗ ಏಕವಚನ ಪ್ರತ್ಯಯ</TD><TD valign=top>Third person feminine singular suffix of verbal forms</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Common Harijan Tribal Jain</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000087");\'>\n                -ಅಲ್</a>\n                &nbsp;(-alụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North brahmin Dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000086");\'>\n                -ಅಳ್</a>\n                &nbsp;(-aḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North common harijan tribal jain dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000089");\'>\n                -ಒಳು</a>\n                &nbsp;(-oḷu).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000091");\'>\n                -ಓಲು</a>\n                &nbsp;(-oolu).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Pancavati Raamaayana Vaali Sugreevera Kaalago (by Sankayya Bhagavatha; Ed. T. Keshava Bhatta)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000089");\'>\n                -ಒಳು</a>\n                &nbsp;(-oḷu).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000091");\'>\n                -ಓಲು</a>\n                &nbsp;(-oolu).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Rare occurance</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2060000000088");\'>\n                -ಆಳ್</a>\n                &nbsp;(-aaḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South common harijan tribal jain dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2060000000088");\'>\n                -ಆಳ್</a>\n                &nbsp;(-aaḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Southern dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000086");\'>\n                -ಅಳ್</a>\n                &nbsp;(-aḷụ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>EXAMPLES</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>battaḷụ/battalụ/battaaḷụ/battoḷu/battolu/battoolu<br/></TD></TR></TABLE><br></BODY>\n</html>')
word8 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>2</font></sup><font size=+3><b>ಬಲಂಬಾಯಿ&nbsp;&nbsp;\n    balambaayi    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Dictionary of Rev. Manner. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>The bamboo in a roof at the entrance of a house</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Dictionary of Rev. Manner</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("50040000000046");\'>\n                ಬಲಬಾಯಿ</a>\n                &nbsp;(balabaayi).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
print(len(word7.get('variations').dialects))