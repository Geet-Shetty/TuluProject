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
- mean semi colon issue, quick fix might be to just not split if the semicolon count isn't the same
  but there still could be edge cases where that wouldn't work 
- fix "" empty issue in the meanings and tulus reference section {"word.english": "agarụ"}
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
    def clean_string(string):
        remove = ['\\r', '\r', '\\n', '\n'] # might actually need the double slashes
        for thing in remove:
            string = string.replace(thing,'')

        quotes = ["\\'", "\'", "\\\\'", "\\\'"]
        for thing in quotes:
            string = string.replace(thing,"'")

        space = ['\xa0', '\\xa0', '\\\\xa0']
        for thing in space:
            string = string.replace(thing, " ")
        return string

    def compactSpaces(s):
        os = ""
        for c in s:
            if c != " " or (os and os[-1] != " "):
                os += c
        return os

    string = compactSpaces(clean_string(string))
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

def img_to_unicode(tag):
    img_tags = tag.findAll('img')
    for img in img_tags:
        if not((img.has_attr('height') and img['height'] == '0') or (img.has_attr('width') and img['width'] == '0')): # ignore the tags that don't show up
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
        if index > 0 and ((ord(char_list[index-1]) >= 3200 and ord(char_list[index-1]) <= 3327) or char_list[index-1] == '>'): # insstances where the o is in a tag so check for >o
            char_list[index] = u'ಂ'

    return ''.join(char_list)
    # conversions = {u'೦': u'ಂ'}
    # for c1,c2 in conversions.items():

def create_id(supobj):
    if supobj is not None:
        return int(supobj.string.extract()) if supobj and supobj.text.isdigit() else 0
    else:
        return 0

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

    word = {'kannada': words[0], 'english': words[1], 'tulu': convert_unicode(words[0])}

    origin = trim(center_elements[1].text.replace(u"\xa0", u""))
    if len(origin):
        word['origin'] = origin

    if id:
        word['id'] = id

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
        if td.has_attr('colspan') and not td.text.isspace() and len(td.text): # its a sub header

            if len(current_definitions): # remember this is true if the length is not zero

                # add data to meanings
                if len(current_contexts['linked_context']):
                    current_contexts['linked_context']['id'] = id
                else:
                    current_contexts.pop('linked_context')
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

                current_contexts['linked_context'] = {'kannada': '', 'english': '', 'tulu': '', 'id': 0}
                current_contexts['contexts'] = list(filter(lambda context: not (context.isspace() or context == ""), header_list[:len(header_list)-1])) # this is -1 for the len because we don't want to inlude the linked context
                current_contexts['contexts'] = list(map(lambda context: trim(context), current_contexts['contexts']))
                # create link context
                link = trim(header_list[len(header_list)-1]).split('of') # all the links of far have been xxxxx of xxxxx
                l_context = trim(link[0])
                if len(l_context):
                    current_contexts['linked_context']['context'] = l_context
                link[1] = link[1].replace('\xa0', '') # don't wanna use trim because we don't wanna replace with space here
                # todo: test
                # link[1] = trim(link[1])
                words = link[1].split('(')
                kannada = trim(words[0])
                current_contexts['linked_context']['kannada'] = kannada
                current_contexts['linked_context']['english'] = trim(words[1][:len(words[1])-1]) # the len is -1 because we want to get rid of the ending )
                current_contexts['linked_context']['tulu'] = convert_unicode(kannada)
            else:

                # this is for creating the context if no linked context exists
                header_list = td.text.split(',')
                current_contexts['contexts'] = list(filter(lambda context: not (context.isspace() or context == ""), header_list))
                current_contexts['contexts'] = list(map(lambda context: trim(context), current_contexts['contexts']))

        else:
            # get meanings
            td_elements = tr.findAll('td')
            td_elements = td_elements[1:len(td_elements)] # get rid of empty td element, so the list should be length of 2
            not_empty = False
            for element in td_elements:
                if len(element):
                    not_empty = True
                    break

            if not_empty:
                if len(td_elements) == 2:
                    # if len(find_occurances(td_elements[0].text,';')) != len(find_occurances(td_elements[1].text,';')):
                    #     print(td_elements[0].text)
                    #     print(td_elements[1].text)
                    #     print('--------------')
                    # current_definitions.append({'kannada': list(map(lambda meaning: trim(meaning), td_elements[0].text.split(';'))), 'english': list(map(lambda meaning: trim(meaning),td_elements[1].text.split(';')))})
                    td_elements[0] = list(filter(lambda context: not (context.isspace() or context == ""), td_elements[0].text.split(';')))
                    td_elements[1] = list(filter(lambda context: not (context.isspace() or context == ""), td_elements[1].text.split(';')))
                    current_definitions.append({'kannada': list(map(lambda meaning: trim(meaning), td_elements[0])),'english': list(map(lambda meaning: trim(meaning), td_elements[1]))})
                elif len(td_elements) == 1:
                    elements = list(filter(lambda context: not (context.isspace() or context == ""), td_elements[0].text.split(';')))
                    data = list(map(lambda meaning: trim(meaning),elements))
                    if td_elements[0].text.isascii():
                        current_definitions.append({'english': data})
                    else:
                        current_definitions.append({'kannada': data})

    # adds the last context
    if len(current_contexts['linked_context']) and id: # if the linked context isn't empty then set the id (don't want to add id if object is empty)
        current_contexts['linked_context']['id'] = id
    else:
        current_contexts.pop('linked_context')
    current_contexts['definitions'] = current_definitions
    meanings.append(current_contexts)

    for meaning in meanings:
        if len(meaning['contexts']) == 0:
            meaning.pop('contexts')
        if len(meaning['definitions']) == 0:
            meaning.pop('definitions')
        if meaning == {}:
            meanings.remove({})

    return meanings

