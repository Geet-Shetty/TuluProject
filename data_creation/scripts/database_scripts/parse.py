# coding=utf8
import unicodedata #TODO: use this
import os
from bs4 import BeautifulSoup
import re
import csv
import path

'''
TODO:
- missing a few words, check new codes 
- separate the bug html lines (ignored for now)
- \" and \' issue 
- \\r\\n issue 
- mean semi colon issue, quick fix might be to just not split if the semicolon count isn't the same
  but there still could be edge cases where that wouldn't work 
'''

def iskannada(string): # might be better to check range using the order function
    for char in string:
        if char.isascii() and char.isalpha():
            return False
    return True

def find_occurances(str, chr):
    indices = []
    for i in range(len(str)):
        if (str[i] == chr):
            indices.append(i)
    return indices

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

    # d[u'ೕ'] = 'ḻ' # temp conversion holder

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

keylist = read_keys('keylist.csv')

def convert_unicode(kannada_word): # converts the kannada unicode into the malayalam unicode
    keylist = read_keys('keylist.csv')
    try:
        tulu_word = ''
        for char in kannada_word:
            # tulu_word.__add__(keylist[char]) # had to do tulu_word =
            tulu_word += keylist[char]
        return tulu_word
    except KeyError: # issues with ೞ and ೕ
        return kannada_word
    # return ''

def img_to_unicode(tag):
    img_tags = tag.findAll('img')
    for img in img_tags:
        if not( (img.has_attr('height') and img['height'] == '0') or (img.has_attr('width') and img['width'] == '0') ): # ignore the tags that don't show up
            if img.has_attr('src'):
                if img['src'] == 'images/LBig.JPG' or img['src'] == 'images/L.JPG':  # this has to be added first to work in combination with character below
                    img.insert_after(u'ೕ')
                elif img['src'] == 'images/EBig.JPG' or img['src'] == 'images/E.JPG':
                    img.insert_after(u'್')

# TODO: added known cases, think about how to find other cases
def correct_unicode(string):
    char_list = list(string)
    '''
    let = 0x0C80
    print(let)
    3200
    print(0xC80)
    3200
    print(0xc80)
    3200
    ord('ಮ')
    3246
    
    'o': u'ಂ', 
    
    'O'.__contains__('o')
    False
    'O'.count('o')
    0
    have to worry about both caps and lower 
    '''
    # test = find_occurances(string,u'ನ')
    # test1 = find_occurances(string, u'ೕ')
    kzerolist = find_occurances(string,u'೦')
    for index in kzerolist:
        # if the kannada zero is used and its previous character is kannada and not a kannada digit then replace with proper character
        if index > 0 and ord(char_list[index-1]) >= 3200 and ord(char_list[index-1]) <= 3327 and not (ord(char_list[index - 1]) >= 3302 and ord(char_list[index - 1]) <= 3311):
            char_list[index] = u'ಂ'

    olist = find_occurances(string,'o') + find_occurances(string,'O')
    for index in olist:
        # if the english o is
        if index > 0 and ord(char_list[index-1]) >= 3200 and ord(char_list[index-1]) <= 3327:
            char_list[index] = u'ಂ'

    return ''.join(char_list)
    # conversions = {u'೦': u'ಂ'}
    # for c1,c2 in conversions.items():

def create_id(supobj):
    return int(supobj.string.extract()) if supobj and supobj.text.isdigit() else 0

def create_word(table):

    center_elements = table.findAll('center')  # center is only used in word and origin display at the top
    supobj = center_elements[0].find('sup')  # find the sup object that hold the word sub id
    id = create_id(supobj)
    word_btag = center_elements[0].find('b')  # contains the kannada and english tulu word

    # split kannada and english and trim spaces from left and right
    words = []
    if word_btag.text.__contains__('\xa0\xa0\n'):
        words = word_btag.text.split('\xa0\xa0\n')
    elif word_btag.text.__contains__('\xa0\xa0\\n'):
        words = word_btag.text.split('\xa0\xa0\\n')

    words[0] = trim(words[0])
    words[1] = trim(words[1])

    # better to do on the html string level will have to check for not ascii chars on both sides
    # # remove english O in kannada word and add proper unicode
    # if words[0].__contains__("o"): # has to be done at this lvl instead of the whole html string because we don't wanna replace the Os in the english ext
    #     words[0] = words[0].replace("o", u"ಂ")

    # remove random commas in words (only specially for one fucken word lmao)
    words[0] = words[0].replace(",","")
    words[1] = words[1].replace(",", "")
    words[0] = words[0].replace("( ","(")
    words[1] = words[1].replace("( ", "(")

    word = {'kannada': words[0], 'english': words[1], 'tulu': convert_unicode(words[0]), 'origin': trim(center_elements[1].text.replace(u"\xa0", u"")), 'id':  id}

    # sometimes instead of dialect it is a source origin or type origin like noun or verb
    # seperate id needed because some words have the same spelling but different meaning and need a way to differentiate between them

    return word

def create_meanings(table):
    meanings = []
    tr_elements = table.findAll('tr')
    current_contexts = {'contexts': [], 'linked_context': {}, 'definitions': []}
    id = 0
    current_definitions = []
    tr_elements = tr_elements[1:len(tr_elements)]  # remove first td that is just the title MEANINGS

    for tr in tr_elements:
        td = tr.find('td')
        if td.has_attr('colspan'): # its a sub header

            if len(current_definitions): # remember this is true if the length is not zero

                # add data to meanings
                if len(current_contexts['linked_context']):
                    current_contexts['linked_context']['id'] = id
                current_contexts['definitions'] = current_definitions
                meanings.append(current_contexts)

                # clear variables
                id = 0
                current_contexts = {'contexts': [], 'linked_context': {}, 'definitions': []}
                current_definitions = []
                current_contexts['linked_context'] = {}

            if td.findAll('a'): # true if the list is longer than one, in our case it will either be len of 0 or 1

                # create id
                supobj = td.find('sup')
                id = create_id(supobj)
                header_list = td.text.split(',')

                current_contexts['linked_context'] = {'context': '', 'kannada': '', 'english': '', 'tulu': '', 'id': 0}
                current_contexts['contexts'] = list(filter(lambda context: not context.isspace(), header_list[:len(header_list)-1])) # this is -1 for the len because we don't want to inlude the linked context
                current_contexts['contexts'] = list(map(lambda context: trim(context), current_contexts['contexts']))

                # create link context
                link = trim(header_list[len(header_list)-1]).split('of') # all the links of far have been xxxxx of xxxxx
                current_contexts['linked_context']['context'] = link[0]
                link[1] = link[1].replace('\xa0', '')
                words = link[1].split('(')
                kannada = trim(words[0])
                current_contexts['linked_context']['kannada'] = kannada
                current_contexts['linked_context']['english'] = trim(words[1][:len(words[1])-1]) # the len is -1 because we want to get rid of the ending )
                current_contexts['linked_context']['tulu'] = convert_unicode(kannada)
            else:

                # this is for creating the context if no linked context exists
                header_list = td.text.split(',')
                current_contexts['contexts'] = list(filter(lambda context: not context.isspace(), header_list))
                current_contexts['contexts'] = list(map(lambda context: trim(context), current_contexts['contexts']))

        else:

            # get meanings
            td_elements = tr.findAll('td')
            td_elements = td_elements[1:len(td_elements)] # get rid of empty td element, so the list should be length of 2
            if len(td_elements) == 2:
                current_definitions.append({'kannada': list(map(lambda meaning: trim(meaning), td_elements[0].text.split(';'))), 'english': list(map(lambda meaning: trim(meaning),td_elements[1].text.split(';')))})
            elif len(td_elements) == 1:
                data = list(map(lambda meaning: trim(meaning),td_elements[0].text.split(';')))
                if td_elements[0].text.isascii():
                    current_definitions.append({'kannada': [], 'english': data})
                else:
                    current_definitions.append({'kannada': data, 'english': []})

    # adds the last context
    if len(current_contexts['linked_context']): # if the linked context isn't empty then set the id (don't want to add id if object is empty)
        current_contexts['linked_context']['id'] = id
    current_contexts['definitions'] = current_definitions
    meanings.append(current_contexts)
    return meanings

