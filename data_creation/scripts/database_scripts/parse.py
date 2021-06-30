from bs4 import BeautifulSoup

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
    html_soup = BeautifulSoup(html,'html.parser')


    header = html_soup.findAll('center') # center is only used in word and dialect type display at the top
    word_text = header[0].find('b').text

    # website used  and image instead of '್' so this is just to add the actual unicode
    word_html = str(header[0].find('b'))
    img_html = '<img src="images/EBig.JPG"/>'
    index = word_html.find(img_html)
    if(index != -1):
        word_html = word_html[:index] + '್' + word_html[index+len(img_html):]
        word_soup = BeautifulSoup(word_html,'html.parser')
        word_text = word_soup.text

    # split kannada and english
    words = word_text.split('\xa0\xa0\n    ')
    words[1].replace(" ", "")

    return Word(words[0], words[1], trim(header[1].text.replace(u"\xa0", u" "))) # Kannada, English, Dialect Type

test_html = '<html>\n\n<head>\n<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>\n<link href="style.css" rel="stylesheet" type="text/css"/>\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<body leftmargin="1" rigntmargin="1" topmargin="1">\n\n<table width="100%">\n<tr><td colspan="3">\n<center><sup><font size="+1"></font></sup><font size="+3"><b>ಇಂಬಾಳ್  \n    imbaaḷụ    </b></font></center><br/> </td>\n</tr>\n\n<tr><td colspan="3"><center> South common harijan tribal jain dialects.   </center></td></tr></table><br/><font size="-1"><table width="100%"><tr><td class="tblhead" colspan="3"><b>MEANINGS</b></td></tr><tr><td colspan="3"><b><i>Pronoun</i></b></td></tr><tr><td valign="top"></td><td valign="top">ಇವಳು</td><td valign="top">This female person;Third person feminine singular proximate</td></tr> </table><br/><table width="100%"><tr><td class="tblhead" colspan="3"><b>VARIATIONS (Region/Caste wise)</b></td></tr><tr><td> </td><td colspan="2"><b><i>Brahmin dialect</i></b></td></tr><td> </td><td> </td><td> <a href="\'javascript:cFunc(&quot;10000000070&quot;);\'">\n                ಅ<img border="0" height="13" src="images/E.JPG" width="10"/>o<img border="0" height="0" src="images/E.JPG" width="0"/>ಬಳು</a>\n                 (ụmbaḷu).                                  <a href="\'javascript:cFunc(&quot;10000000071&quot;);\'">\n                ಇಂಬಳ್</a>\n                 (imbaḷụ).  </td><tr><td> </td><td colspan="2"><b><i>North common harijan tribal jain dialect</i></b></td></tr><td> </td><td> </td><td> <a href="\'javascript:cFunc(&quot;10000000072&quot;);\'">\n                ಅ<img border="0" height="13" src="images/E.JPG" width="10"/>o<img border="0" height="0" src="images/E.JPG" width="0"/>ಬೊಲು</a>\n                 (ụmbolu).                                  <a href="\'javascript:cFunc(&quot;10000000073&quot;);\'">\n                ಇಂಬೊಲು</a>\n                 (imbolu).  </td><tr><td> </td><td colspan="2"><b><i>South common harijan tribal jain dialects</i></b></td></tr><td> </td><td> </td><td> <a href="\'javascript:cFunc(&quot;10000000066&quot;);\'">\n                ಅ<img border="0" height="13" src="images/E.JPG" width="10"/>o<img border="0" height="0" src="images/E.JPG" width="0"/>ಬಳ್</a>\n                 (ụmbaḷụ).                                  <a href="\'javascript:cFunc(&quot;10000000067&quot;);\'">\n                ಅ<img border="0" height="13" src="images/E.JPG" width="10"/>o<img border="0" height="0" src="images/E.JPG" width="0"/>ಬಾಳ್</a>\n                 (ụmbaaḷụ).                                  <a href="\'javascript:cFunc(&quot;10000000068&quot;);\'">\n                ಇಂಬಳ್</a>\n                 (imbaḷụ).  <br/></td></table><br/><table width="100%"><tr><td class="tblhead" colspan="3"><b>Language References</b></td></tr><tr><td><i><b></b></i></td><td colspan="2">Ta. ,Ma.ivaḷ;Ko.evḷ;Ka.ivaḷ(u<br/></td></tr></table><br/></font></body>\n</html>'