def create_variations(table):
    # the smaller versions of the images ex E.jpg compared to EBig.jpg is for variations
    # also have to consider if some words in it might be poorly formatted
    variations = [] # could also be the context of the word, like medicinal instead of Lexical categories
    td_elements = table.findAll('td')
    current_origin = ''
    current_words = []
    td_elements = td_elements[1:len(td_elements)] # remove first td that is just the title VARIATIONS (Region/Caste wise)
    for td in td_elements:
        if td.has_attr('colspan'): # sub header
            if len(current_origin) and len(current_words):
                variations.append({'origin': current_origin, 'words': current_words})
                current_words = []
            current_origin = trim(td.text)
        else:
            text = re.findall('\(.*?\)', td.text)  # english words stored as plain text between parathesises
            supobj = None
            counter = 0

            for child in td.children:
                if child.name == 'sup':
                    supobj = child
                elif child.name == 'a':
                    id = create_id(supobj)
                    supobj = None
                    word = trim(child.text)
                    word_obj = {'kannda': word, 'english': trim(text[counter][1:len(text[counter])-1]), 'tulu': convert_unicode(word)}
                    # the len -1 is to get rid of the ending ) for the english word, same case like in meanings
                    # also the creation of the id doesn't need the .extract but it does it anyway because its a general function
                    if id:
                        word_obj['id'] = id
                    current_words.append(word_obj)
                    counter += 1

    variations.append({'origin': current_origin, 'words': current_words})
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

    references = []
    td_elements = table.findAll('td')
    current_ref_type = ''
    current_refs = []
    td_elements = td_elements[1:len(td_elements)] # remove first td that is just the title REFERENCES
    for td in td_elements:
        if td.has_attr('colspan'):  # sub header
            if len(current_ref_type) and len(current_refs): # if neither are zero
                references.append({'reference': current_ref_type, 'sentences': current_refs})
                current_refs = []
            current_ref_type = trim(td.text)
        else:
            if td.text.isspace() or td.text == "": # if td is empty
                continue

            text = ''
            print(len(list(td.children)))
            for child in td.children:
                print(child.name)
                # print(type(child))
                # print(child.name)
                # print(type(child))
                if child.string is not None:
                    text += child.string
                elif child.text is not None:
                    text += child.text
                print(text)
                if child.name == 'br':
                    # print(text)
                    # nbsp is a space character that usually breaks up the different languages but sections with more than one saying kannada and tulu are not split by nbsp
                    sentences = text.split('\xa0')
                    sentences = list(map(lambda sentence: trim(sentence), sentences))
                    current_refs.append({'tulu': convert_unicode(sentences[0]), 'english': sentences[1], 'kannada': sentences[2]})
                    text = ''
                # print('---------')

            if text != '': # have to do this because for some reason sometimes the ending br tag isnt picked up
                sentences = text.split('\xa0')
                sentences = list(map(lambda sentence: trim(sentence), sentences))
                current_refs.append({'tulu': convert_unicode(sentences[0]), 'english': sentences[1], 'kannada': sentences[2]})

    references.append({'reference': current_ref_type, 'sentences': current_refs})
    return references

def create_examples(table):
    td_elements = table.findAll('td',attrs={"colspan": "2"})
    examples_text = []
    for td in td_elements:
        examples_text.append(trim(td.text))
    return examples_text

def create_language_refs(table): # assumes only one line, true for the current data set
    return trim(table.find('td',attrs={"colspan": "2"}).text)

def parse_html(html):

    # create soup object and find the needed tags
    html_soup = BeautifulSoup(correct_unicode(html),'html.parser')

    img_to_unicode(html_soup)

    table_list = html_soup.findAll('table')
    word = create_word(table_list[0])
    table_list = table_list[1:len(table_list)] # all table objects except the first one with main word

    meanings = []
    variations = []
    language_refs = ''
    examples = []
    references = []

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

    data = {}
    if len(word):
        data['word'] = word
    if len(meanings):
        data['meanings'] = meanings
    if len(variations):
        data['variations'] = variations
    if len(references):
        data['references'] = references
    if len(examples):
        data['examples'] = examples
    if len(language_refs):
        data['language_refs'] = language_refs

    return data
    # return {'word': word, 'meanings': meanings, 'variations': variations, 'references': references, 'examples': examples, 'language_refs': language_refs}