def create_variations(table):
    # the smaller versions of the images ex E.jpg compared to EBig.jpg is for variations
    # also have to consider if some words in it might be poorly formatted
    variations = {} # could also be the context of the word, like medicinal instead of Lexical categories
    td_elements = table.findAll('td')
    current_origin = ''
    current_words = []
    td_elements = td_elements[1:len(td_elements)] # remove first td that is just the title VARIATIONS (Region/Caste wise)
    for td in td_elements:
        if td.has_attr('colspan'): # sub header
            if len(current_origin) and len(current_words):
                variations[current_origin] = current_words
                current_words = []
            current_origin = td.text
        else:
            # get links
            supobj = td.find('sup')
            links = td.findAll('a')
            # print(td.text.split(' '))
            text = re.findall('\(.*?\)', td.text) # english words stored as plain text between parathesises
            counter = 0
            for link in links:
                word = trim(link.text.replace("\\n", ''))
                word = trim(word.replace("\n", ''))
                current_words.append({'kannda': word, 'english': trim(text[counter][1:len(text[counter])-1]), 'tulu': convert_unicode(word), 'id':  create_id(supobj)})
                # the len -1 is to get rid of the ending ) for the english word, same case like in meanings
                # also the creation of the id doesn't need the .extract but it does it anyway because its a general function
                counter+=1

    variations[current_origin] = current_words
    return variations

def create_references(table): # could just go by td elements instead
    #TODO: flush out this function, currently there is only one case (in nbsp over 2) where a general method would be needed for so now imma cheese it
    def split_kt(string): # this function would find the chunks of sentence ender and clean it to just only the first
        char_list = list(string)

        '''
        so far this have not been cleaned up but just separated by nbsp
        ....,.
        .,.
        ....
        '''

    references = {}
    td_elements = table.findAll('td')
    current_ref_type = ''
    current_refs = []
    td_elements = td_elements[1:len(td_elements)] # remove first td that is just the title REFERENCES
    for td in td_elements:
        if td.has_attr('colspan'):  # sub header
            if len(current_ref_type) and len(current_refs): # if neither are zero
                references[current_ref_type] = current_refs
                current_refs = []
            current_ref_type = trim(td.text)
        else:
            if td.text.isspace(): # if td is empty
                continue

            # nbsp is a space character that usually breaks up the different languages but sections with more than one saying kannada and tulu are not split by nbsp
            sentences = td.text.split(' ')
            if len(find_occurances(td.text,' ')) == 2:
                current_refs.append({'tulu': convert_unicode(sentences[0]), 'english': sentences[1], 'kannada': sentences[2]})
            else:
                current_ref = {'tulu': convert_unicode(sentences[0]), 'english': '', 'kannada': ''}

                for i in range(1, len(sentences) - 1,2):
                    current_ref['english'] = sentences[i]
                    # this current method is a hack, but hey it should work
                    # do not split by ;, split isn't just single character like . ? ! it can also be ... etc
                    # if len is 3 then just do t e k
                    # if len is 5 then just do t e kt e t and split the kt
                    # if len is 7 then just do t e kt e kt e k  and split both of the kt
                    # the greater lens follow the same pattern as 5 and 7
                    sentence = sentences[i+1]
                    kannada_tulu = []
                    if sentence.__contains__('...'):
                        kannada_tulu = sentence.split('...')
                        kannada_tulu[0] = kannada_tulu[0] + '.'
                    else:
                        index = 0
                        # the order matters here, between ? and ! is doesn't matter what is first, just matters that . is last because we have combos of ! . and ? . for the two sentences and want to split by the first ender
                        if sentence.__contains__('?') and not sentence.__contains__(
                                '(?)'):  # we don't wanna split when its (?), this only occurs with . as the sentence ender
                            index = sentence.find('?')
                        elif sentence.__contains__('!'):
                            index = sentence.find('!')
                        elif sentence.__contains__('.'):
                            index = sentence.find('.')

                        # remember the kannada sentence ender tulu
                        kannada_tulu.append(sentence[:index + 1])
                        kannada_tulu.append(sentence[index + 1:])

                    current_ref['kannada'] = kannada_tulu[0]
                    current_refs.append(current_ref)
                    current_ref = {'tulu': convert_unicode(kannada_tulu[1]), 'english': '', 'kannada': ''}

    references[current_ref_type] = current_refs
    return references

def create_examples(table):
    td_elements = table.findAll('td',attrs={"colspan": "2"})
    examples_text = []
    for td in td_elements:
        examples_text.append(td.text)
    return examples_text

def create_language_refs(table): # assumes only one line, true for the current data set
    return table.find('td',attrs={"colspan": "2"}).text

def parse_html(html):

    # create soup object and find the needed tags
    html_soup = BeautifulSoup(correct_unicode(html),'html.parser')

    img_to_unicode(html_soup)

    table_list = html_soup.findAll('table')
    word = create_word(table_list[0])
    table_list = table_list[1:len(table_list)] # all table objects except the first one with main word

    meanings = []
    variations = {}
    language_refs = ''
    examples = []
    references = {}

    for table in table_list:
        header_rows = table.findAll('td')
        for row in header_rows:
            if row.has_attr('class') and row['class'][0] == 'tblhead':
                if row.text == 'VARIATIONS (Region/Caste wise)':
                    variations = create_variations(row.parent.parent)
                elif row.text == 'MEANINGS':
                    meanings = create_meanings(row.parent.parent)
                elif row.text == 'Language References':
                    language_refs = create_language_refs(row.parent.parent)
                elif row.text == 'EXAMPLES':
                    examples = create_examples(row.parent.parent)
                elif row.text == 'REFERENCES':
                    references = create_references(row.parent.parent)

    return {'word': word, 'meanings': meanings, 'variations': variations, 'references': references, 'examples': examples, 'language_refs': language_refs}