# test_html = '<html>\n\n<head>\n<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>\n<link href="style.css" rel="stylesheet" type="text/css"/>\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<body leftmargin="1" rigntmargin="1" topmargin="1">\n\n<table width="100%">\n<tr><td colspan="3">\n<center><sup><font size="+1">3</font></sup><font size="+3"><b>-ಉ  \n    -u    </b></font></center><br/> </td>\n</tr>\n\n<tr><td colspan="3"><center>  </center></td></tr></table><br/><font size="-1"><table width="100%"><tr><td class="tblhead" colspan="3"><b>MEANINGS</b></td></tr><tr><td colspan="3"><b><i>Suffix</i></b></td></tr><tr><td valign="top"></td><td valign="top">ಕೃದಂತಾವ್ಯಯ ಪ್ರತ್ಯಯದ ರೂಪ ಭೇದ</td><td valign="top">Forms of indeclinable participle suffix added to participle base</td></tr> </table><br/><table width="100%"><tr><td class="tblhead" colspan="3"><b>VARIATIONS (Region/Caste wise)</b></td></tr><tr><td> </td><td colspan="2"><b><i>All</i></b></td></tr><td> </td><td> </td><td> <sup><font size="-2">2</font></sup> <a href="\'javascript:cFunc(&quot;1000000002&quot;);\'">\n                -ಅ<img border="0" height="13" src="images/E.JPG" width="10"/></a>\n                 (-ụ).  <br/></td></table><br/><table width="100%"><tr><td class="tblhead" colspan="3"><b>EXAMPLES</b></td></tr><tr><td><i><b></b></i></td><td colspan="2">battụdụ having come, barondu coming; korụdụ having given; poodu having gone, etc<br/></td></tr></table><br/></font></body>\n</html>'

# test_html = '<html>\n\n<head>\n<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>\n<link href="style.css" rel="stylesheet" type="text/css"/>\n<script type="text/javascript">function cFunc(val){top.frames["synonym"].location=\'synonym.php?search=\'+val;top.frames["similar"].location=\'similar.php?search=\'+val;top.frames["result"].location=\'detail.php?search=\'+val;}</script>\n</head>\n\n<body leftmargin="1" rigntmargin="1" topmargin="1">\n\n<table width="100%">\n<tr><td colspan="3">\n<center><sup><font size="+1">2</font></sup><font size="+3"><b>-ಅ<img src="images/EBig.JPG"/>  \n    -ụ    </b></font></center><br/> </td>\n</tr>\n\n<tr><td colspan="3"><center>  </center></td></tr></table><br/><font size="-1"><table width="100%"><tr><td class="tblhead" colspan="3"><b>MEANINGS</b></td></tr><tr><td colspan="3"><b><i>Suffix</i></b></td></tr><tr><td valign="top"></td><td valign="top">ಕೃದಂತಾವ್ಯಯ ಪ್ರತ್ಯಯದ ರೂಪ ಭೇದ</td><td valign="top">Forms of indeclinable participle suffix added to participle base</td></tr> </table><br/><table width="100%"><tr><td class="tblhead" colspan="3"><b>VARIATIONS (Region/Caste wise)</b></td></tr><tr><td> </td><td colspan="2"><b><i>All</i></b></td></tr><td> </td><td> </td><td> <sup><font size="-2">3</font></sup> <a href="\'javascript:cFunc(&quot;1000000003&quot;);\'">\n                -ಉ</a>\n                 (-u).  <br/></td></table><br/><table width="100%"><tr><td class="tblhead" colspan="3"><b>EXAMPLES</b></td></tr><tr><td><i><b></b></i></td><td colspan="2">battụdụ having come, barondu coming; korụdụ having given; poodu having gone, etc<br/></td></tr></table><br/></font></body>\n</html>'

word = parse_html(test_html)

print(word.kannada)
print(word.english)
print(word.dialect)

