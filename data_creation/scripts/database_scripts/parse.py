from bs4 import BeautifulSoup
'''
TODO:
- parse all the words and look for special symbols (non english and non kannada)
- some lines seems to be missing the words, investigate
- anytime hyper text is used for words we can just the js(id) to link things (mayb)
'''
def trim(string): # could flesh this out later
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

class Word:

    def __init__(self, kannada, english, dialect):
        self.kannada = kannada
        self.english = english
        self.dialect = dialect

def parse_html(html):

    # create soup object and find the needed tags
    html_soup = BeautifulSoup(html,'html.parser')
    header = html_soup.findAll('center') # center is only used in word and dialect type display at the top
    word_text = header[0].find('b').text

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

    return Word(words[0], words[1], trim(header[1].text.replace(u"\xa0", u"")))  # Kannada, English, Dialect Type


# test_html = '<html>\n\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n<LINK href="style.css" rel="stylesheet" type="text/css">\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<BODY topmargin=1 LEFTMARGIN=1 rigntmargin="1">\n\n<TABLE WIDTH=100%>\n<TR><TD COLSPAN=3>\n<center><sup><font size=+1></font></sup><font size=+3><b>ಅತಿಯುಕ್ತಿ ( ಕುಳು),&nbsp;&nbsp;\n    atiyukti ( kuḷu),    </center></b></font><br> </TD>\n</TR>\n\n<TR><TD COLSPAN=3><center>&nbsp;&nbsp;</center></TD></TR></TABLE><br><font size=-1><TABLE WIDTH=100%><TR><TD COLSPAN=3 class=tblhead><b>MEANINGS</b></TD></TR><TR><TD colspan=3><b><i> </i></b></TD></TR><TR><TD valign=top></TD><TD valign=top>ವಿವಿಧ ಯುಕ್ತಿಗಳು</TD><TD valign=top>Varieties of means and devices</TD></TR>      </TABLE><br></BODY>\n</html>'
# word = parse_html(test_html)
# print(word.kannada)
# print(word.english)
# print(word.dialect)


raw_html_data = open('D:\projects\Pythonnnn\TuluProject\data_creation\data\\raw_html_data.txt',
                     'r',
                     encoding="utf-8")

def create_word_dump():
    words = open(
        f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\dump.txt",
        "w",
        encoding="utf-8")

    count = 0
    for html_line in raw_html_data:
        if not html_line.replace("\n","").isdigit() and not html_line == "\n":
            count += 1
            try:
                # if count == 699: # 803
                #     print(html_line)
                word = parse_html(html_line)
                data = f'{word.kannada},{word.english},{word.dialect}\n'
                words.write(data)
            except (AttributeError,IndexError):
                print("testsstttt", html_line)

def empty_pages(num):
    page0 = open(
        f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page.html",
        "w",
        encoding="utf-8")

    page1 = open(
        f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page1.html",
        "w",
        encoding="utf-8")

    count = 0
    for html_line in raw_html_data:
        if not html_line.replace("\n","").isdigit() and not html_line == "\n":
            count += 1
            try:
                if count == num: # 803 do one count down
                    page0.write(html_line)
                    page1.write(raw_html_data.readline())
                    return
            except (AttributeError,IndexError):
                print("testsstttt", html_line)

empty_pages(403)