# # testing data
# words = [
# parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಸಾತ್ತಿರ&nbsp;&nbsp;\n    saattira    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Paaddana, Tulu folk literature. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಶಾಸ್ತ್ರ;ಕಟ್ಟುಪಾಡು;ನಿಯಮ;ಪದ್ಧತಿ</TD><TD valign=top>Law;System;Rule;Custom</TD></TR><TR><TD valign=top></TD><TD valign=top>ಶುಭಾಶುಭಕಾರ್ಯಗಳಲ್ಲಿ ರೂಢಿಗತವಾಗಿರುವ ಆಚರಣೆ</TD><TD valign=top>Customary rites;Traditionally accepted rituals</TD></TR><TR><TD valign=top></TD><TD valign=top>ಭಾಷೆ, ಛಂದಸ್ಸು, ಸಂಪ್ರದಾಯ ಮೊದಲಾದುವುಗಳ ಕುರಿತಾದ ನಿಯಮಗಳನ್ನು ತಿಳಿಸುವ ವಿಜ್ಞಾನ</TD><TD valign=top>Science which tells about language, metre, tradition etc</TD></TR><TR><TD valign=top></TD><TD valign=top>ಧರ್ಮ, ವಿಜ್ಞಾನ ಮೊದಲಾದುವುಗಳ ಬಗೆಗೆ ತಿಳಿಸುವ ಗ್ರಂಥ;ಶಾಸ್ತ್ರಗ್ರಂಥ</TD><TD valign=top>Any work of literature or science which deals with religion;A treatise on religion or science</TD></TR><TR><TD valign=top></TD><TD valign=top>ಮುಂದಾಗುವ ಘಟನೆಗಳನ್ನು ತಿಳಿಸುವ ವಿಜ್ಞಾನ;ಭವಿಷ್ಯ</TD><TD valign=top>Sooth saying;Prediction</TD></TR><TR><TD colspan=3><b><i>Figurative, Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಪರಂಪರಾಗತ ಪದ್ಧತಿಯ ಅಲ್ಪಾನುಸರಣೆ</TD><TD valign=top>Perfunctory work;Following the customary rites without interest</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Mandaara Raamaayana (by Mandara Keshava Bhatta)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000020");\'>\n                ಸಾತ್ರ</a>\n                &nbsp;(saatra).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Northen Dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000015");\'>\n                ಶಾಸ್ತ್ರ</a>\n                &nbsp;(śaastra).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South brahmin dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000016");\'>\n                ಶಾಸ್ತ್ರೊ</a>\n                &nbsp;(śaastro).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South Common dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000017");\'>\n                ಸಾಸ್ತ್ರೊ</a>\n                &nbsp;(saastro).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("28420000000018");\'>\n                ಸಾತ್ರೊ</a>\n                &nbsp;(saatro).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("28420000000019");\'>\n                ಸಾಸ್ರೊ</a>\n                &nbsp;(saasro).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South harijan tribal dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("28420000000021");\'>\n                ಚಾತ್ರೊ</a>\n                &nbsp;(caatro).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(1.2.25,17)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಧರೆಟ್ ಸರ್ವಪುರಾಣ ಶಾಸ್ತ್ರೊಮಿ ವ್ಯಾಸರೂಪುಟ್ ನಿರ್ಮಿತ್.&nbsp;dhareṭụ sarvapuraaṇa śaastromi vyaasaruupuṭụ nirmitụ.&nbsp;ಭೂಮಿಯಲ್ಲಿ ವ್ಯಾಸರೂಪದಲ್ಲಿ ಬಂದು ಎಲ್ಲ ಪುರಾಣಶಾಸ್ತ್ರಗಳನ್ನು ಸೃಷ್ಟಿಮಾಡಿ.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Proverb</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಓದುನೆ<img src=images/EBig.JPG width=10 height=13 /> ಶಾಸ್ತ್ರೊ ಪಾಡುನೆ<img src=images/EBig.JPG width=10 height=13 /> ಗಾಳೊ.&nbsp;oodunϵ śaastro paaḍunϵ gaaḷo.&nbsp;ಓದುವುದು ಶಾಸ್ತ್ರ ಇಕ್ಕುವುದು ಗಾಳ.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Skt.śaastra.<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>1</font></sup><font size=+3><b>ಉದಿಪನ&nbsp;&nbsp;\n    udipana    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Paaddana, Tulu folk literature. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಜನನ;ಸೃಷ್ಟಿ</TD><TD valign=top>Birth;Creation</TD></TR><TR><TD valign=top></TD><TD valign=top>ಪ್ರಾರ೦ಭ</TD><TD valign=top>Beginning</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Northen Dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("3610000000010");\'>\n                ಉತ್ಪನ್ನ</a>\n                &nbsp;(utpanna).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("3610000000011");\'>\n                ಉದ್ಪನ್ನ</a>\n                &nbsp;(udpanna).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Southern dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3610000000012");\'>\n                ಉತ್ಪನ್ನೊ</a>\n                &nbsp;(utpanno).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("3610000000013");\'>\n                ಉದ್ಪನ್ನೊ</a>\n                &nbsp;(udpanno).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Srii Bhagavato (Ed. Venktataraja Puninchattaya)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3610000000014");\'>\n                ಉತ್ಪನ್ನೊ</a>\n                &nbsp;(utpanno).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(3.13.8,313)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಉತ್ಪನ್ನೊಂಟುಂದುವಿಂಚ ಜೇವಪ ಮುಪ್ಪುತಾನಿಕ್ ಜಾಗತೀ.&nbsp;utpannoṇṭunduviñca jeevapa mupputaanikụ jaagatii.&nbsp;ಪ್ರಾರ೦ಭದಲ್ಲೇ ಇದು ಹೀಗೆ ಹೆಚ್ಚಾಗಲು ಮುಪ್ಪಿನಲ್ಲಿ ಏನು ಗತಿ?<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Paaddana, Tulu folk literature</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಪಚ್ಚಡೆ<img src=images/EBig.JPG width=10 height=13 /> ಸಿರೆಂಗ್<img src=images/E.JPG width=0 />ಡ್ ಗಂದ ಪುರ್ಪಾದ್ ಉದಿಪನ ಆಯಿ ಮಗಳಾಳ್.&nbsp;paccaḍϵ sireṅgụḍụ ganda purpaadụ udipana aayi magaḷaaḷụ.&nbsp;ಹಚ್ಚಡದ ಸೆರಗಿನಲ್ಲಿ ಗ೦ಧ ಪುಷ್ಪವಾಗಿ ಜನನವಾದ ಮಗಳವಳು.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Skt.utpanna.<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಕಟ್ಟಳೆ<img src=images/EBig.JPG /> ಕಂದಾಚಾರ&nbsp;&nbsp;\n    kaṭṭaḷϵ kandaacaara    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Kissanwar Glossary of Kannada words (by Ullal Narasinga Rao). &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>Customary ceremonies</TD></TR>      </TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅೞಿ&nbsp;&nbsp;\n    aḻi    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Verb neuter</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಲಯವಾಗು (?)</TD><TD valign=top>Be saturated(?)</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(3.21.21;367)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಕರೊಸ್ಟ್ ಕರಣೇಂದ್ರಿಯೊ ಭಕ್ತಿಸುಖೊಂಟೞಿಸ್ಟೀ ವರ ಚಿತ್ತೊಂಟೊರೊ ಪಾರ್ಪನೆ.&nbsp;karosṭụụ karaṇeendriyo bhaktisukhoṇṭaḻisṭii vara cittoṇṭoro paarpane.&nbsp;ಭಕ್ತಿ ಸುಖದಲ್ಲಿ ಕರಣೇಂದ್ರಿಯಗಳು ಕರಗಿ ಲಯವಾಗಿ (?) ಪವಿತ್ರವಾದ ಚಿತ್ತದಲ್ಲಿ ಒಮ್ಮೆಯೂ ಚಲಿಸದೆ.<br></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>2</font></sup><font size=+3><b>ಅಣಿಲೆ<img src=images/EBig.JPG />&nbsp;&nbsp;\n    aṇilϵ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಭತ್ತದ ಮೊಳಕೆ</TD><TD valign=top>Germ of paddy seed</TD></TR><TR><TD valign=top></TD><TD valign=top>ಭತ್ತದ ಮೊಳಕೆಯೊಡೆಯುವ ತುದಿ</TD><TD valign=top>Germinating point of paddy seed</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>All</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("770000000048");\'>\n                ಅನಿಲೆ<img src=images/E.JPG height=13 width=10 BoRDER=0 /></a>\n                &nbsp;(anilϵ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>8</font></sup><font size=+3><b>ಆಯ&nbsp;&nbsp;\n    aaya    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Postposition</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಸಾಮಾನ್ಯವಾಗಿ ಶಿವಳ್ಳಿ ಬ್ರಾಹ್ಮಣ ಕುಲನಾಮಗಳ ಅಂತ್ಯದಲ್ಲಿ ಬರುವ ಪರಸರ್ಗ;<sup>1</sup><b>ಆಯೆ</b> \'ಅವನು\' ಎಂಬುದರ ರೂಪಭೇದ</TD><TD valign=top>The postposition appended usually in a shivalli Brahmin’s surname;A variant of <sup>1</sup><b>aaye</b> \'he’</TD></TR>      </TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>-ಒಲು&nbsp;&nbsp;\n    -olu    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;North common harijan tribal jain dialect. &nbsp;Pancavati Raamaayana Vaali Sugreevera Kaalago (by Sankayya Bhagavatha; Ed. T. Keshava Bhatta). &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Suffix</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಕ್ರಿಯಾ ರೂಪಗಳ ಪ್ರಥಮ ಪುರುಷ ಸ್ತ್ರೀಲಿಂಗ ಏಕವಚನ ಪ್ರತ್ಯಯ</TD><TD valign=top>Third person feminine singular suffix of verbal forms</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Common Harijan Tribal Jain</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000087");\'>\n                -ಅಲ್</a>\n                &nbsp;(-alụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North brahmin Dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000086");\'>\n                -ಅಳ್</a>\n                &nbsp;(-aḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North common harijan tribal jain dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000089");\'>\n                -ಒಳು</a>\n                &nbsp;(-oḷu).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000091");\'>\n                -ಓಲು</a>\n                &nbsp;(-oolu).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Pancavati Raamaayana Vaali Sugreevera Kaalago (by Sankayya Bhagavatha; Ed. T. Keshava Bhatta)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000089");\'>\n                -ಒಳು</a>\n                &nbsp;(-oḷu).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000091");\'>\n                -ಓಲು</a>\n                &nbsp;(-oolu).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Rare occurance</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2060000000088");\'>\n                -ಆಳ್</a>\n                &nbsp;(-aaḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South common harijan tribal jain dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2060000000088");\'>\n                -ಆಳ್</a>\n                &nbsp;(-aaḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Southern dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000086");\'>\n                -ಅಳ್</a>\n                &nbsp;(-aḷụ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>EXAMPLES</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>battaḷụ/battalụ/battaaḷụ/battoḷu/battolu/battoolu<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>2</font></sup><font size=+3><b>ಬಲಂಬಾಯಿ&nbsp;&nbsp;\n    balambaayi    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Dictionary of Rev. Manner. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>The bamboo in a roof at the entrance of a house</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Dictionary of Rev. Manner</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("50040000000046");\'>\n                ಬಲಬಾಯಿ</a>\n                &nbsp;(balabaayi).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>-ದೆ<img src=images/EBig.JPG /><img src=images/LBig.JPG width=15 height=25/>&nbsp;&nbsp;\n    -dϵϵ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Northen Dialects. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Particle</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ನಿರಾಸೆ, ಅಸಹಾಯಕಸ್ಥಿತಿ, ಪಶ್ಚಾತ್ತಾಪ ಮೊದಲಾದವುಗಳನ್ನು ಸೂಚಿಸುವ ಘಟಕ</TD><TD valign=top>An element added at the end of an expression to indicate disappointment, helplessness, repulsion etc</TD></TR>      </TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅಕ್ಕ&nbsp;&nbsp;\n    akka    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun, Vocative</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಅಕ್ಕಾ ! ಹಿರಿಯ ಸೋದರಿಯನ್ನು ಅಥವಾ ಹಿರಿಯ ಹೆಂಗಸರನ್ನು ಕರೆಯುವಾಗ ಗೌರವಾರ್ಥವಾಗಿ ಬಳಸುವ ಪದ</TD><TD valign=top>A term used in addressing one\'s elder sister or an elderly woman honorifically</TD></TR><TR><TD valign=top></TD><TD valign=top>ದೊಡ್ಡ ಮಗಳನ್ನು ಪ್ರೀತಿಯಿಂದ, ಚಿಕ್ಕ ಹುಡುಗಿಯನ್ನು ವಾತ್ಸಲ್ಯದಿಂದ ಸಂಬೋಧಿಸುವ ಪದ</TD><TD valign=top>A term used while affectionately addressing the first daughter or any young female child</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>All</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3100000000122");\'>\n                ಅಕ್ಕಾ</a>\n                &nbsp;(akkaa).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Common Harijan Tribal Jain</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3100000000123");\'>\n                ಅಕ್ಕೆ<img src=images/E.JPG height=13 width=10 BoRDER=0 /><img src=images/L.JPG height=13 width=10 BoRDER=0 /></a>\n                &nbsp;(akkϵϵ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಮುಡಿಪ್ಪಾ&nbsp;&nbsp;\n    muḍippaa    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;South common harijan tribal jain dialects. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Verb causative<a href=\'javascript:cFunc("26210000000010");\'> of <sup><font size=-2>1</font></sup>ಮುಡಿಪು&nbsp; (muḍipu) </a></i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಮುಡಿಪು;ಹೂ ಮುಡಿಯುವಂತೆಮಾಡು</TD><TD valign=top>Cause to wear flower;Cause to decorate head with flower</TD></TR><TR><TD colspan=3><b><i>Northen Dialects, Figurative, Verb causative<a href=\'javascript:cFunc("26210000000010");\'> of <sup><font size=-2>1</font></sup>ಮುಡಿಪು&nbsp; (muḍipu) </a></i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಸುಂದರಗೊಳಿಸು</TD><TD valign=top>Decorate;Beautify</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North brahmin Dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("2621000000006");\'>\n                ಮುಡಿಪೋ</a>\n                &nbsp;(muḍipoo).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North common harijan tribal jain dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("2621000000004");\'>\n                ಮುಡಿಪಾ</a>\n                &nbsp;(muḍipaa).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South brahmin dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("2621000000007");\'>\n                ಮುಡಿಪ್ಪೋ</a>\n                &nbsp;(muḍippoo).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಬುಲೆಪಾ&nbsp;&nbsp;\n    bulepaa    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Common Harijan Tribal. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>10<a href=\'javascript:cFunc("23520000000022");\'> of ಬುಲೆ&nbsp; (bule) </a></i></b></TD></TR><TR><TD valign=top></TD></TR><TR><TD colspan=3><b><i>South brahmin dialect, Verb causative<a href=\'javascript:cFunc("23520000000022");\'> of ಬುಲೆ&nbsp; (bule) </a></i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಬೆಳೆಯಿಸು;ಬೆಳೆಯುವಂತೆ ಮಾಡು;ಬೆಳೆಸು</TD><TD valign=top>Grow (crops);Make grow;Rear</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North brahmin Dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("23500000000041a");\'>\n                ಬೊಳೆಪಾ</a>\n                &nbsp;(boḷepaa).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("23500000000041b");\'>\n                ಬುಳೆಪಾ</a>\n                &nbsp;(buḷepaa).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South brahmin dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("23500000000041c");\'>\n                ಬುಳೆಪ್ಪೋ</a>\n                &nbsp;(buḷeppoo).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South common harijan tribal jain dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("23500000000040");\'>\n                ಬುಳೆಪ್ಪಾ</a>\n                &nbsp;(buḷeppaa).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Proverb</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಮಗಲೆನ್ ಪುಗರ್ದ್ ಬುಲೆಪಾವೊಡ್ಚಿ ಮಗನ್ ನೆರ್<img src=images/E.JPG width=0 />ದ್ ಬುಲೆಪಾವೊದ್ಚಿ.&nbsp;magalenụ pugardụ bulepaavoḍci maganụ nerụdụ bulepaavodci.&nbsp;ಮಗಳನ್ನು ಹೊಗಳಿ ಬೆಳೆಸಬೇಡ ಮಗನನ್ನು ಗದರಿಸಿ ಬೆಳೆಸಬೇಡ.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Saying</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ನಮನ್ ಬುಳೆಪಾದು ಸಾಂಕ್<img src=images/E.JPG width=0 />ದ್.&nbsp;namanụ buḷepaadu saaṅkụdụ.&nbsp;ನಮ್ಮನ್ನು ಬೆಳೆಸಿ ಸಾಕಿ.<br></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>1</font></sup><font size=+3><b>-ಅಳ್&nbsp;&nbsp;\n    -aḷụ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;North brahmin Dialect. &nbsp;Southern dialects. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Suffix</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಕ್ರಿಯಾ ರೂಪಗಳ ಪ್ರಥಮ ಪುರುಷ ಸ್ತ್ರೀಲಿಂಗ ಏಕವಚನ ಪ್ರತ್ಯಯ</TD><TD valign=top>Third person feminine singular suffix of verbal forms</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Common Harijan Tribal Jain</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000087");\'>\n                -ಅಲ್</a>\n                &nbsp;(-alụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North common harijan tribal jain dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000089");\'>\n                -ಒಳು</a>\n                &nbsp;(-oḷu).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("2060000000090");\'>\n                -ಒಲು</a>\n                &nbsp;(-olu).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000091");\'>\n                -ಓಲು</a>\n                &nbsp;(-oolu).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Pancavati Raamaayana Vaali Sugreevera Kaalago (by Sankayya Bhagavatha; Ed. T. Keshava Bhatta)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000089");\'>\n                -ಒಳು</a>\n                &nbsp;(-oḷu).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("2060000000090");\'>\n                -ಒಲು</a>\n                &nbsp;(-olu).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("2060000000091");\'>\n                -ಓಲು</a>\n                &nbsp;(-oolu).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Rare occurance</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2060000000088");\'>\n                -ಆಳ್</a>\n                &nbsp;(-aaḷụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South common harijan tribal jain dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2060000000088");\'>\n                -ಆಳ್</a>\n                &nbsp;(-aaḷụ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>EXAMPLES</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>battaḷụ/battalụ/battaaḷụ/battoḷu/battolu/battoolu<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>she )came ;pooyaḷU /pooyalU (she )went<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಆವಾಡ್&nbsp;&nbsp;\n    aavaaḍụ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Rare occurance. &nbsp;South common harijan tribal dialects. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Permissive, Verb neuter<a href=\'javascript:cFunc("20600000000228");\'> of <sup><font size=-2>2</font></sup>ಆ&nbsp; (aa) </a></i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಆಗಲಿ</TD><TD valign=top>Let it be so</TD></TR><TR><TD valign=top></TD><TD valign=top>ಹಾರೈಕೆ;ಅನುಮೋದನೆ;ಆಜ್ಞೆ ಮೊದಲಾದ ಅರ್ಥಗಳನ್ನು ಸೂಚಿಸುವ ಪದ</TD><TD valign=top>Word used to express one’s desire, agreement, command</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South common harijan tribal dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("26600000000136");\'>\n                ಆವಡ್</a>\n                &nbsp;(aavaḍụ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Saying</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಆವಡ್ ಪೋವಡ್ ಮಲ್ಪುನವು ಮಲ್ಪೊಡೆ.&nbsp;aavaḍụ poovaḍụ malpunavu malpoḍe.&nbsp;ಆಗಲಿ ಹೋಗಲಿ ಮಾಡುವುದನ್ನು ಮಾಡಲೇ ಬೇಕು.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>EXAMPLES</b></TD></TR><TR><TD><i><b>1.</TD><TD COLSPAN=2>aavaḍụ may (you) prosper well, let it be well done aa kelasa aavaḍụ, let that work continue</TD></TR><TR><TD><i><b>2.</TD><TD COLSPAN=2>vaadya aavaḍụ, let the pipers blow pipes<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>aa   aḍụ.<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>-ಅ<img src=images/EBig.JPG /><img src=images/E.JPG width=0 />ನ್ನೆ&nbsp;&nbsp;\n    -ụnne    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Common Harijan Tribal Jain. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Suffix</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಬಳಿಕ;ಮೇಲೆ;ಕೂಡಲೇ;ಕ್ರಿಯೆ ನಡೆದೊಡನೆ ಎ೦ಬರ್ಥದ ಕೃದ೦ತಾವ್ಯಯವನ್ನು ಸಾಧಿಸಲು ಸೇರಿಸುವ ಪ್ರತ್ಯಯ</TD><TD valign=top>After doing etc;A suffix added to obtain indeclinable participle meaning subsequent to an action</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Brahmin dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("3720000000010");\'>\n                -ಅ<img src=images/E.JPG height=13 width=10 BoRDER=0 /><img src=images/E.JPG height=0 width=0 BORDER=0 />ಣ್ಣೆ</a>\n                &nbsp;(-ụṇṇe).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("372000000009");\'>\n                -ಉಣ್ಣೆ</a>\n                &nbsp;(-uṇṇe).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Common Harijan Tribal Jain</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("372000000006");\'>\n                -ಉನ್ನೆ</a>\n                &nbsp;(-unne).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("372000000008");\'>\n                -ಉನೆ</a>\n                &nbsp;(-une).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>EXAMPLES</b></TD></TR><TR><TD><i><b>1.</TD><TD COLSPAN=2>barepunne, barepuṇṇe after writing; immediately after writing</TD></TR><TR><TD><i><b>2.</TD><TD COLSPAN=2>poopunne, poopuṇṇe after going; immediately after going<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅತಿಯುಕ್ತಿ ( ಕುಳು),&nbsp;&nbsp;\n    atiyukti ( kuḷu),    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ವಿವಿಧ ಯುಕ್ತಿಗಳು</TD><TD valign=top>Varieties of means and devices</TD></TR>      </TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>1</font></sup><font size=+3><b>ಅದ್&nbsp;&nbsp;\n    adụ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Rare occurance. &nbsp;South West harijan trial dialects. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>10</i></b></TD></TR><TR><TD valign=top></TD></TR><TR><TD colspan=3><b><i> , Pronoun, Remote, Singular</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಅದು</TD><TD valign=top>That</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Ta.,Ma.atu;Ko.adu;Ha.aduśe,it;Te.adiid.;Kol.;ṇk.,Pa.;Ga.,Go.ad.id.,Kur.add;Mal.ath<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಆಸಾಮಿ&nbsp;&nbsp;\n    aasaami    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಜನ;ವ್ಯಕ್ತಿ</TD><TD valign=top>Individual;A person</TD></TR><TR><TD valign=top></TD><TD valign=top>ಗಿರಾಕಿ</TD><TD valign=top>A customer</TD></TR><TR><TD colspan=3><b><i>Figurative, Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>A rogue;A cunning fellow</TD></TR><TR><TD colspan=3><b><i>Dictionary of Rev. Manner, Figurative, Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಸಾಲಗಾರ</TD><TD valign=top>A debtor</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Saying</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಆಸಾಮಿ ದೊಡ್ಡು ಲಕ್ಕಾಯೆ ಪಿದ್ಚೊ ಪಾಡ್ಯೆ.&nbsp;aasaami doḍḍu lakkaaye pidco paaḍye.&nbsp;ಆಸಾಮಿ ಹಣ ಕದ್ದ ಓಡಿ ಹೋದ.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Ar. Aasaami.<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ರುಯಿ&nbsp;&nbsp;\n    ruyi    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಹಳೆಯ ಕಾಲದ ಒಂದು ಅತಿ ಚಿಕ್ಕ ನಾಣ್ಯ;ಪೈ;ರೂಪಾಯಿಯ ೧೯೨ನೇ ಒಂದು ಭಾಗ</TD><TD valign=top>An old paisa equal to part of a rupee</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>All</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("27390000000024");\'>\n                ರುವಿ</a>\n                &nbsp;(ruvi).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Proverb</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ರುಯಿತ್ತ ಪುಚ್ಚೆ<img src=images/EBig.JPG width=10 height=13 /> ಪಣವುದ ನೆಯಿ ತಿಂದ್O<img src=images/E.JPG width=0 />ಡ್<img src=images/E.JPG width=0 />ಗೆ<img src=images/EBig.JPG width=10 height=13 />.&nbsp;ruyitta puccϵ paṇavuda neyi tindụṇḍụgϵ.&nbsp;ಒಂದು ಪೈಸೆ ಬೆಲೆಯ ಬೆಕ್ಕು ಒಂದು ಚಿನ್ನದ ನಾಣ್ಯದ ಬೆಲೆಯ ತುಪ್ಪ ತಿಂದಿತಂತೆ<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Saying</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ರುಯಿ ಕೂಡುದೇ ರುಪಾಯಿ ಆಪುನಿ.&nbsp;ruyi kuuḍudee rupaayi aapuni.&nbsp;ಪೈಸೆಗಳು ಸೇರಿಯೇ ರೂಪಾಯಿ ಆಗುವುದು.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Ka.ruvi.<br/></TD></TR></TABLE><br></BODY>\n</html>\n')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>2</font></sup><font size=+3><b>ಆಜ್ಲೆ<img src=images/EBig.JPG />&nbsp;&nbsp;\n    aajlϵ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>೬೦ ಸೇರು ಬೀಜ ಬಿತ್ತಲು ಬೇಕಾಗುವಷ್ಟು ಸ್ಥಳ</TD><TD valign=top>A field with an area where eers of seeds can be sown</TD></TR>      </TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅಯ್ತ ಕರಲ್ ದೆತ್ತ್<img src=images/E.JPG width=0 />ದ್ ಉಜರಂದ ಕಂಬಗ್ ಕಟ್ಟುವೆ<img src=images/EBig.JPG />&nbsp;&nbsp;\n    ayta karalụ dettụdụ ujaranda kambagụ kaṭṭuvϵ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Dictionary of Rev. Manner. &nbsp;Folktale. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಅದರ ಕರುಳು ತೆಗೆದು ವಜ್ರದ ಕ೦ಬಕ್ಕೆ ಕಟ್ಟುವೆ</TD></TR>      </TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಗೋವು&nbsp;&nbsp;\n    goovu    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಹಸು;ದನ;ಗೋವು</TD><TD valign=top>A cow</TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಜಾನುವಾರು</TD><TD valign=top>Cattle</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>All</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("11480000000026");\'>\n                ಗೋ</a>\n                &nbsp;(goo).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(1.9.9.,83)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಭೂಮಿ ಪಸೆಯೇರುವೊ ಗೋಮಹಿಷೀತಾ ಕ್ಷೀರರೆಸಂಟ್.&nbsp;bhuumi paseyeeruvo goomahiṣiitaa kṣiiraresaṇṭụ.&nbsp;ಹಸು ಎಮ್ಮೆಗಳ ಕ್ಷೀರರಸದಲ್ಲಿ (ಹಾಲಿನಿಂದ) ಭೂಮಿ ನೆನೆಯುತ್ತದೆ.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Kv.(10.49,56)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಅಯೆತುತ್ತಮೊ ಭಿಕ್ಷುಪದಾಸ್ಪರ್ಶೋ ಗೋಸ್ಪರ್ಶೊಲ ಸೌಖ್ಯೋ.&nbsp;ayetuttamo bhikṣupadaasparśoo goosparśola saukhyoo.&nbsp;ಅದಕ್ಕಿಂತಲೂ ಭಿಕ್ಷು (ಸಾಧು) ಗಳ ಪಾದಸ್ಪರ್ಶ ಶ್ರೇಷ್ಠವಾದುದು ಹಸುಗಳ ಸ್ಪರ್ಶವೂ ಸೌಖ್ಯಕರವಾದುದು.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Kv.(9.76,50)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಸ್ವರ್ಣೊ ಗೋವು ಗಜಾಶ್ವೊ ಮಂದಿರೊ.&nbsp;svarṇo goovu gajaaśvo mandiro ....,.&nbsp;ಚಿನ್ನ ಹಸು ಆನೆ ಕುದುರೆ ಮನೆ ....(ದಾನಯೋಗ್ಯ ವಸ್ತುಗಳು.)<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Paaddana, Tulu folk literature</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಗೋವು ಮೇಪಿ ಗೋವಲೆರೆ<img src=images/EBig.JPG width=10 height=13 /> ಜೋಕುಲು ಉರಲ್ ಪಾಡುನ ರಾಜಾವೆ ಮಡ್ಯಲನ ಜಕ್ಕೆಲ್<img src=images/E.JPG width=0 />ಡ್ ಪುರೆಲ್<img src=images/E.JPG width=0 />ವಲ್ ಕನ್ಯಗೆ<img src=images/EBig.JPG width=10 height=13 /> ಇಂದ್<img src=images/E.JPG width=0 />ದ್.&nbsp;goovu meepi goovalerϵ jookulu uralụ paaḍuna raajaave maḍyalana jakkelụḍụ purelụvalụ kanyagϵ indụdụ.&nbsp;ದನ ಮೇಯಿಸುವ ಗೋಪಾಲ ಹುಡುಗರು ರಾಗ ಹಾಕುತ್ತಾರೆ ರಾಜನೇ ಕನ್ಯಗೆ ಮಡಿವಾಳನ ಮಡಿಲಲ್ಲಿ ಹೊರಳಾಡುತ್ತಿದ್ದಾಳೆ ಎಂದು.<br>ಗೋವುಟು ಮೇಲಪೊ ಉದ್ಯೊಬೆಂದ್O<img src=images/E.JPG width=0 />ಡ್ ಕಾರಿ ಕಬಿಲ್ಚಿಗೋವು.&nbsp;goovuṭu meelapo udyobendụṇḍụ kaari kabilcigoovu.&nbsp;ಹಸುಗಳಲ್ಲಿ ಶ್ರೇಷ್ಠವಾದ ಕಾರಿ ಕಪಿಲೆ ಎಂಬ ಗೋವುಗಳು ಸೃಷ್ಟಿಯಾದವು.<br>ಕಂಜಿದ ಬಲ್ಲ್ ತೊರಿತ್ ಪತ್<img src=images/E.JPG width=0 />ದೆರಾ ಓ ಬಾಲಕೃಷ್ಣೆ ಗೋವುಕಂಜಿಲೆ<img src=images/EBig.JPG width=10 height=13 /> ಪಾಪ ಕಟಿಯೆರಾ.&nbsp;kañjida ballụ toritụ patụderaa oo baalakṛṣṇe goovukañjilϵ paapa kaṭiyeraa.&nbsp;ಕರುವಿನ ಹಗ್ಗವನ್ನು ಕಾಲಲ್ಲಿ ತುಳಿದು ಹಿಡಿದರು ಬಾಲಕೃಷ್ಣ ಗೋವು ಕರುಗಳ ಪಾಪ ಕಟ್ಟಿಕೊಂಡರು.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Skt.goo.<br/></TD></TR></TABLE><br></BODY>\n</html>')
# ,parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಇಷ್ಟಬುದ್ಧಿ&nbsp;&nbsp;\n    iṣṭabuddhi    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಇಷ್ಟಬುದ್ಧಿ;ಹಿತವಾದ ವಿವೇಚನೆ(?);ಪ್ರೀತಿ</TD><TD valign=top>Pleasant discretion(?);Affection</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(3.13.9,313)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಹಿರಣ್ಯಾಕ್ಷೆನಾಂದಿಷ್ಟ ಬುದ್ಧಿಟೆ ನಾಮಕ್ರಣೊಡ್<img src=images/E.JPG width=0 />ಸ್ಟಿಂಚ ವೆಂದೆರ್ ಸತ್ಕ್ರಿಯೆ.&nbsp;hiraṇyaakṣenaandiṣṭa buddhiṭe naamakraṇoḍụsṭiñca venderụ satkriye.&nbsp;ಹಿರಣಾಕ್ಷನೆಂದು ಹಿತವಾದ ವಿವೇಚನೆಯಿಂದ (?) ನಾಮಕರಣ ಮಾಡಿ ಸತ್ಕ್ರಿಯೆಗಳನ್ನು ಮಾಡಿದರು.<br></TD></TR></TABLE><br></BODY>\n</html>')
# ]
# word = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಎರ್ಮೆ<img src=images/EBig.JPG />&nbsp;&nbsp;\n    ermϵ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಎಮ್ಮೆ</TD><TD valign=top>A she buffalo</TD></TR><TR><TD colspan=3><b><i>Figurative, Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಬೊಜ್ಜು ಮೈಯ ಹೆಣ್ಣು</TD><TD valign=top>A stout and fat woman</TD></TR><TR><TD colspan=3><b><i>Northen Dialects, Figurative, Noun</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ದಪ್ಪವಾದುದು</TD><TD valign=top>A stout object</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Northen Dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("4620000000011");\'>\n                ಎಮ್ಮೆ<img src=images/E.JPG height=13 width=10 BoRDER=0 /></a>\n                &nbsp;(emmϵ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Rare occurance</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("4620000000011");\'>\n                ಎಮ್ಮೆ<img src=images/E.JPG height=13 width=10 BoRDER=0 /></a>\n                &nbsp;(emmϵ).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("4620000000012");\'>\n                ಎರ್ಮೆಚ್ಚಿ</a>\n                &nbsp;(ermecci).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>South West harijan trial dialects</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("4620000000012");\'>\n                ಎರ್ಮೆಚ್ಚಿ</a>\n                &nbsp;(ermecci).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Phrase</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಎರ್ಮೆತ ಪೇರ್ ಪರ್ನಾಯೆ.&nbsp;ermeta peerụ parnaaye.&nbsp;ಎಮ್ಮೆಯ ಹಾಲು ಕುಡಿದವನು ; ಮಂದಬುದ್ದಿಯವನು ; ಮಂದಚಲನೆಯವನು ; ಸೋಮಾರಿ.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Proverb</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಅಳೆಕ್ಕ್ ಬತ್ತ್<img src=images/E.JPG width=0 />ನಾಯಗ್ ಎರ್ಮೆತ ಕ್ರಯೊ ದಾಯೆ.&nbsp;aḷekkụ battụnaayagụ ermeta krayo daaye.&nbsp;ಮಜ್ಜಿಗೆಗೆ ಬಂದವನಿಗೆ ಎಮ್ಮೆಯ ಬೆಲೆ ಏತಕ್ಕೆ?<br>ನೆಯಿಕ್ಕ್ ಬತ್ತ್<img src=images/E.JPG width=0 />ನಾಯೆ ಎರ್ಮೆತ ಕಣ್ಣ್ ಮಲ್ಲೆ<img src=images/EBig.JPG width=10 height=13 /> ಪಂಡೆಗೆ<img src=images/EBig.JPG width=10 height=13 />.&nbsp;neyikkụ battụnaaye ermeta kaṇṇụ mallϵ paṇḍegϵ.&nbsp;ತುಪ್ಪಕ್ಕೆ ಬಂದವನು ಎಮ್ಮೆಯ ಕಣ್ಣು ದೊಡ್ಡದು ಎಂದನಂತೆ.<br>ಸಯ್ತಿ ಎರ್ಮೆಗ್ ಅಯ್ಯಲ ಪೇರ್.&nbsp;sayti ermegụ ayyala peerụ.&nbsp;ಸತ್ತ ಎಮ್ಮೆಗೆ ಐದು ಬಳ್ಳ ಹಾಲು.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Saying</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಪೇರ್<img src=images/E.JPG width=0 />ಗ್ ಪೆತ್ತ ಕೊಜಪುಗು ಎರ್ಮೆ<img src=images/EBig.JPG width=10 height=13 />.&nbsp;peerụgụ petta kojapugu ermϵ.&nbsp;ಹಾಲಿಗೆ ಆಕಳು ಮೊಸರಿಗೆ ಎಮ್ಮೆ.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Ta.erumai;Ma.erima,eruma;Ko.im;Ka.,Kod.emme;Te.enumu;Go.ermii.<br/></TD></TR></TABLE><br></BODY>\n</html>')
# word1 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>1</font></sup><font size=+3><b>ಕಡೊ&nbsp;&nbsp;\n    kaḍo    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Srii Bhagavato (Ed. Venktataraja Puninchattaya). &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Verb active</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಕಳುಹಿಸು</TD><TD valign=top>Send</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Paaddana, Tulu folk literature</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("6200000000045");\'>\n                ಕಡಾ</a>\n                &nbsp;(kaḍaa).&nbsp;&nbsp;                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("6200000000046");\'>\n                ಕಡ</a>\n                &nbsp;(kaḍa).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>Srii Bhagavato (Ed. Venktataraja Puninchattaya)</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("6200000000043");\'>\n                ಕಡಾ</a>\n                &nbsp;(kaḍaa).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(1.11.29,18)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ವೆರ್ತಾಡೆಕ್ ದೂತೆರೆನಿನ್ ಕಡೋಸ್ಟ್.&nbsp;vertaaḍekụ duutereninụ kaḍoosṭụụ.&nbsp;ಆ ಮೇಲೆ ಅಲ್ಲಿಗೆ ದೂತರನ್ನು ಕಳುಹಿಸಿ.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Bhagavato.(1.6.19,56)</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಬ್ರಹ್ಮಾಸ್ರೊಮೀ ತೊೞ್<img src=images/E.JPG width=0 />ಸ್ತೀಯ್ಯೆ ಪಾರ್ಥಶಿರಸ್ಸಿನೀ ಕತ್ತರೀಪಿಲನಾಂದನುಜ್ಞೆನನುಗ್ರಹೀತ್ ಕಡಾತೆನಾ.&nbsp;brahmaastromii toḻụstiiyye paarthaśirassinii kattariipilanaandanujñenanugrahiitụ kaḍaatenaa.&nbsp;ಬ್ರಹ್ಮಾಸ್ತ್ರವನ್ನು ತೊಟ್ಟು ನೀನೆ ಅರ್ಜುನನ ತಲೆಯನ್ನು ಕತ್ತರಿಸು ಎಂದು ಆಜ್ಞೆಯನ್ನು ಕೊಟ್ಟು ಕಳುಹಿಸಿದನು.<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Paaddana, Tulu folk literature</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಎನನೊರ ಕಡಾಲೆ ಪೆರಿಂಜಗುತ್ತುನೊರ ಒರಿಪಾಲೆ.&nbsp;enanora kaḍaale periñjaguttunora oripaale.&nbsp;ನನ್ನನ್ನೊಂದು ಸಲ ಕಳುಹಿಸಿರಿ ಪೆರಿಂಜಗುತ್ತನ್ನು ಉಳಿಸಿರಿ.<br>ದಾನೆಲ ಮಲ್ಪುನದೆ ಕನ್ಯಗ ತಿಮ್ಮನ್ನ ಅಜಿಲೆರ್ ಕಡಾಯಿ ವಾಲೆದೆ.&nbsp;daanela malpunade kanyaga timmanna ajilerụ kaḍaayi vaalede.&nbsp;ಏನು ಮಾಡಲಿಯಪ್ಪಾ ಕನ್ಯಗೆ ತಿಮ್ಮಣ್ಣ ಅಜಿಲರು ಕಳುಹಿಸಿದ ಓಲೆಯಲ್ಲವೇ!<br>ಮಿತ್ತ್<img src=images/E.JPG width=0 />ಮೇಲ್ ರಾಜ್ಯೊಗ್ ಓಲೆ ಕೊರ್ದು ಕಡದೆರ್.&nbsp;mittụmeelụ raajyogụ oole kordu kaḍaderụ.&nbsp;(ಗಟ್ಟದ) ಮೇಲಿನ ರಾಜ್ಯಕ್ಕೆ ಓಲೆಕೊಟ್ಟು ಕಳುಹಿಸಿದರು.<br></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>Language References</b></TD></TR><TR><TD><i><b></TD><TD COLSPAN=2>Ta.kaṭattu.kaṭavucausetogo;Ma.kaṭakkuka;Te.kaṭapu.<br/></TD></TR></TABLE><br></BODY>\n</html>')
# word3 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅ<img src=images/EBig.JPG />o<img src=images/E.JPG width=0 />ದ್&nbsp;&nbsp;\n    ụndụ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;Southern dialects. &nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Indeclinable participle<a href=\'javascript:cFunc("8100000000408");\'> of ಅ<img src=images/E.JPG height=13 width=10 BoRDER=0 /><img src=images/E.JPG height=0 width=0 BORDER=0 />ನ್&nbsp; (ụnụ) </a></i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಉದ್ಧರಣ ಸೂಚಕ ಉಪಪದ;\'ಅಂತ\', \'ಎಂದು\' ಮೊದಲಾದ ಅರ್ಥ ಕೊಡುವ \'ಅ<img src=images/E.JPG height=13 width=10 BoRDER=0 /><img src=images/E.JPG height=0 width=0 BORDER=0 />ನ್\' ಎನ್ನುವ ಕ್ರಿಯಾ ಧಾತುವಿನಿನಿಂದ ಸಾಧಿತವಾದ ಕೃದಂತಾವ್ಯಯ</TD><TD valign=top>A quotative form meaning \'like this\', \'so\'  to denote the termination of a quotation \'ụnụ\'</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North brahmin Dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("10000000020");\'>\n                ಅ<img src=images/E.JPG height=13 width=10 BoRDER=0 />o<img src=images/E.JPG height=0 width=0 BORDER=0 />ತ್</a>\n                &nbsp;(ụntụ).&nbsp;&nbsp;</TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>North common harijan tribal jain dialect</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                                <a href=\'javascript:cFunc("10000000016");\'>\n                ಅ<img src=images/E.JPG height=13 width=10 BoRDER=0 />o<img src=images/E.JPG height=0 width=0 BORDER=0 />ದ್</a>\n                &nbsp;(ụndụ).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("10000000017");\'>\n                ಅ<img src=images/E.JPG height=13 width=10 BoRDER=0 />o<img src=images/E.JPG height=0 width=0 BORDER=0 />ದ್<img src=images/E.JPG height=0 width=0 BORDER=0 />ದ್</a>\n                &nbsp;(ụndụdụ).&nbsp;&nbsp;                <sup><font size=-2>1</font></sup>                <a href=\'javascript:cFunc("10000000018");\'>\n                ಇಂದ್</a>\n                &nbsp;(indụ).&nbsp;&nbsp;                                <a href=\'javascript:cFunc("10000000019");\'>\n                ಇಂದ್<img src=images/E.JPG height=0 width=0 BORDER=0 />ದ್</a>\n                &nbsp;(indụdụ).&nbsp;&nbsp;<br/></TD></TR></TABLE><br></BODY>\n</html>')
# word2 = parse_html('<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1>2</font></sup><font size=+3><b>ಬುಡ್&nbsp;&nbsp;\n    buḍụ    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i>Verb active</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಬಿಡು;ತ್ಯಜಿಸು</TD><TD valign=top>Drop (idea etc);Leave;Forsake;Quit;Give up</TD></TR><TR><TD valign=top></TD><TD valign=top>ಹೋಗಲು ಬಿಡು;ಹೋಗಲು ಅನುಮತಿ ಕೊಡು</TD><TD valign=top>Let go;Allow to go</TD></TR><TR><TD valign=top></TD><TD valign=top>ವಿಚ್ಛೇದಿಸು;ಪರಿತ್ಯಜಿಸು</TD><TD valign=top>Divorce</TD></TR><TR><TD valign=top></TD><TD valign=top>ನೀರು ಮೊದಲಾದುವುಗಳು ಹರಿಯಬಿಡು</TD><TD valign=top>Let water etc flow;allow;Let go</TD></TR><TR><TD valign=top></TD><TD valign=top>ವಜಾ ಮಾಡು;ದೂರ ಮಾಡು;ತೆಗೆದು ಹಾಕು</TD><TD valign=top>Send away;Drop;Dismiss</TD></TR><TR><TD valign=top></TD><TD valign=top>ಗುಂಡು ಹಾರಿಸು;ಗುಂಡಿಕ್ಕು</TD><TD valign=top>Shoot</TD></TR><TR><TD valign=top></TD><TD valign=top>ನಿಲ್ಲಿಸು</TD><TD valign=top>Cease;Terminate</TD></TR><TR><TD valign=top></TD><TD valign=top>ಕಡಮೆ ಮಾಡು;ಕಳೆಯು</TD><TD valign=top>Decrease (price);Deduct</TD></TR><TR><TD valign=top></TD><TD valign=top>ಕಣ್ಣು, ಬಾಯಿ ಮೊದಲಾದುವುಗಳನ್ನು ತೆರೆ</TD><TD valign=top>Open (eye, mouth etc)</TD></TR><TR><TD colspan=3><b><i>Northen Dialects, Verb active</i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ಕೆಲಸಕ್ಕೆ ಹಚ್ಚು</TD><TD valign=top>Set to work</TD></TR>      </TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>VARIATIONS (Region/Caste wise)</b></TD></TR><TR><TD>&nbsp;</TD><TD COLSPAN=2><b><i>All</i></b></TD></TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>                <sup><font size=-2>2</font></sup>                <a href=\'javascript:cFunc("2342000000006");\'>\n                ಬುಡು</a>\n                &nbsp;(buḍu).&nbsp;&nbsp;<br/></TD></TR></TABLE><br><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>REFERENCES</b></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Proverb</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ದಂಡ್<img src=images/E.JPG width=0 />ಗ್ ಸೇರ್<img src=images/E.JPG width=0 />ದ್ ಗುಂಡು ಬುಡಿಯರೆ<img src=images/EBig.JPG width=10 height=13 /> ಪೋಡ್ಯುನಿ ದಾಯೆ.&nbsp;daṇḍụgụ seerụdụ guṇḍu buḍiyarϵ pooḍyuni daaye.&nbsp;ಸೈನ್ಯಕ್ಕೆ ಸೇರಿ ಗುಂಡು ಹಾರಿಸಲಿಕ್ಕೆ ಅಂಜುವುದು ಯಾಕೆ?<br></TD></TR><TR><TD>&nbsp;&nbsp;</TD><TD COLSPAN=2><i><b>Saying</TD></TR><TD>&nbsp;&nbsp;</TD><TD>&nbsp;&nbsp;</TD><TD>ಇನಿ ಏತಾಳ್ ಕೆಲಸೊಗು ಬುಡೊಡು.&nbsp;ini eetaaḷụ kelasogu buḍoḍu.&nbsp;ಇವತ್ತು ಎಷ್ಟು ಆಳುಗಳನ್ನು ಕೆಲಸಕ್ಕೆ ಹಚ್ಚಬೇಕು?<br>ದಯಿ ಮಲ್ಲೆ<img src=images/EBig.JPG width=10 height=13 /> ಆಂಡ್ ಪೂ ಬುಡಿಯರೆ<img src=images/EBig.JPG width=10 height=13 /> ಆಂಡ್.&nbsp;dayi mallϵ aaṇḍụ puu buḍiyarϵ aaṇḍụ.&nbsp;ಗಿಡ ದೊಡ್ಡದಾಯಿತು ಹೂ ಬಿಡಲಿಕ್ಕಾಯಿತು.<br>ಕಿಲೋ ಪತ್ತ್ ರೂಪಾಯಿ ಜಾಸ್ತಿ, ಒಂತೆ<img src=images/EBig.JPG width=10 height=13 /> ಬುಡುದು ಕೊರಿ.&nbsp;kiloo pattụ ruupaayi jaasti, ontϵ buḍudu kori.&nbsp;ಕಿಲೋಗೆ ಹತ್ತು ರೂಪಾಯಿ ಜಾಸ್ತಿ, ಸ್ವಲ್ಪ ಕಡಿಮೆ ಮಾಡಿ ಕೊಡಿ.<br>ಬಾಲೆ<img src=images/EBig.JPG width=10 height=13 /> ಪಿಲಿಪಿಳಿಂದ್ ಕಣ್ಣ್ ಬುಡುದು ತೂಪುಂಡು.&nbsp;baalϵ pilipiḷindụ kaṇṇụ buḍudu tuupuṇḍu.&nbsp;ಮಗು ಪಿಳಿ ಪಿಳಿ ಎಂದು ಕಣ್ಣು ಬಿಟ್ಟು ನೋಡುತ್ತದೆ.<br>ಆಯೆ ಇತೆ<img src=images/EBig.JPG width=10 height=13 /> ಕಲಿ ಪರ್ಪುನ ಪೂರ ಬುಡಿಯೆ.&nbsp;aaye itϵ kali parpuna puura buḍiye.&nbsp;ಆತ ಈಗ ಕಳ್ಳು ಕುಡಿಯುವುದನ್ನು ಪೂರ್ತಿ ಬಿಟ್ಟುಬಿಟ್ಟ.<br>ಎಂಕುಲಾದ್ ಲೆಪ್ಪುಜೊ, ಬತ್ತಿನಕುಲೆನ್ ಬುಡ್ಪುಜೊ.&nbsp;eṅkulaadụ leppujo, battinakulenụ buḍpujo.&nbsp;ನಾವಾಗಿ ಕರೆಯುವುದಿಲ್ಲ, ಬಂದವರನ್ನು ಬಿಡುವುದಿಲ್ಲ.<br>ನಾಯಿ ತಾನ್<img src=images/E.JPG width=0 />ಲಾ ತಿನ್ಪುಜಿ ತಿನ್ನರೆಲಾ ಬುಡ್ಪುಜಿ.&nbsp;naayi taanụlaa tinpuji tinnarelaa buḍpuji.&nbsp;ನಾಯಿ ತಾನೂ ತಿನ್ನದು ತಿನ್ನಲಿಕ್ಕೂ ಬಿಡದು.<br>ಕೆಬಿಕ್ ಎಣ್ಣೆ<img src=images/EBig.JPG width=10 height=13 /> ಬುಡೊಡು.&nbsp;kebikụ eṇṇϵ buḍoḍu.&nbsp;ಕಿವಿಗೆ ಎಣ್ಣೆ ಬಿಡಬೇಕು.<br>ಪತ್ತ್ ಕೊರ್ಪೆ<img src=images/EBig.JPG width=10 height=13 /> ಪನ್ಪುನೆಡ್ದ್ ಒಂಜಿ ಕೊರ್ದು ಬುಡ್ಪುನ ಎಡ್ಡೆ<img src=images/EBig.JPG width=10 height=13 />.&nbsp;pattụ korpϵ panpuneḍdụ oñji kordu buḍpuna eḍḍϵ.&nbsp;ಹತ್ತು ಕೊಡುತ್ತೇನೆಂದು ಹೇಳುವುದಕ್ಕಿಂತ ಒಂದು ಕೊಟ್ಟುಬಿಡುವುದು ಲೇಸು.<br>ಆಯೆ ಬುಡೆದಿನ್ ಬುಡಿಯೆ.&nbsp;aaye buḍedinụ buḍiye.&nbsp;ಆತ ಹೆಂಡತಿಯನ್ನು ಬಿಟ್ಟ.<br>ಕಡ ಗೆತ್ತೊಂದಿನ ಪತ್ತ್ ರೂಪಾಯಿ ಬುಡ್ದು ಕೊರು.&nbsp;kaḍa gettondina pattụ ruupaayi buḍdu koru.&nbsp;ಸಾಲ ತೆಗೆದುಕೊಂಡ ಹತ್ತು ರೂಪಾಯಿಯನ್ನು ಬಿಟ್ಟು (ವಜಾ ಮಾಡಿ) ಕೊಡು.<br></TD></TR></TABLE><br></BODY>\n</html>')

# # for word in words:
# #     print(word['word']['english']+ ' ' + str(word['word']['id']))
# print(convert_unicode('ಗೋವು'))
# print(convert_unicode('ಬರ್ಕೆನಾ'))
# print(convert_unicode('ಕಣ್ಣ್'))
#print(word9['word']['kannada'])
# print(iskannada('-ದೆ್ೕ'))
# print(iskannada('ಜಾನೆoದ್ಪಂಟ'))
# print(convert_unicode(u'ಬಲ್ಪು'))
# print(convert_unicode(u'ಅೞಿ'))
#create_word_dump()