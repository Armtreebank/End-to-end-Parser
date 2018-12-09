import re
from xml.dom import minidom

class Dictionary:
  PATH = '/dictionaries'
  
  def __init__(self, name):
    if not name:
      raise KeyError('Please write dictionary name')
    
    fullpath = '{path}/{name}'.format(path=self.PATH, name=name)
    try:
      xml = minidom.parse(fullpath)
    except FileNotFoundError as E:
      return
      
    self.xml = xml
    self.name = name
    
  def get_word(self, sentence):
    if not hasattr(self, 'xml'):
      raise Exception('Dictionary is not initialized')
      
    itemlist = self.xml.getElementsByTagName('unit')
    for unit in itemlist:
      text_elem = unit.getElementsByTagName('p')[0]
      text = text_elem.childNodes[0].nodeValue
      match = re.match(text, sentence)
      if match:
        return {
          'word': text,
          'exist': True,
        }
    
    return {
      'word': '',
      'exist': False,
    }
      
class Punct:
  LINEAR_PUNCTUATION = {
    '0l': ('՚','\u055A',''),
    '1l': ('՛','\u055B',''),
    '2l': ('՜','\u055C','~'),
    '3l': ('՞','\u055E',''),
    '4l': ('՟','\u055F',''),
  }

  PUNCTUATION = {
    ':': ('։','\u0589',':'),
    4: ('\.\.\.\.','',''),
    3: ('\.\.\.','',''),
    'dot': ('\.','\u002E','\.'),
    'comma': (',','\u002C',','),
    '`': ('՝','\u055D','`'),
    0: ('֊','\u058A',''),
    1: ('«','',''),
    2: ('»','',''),
    5: ('—','','_'),
    6: ('֊','','\-'),
    7: ('~','',''),
    8: ('”','',''),
    9: ('֏','\u058F',''),
    10: ('\(','',''),
    11: ('\)','',''),
    12: ('\{','',''),
    13: ('\}','',''),
    14: ('\[','',''),
    15: ('\]','',''),
    16: ('\/','',''),
  }
    
  INTERNATIONAL = [ '+', '-', '%', '°С', '$', '€', '₩', '¥', '₦', '₽', '£' ]
  METRIC = [ 'կմ', 'մ', 'ժ', 'վ', 'ր', 'կգ', 'գ', 'տ' ]
    
  def __init__(self, punct):
    if punct:
      if not isinstance(punct, list):
        self.punct = [punct]
      else:
        self.punct = punct
    else:
        raise KeyError('Please write punctuation symbol.')
  
  def regex(self):
    reg_arr = []
    if self.punct:
      for p in self.punct:
        if p in self.LINEAR_PUNCTUATION:
          reg_arr += [i for i in self.LINEAR_PUNCTUATION[p] if i]
        elif p in self.PUNCTUATION:
          reg_arr += [i for i in self.PUNCTUATION[p] if i]
    else:
      return ''
    return u'|'.join(reg_arr)

  @classmethod
  def all(cls, linear=False):
    reg_arr = []
    for i in (cls.PUNCTUATION.values() if linear == False else cls.LINEAR_PUNCTUATION.values()):
        for j in i:
            if j:
              reg_arr.append(j)
    return u'|'.join( reg_arr )

  @classmethod
  def inter(cls):
    return u'|'.join( cls.INTERNATIONAL )

  @classmethod
  def metric(cls, double):
    if double:
      return u'|'.join(['{}/{}'.format(i,j) for i in cls.METRIC for j in cls.METRIC])
    else:
      return u'|'.join(cls.METRIC)

class Tokenizer:
  SEGMENTATION_RULES = [
    (1, u'(' + Punct(':').regex() + ')\s*[Ա-ՖևA-ZА-ЯЁ]+', 1), #: Ա
    (12, u'(' + Punct(4).regex() + ')\s*[Ա-ՖևA-ZА-ЯЁ]+', 4), #.... Ա
    (13, u'(' + Punct(3).regex() + ')\s*[Ա-ՖևA-ZА-ЯЁ]+', 3), #... Ա
    (2, u'(' + Punct(':').regex() + ')\s*$', 1), #:
    (22, u'(' + Punct(4).regex() + ')\s*$', 4), #....
    (23, u'(' + Punct(3).regex() + ')\s*$', 3), #...
    (3, u'[' + Punct(':').regex() + ']\s+[0-9]{1}', 1), #: 2016
    #(4, u'([' + Punct.all() + ']\s*[' + Punct([5, 6]).regex() + ']+\s*[Ա-ֆևևA-zА-яЁё0-9]+)'), #, -
    (5, u'[' + Punct.all() + ']\s*[' + Punct(1).regex() + ']{1}\s*[Ա-ֆևևA-zА-яЁё0-9]+', 1), #. <<
    (6, u'\.{1}\n', 1),
  ]
  
  TOKENIZATION_RULES = [
    (1, u'[' + Punct.inter() + ']'), # 5°С, $5, -5, +5
    (2, Punct.metric(double=True)), # 5կմ/ժ, 5մ/վ
    (3, u'[0-9]+-[ա-ֆԱ-Ֆևև]+'), #1-ին , 5-ական
    #(4, u'թ[ա-ֆև]*\.*-[ա-ֆԱ-Ֆևև]+'), #1999թ.-ին
    #(19, u'թթ.-ին|թ.-ին'),
    #(5, u'[0-9]+\s+[0-9]+'), #numbers 250 000
    (6, u'[0-9]+[\.|,|/]{1}[0-9]+'), #numbers 2.5 2,5 2/3
    (7, u'\.[0-9]+'), #numbers .5 , .08
    (7.1, u'[0-9]+'), #numbers 25
    (8, u'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'), #E-mail
    (9, u'@[a-z0-9_-]{3,}'), #nickname @gor_ar
    (10, u'[Ա-Ֆև]+[ա-ֆև]+-[Ա-Ֆև]+[ա-ֆև]+'), #Սայաթ-Նովա
    (11, u'[Ա-Ֆևа-яА-ЯЁёA-z]+-[ա-ֆև]+'), #ՀՀԿ-ական ( լավ չի, բայց ուրիշ օրինակ մտքիս չեկավ )
    (12, u'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?'), #URL
    (20, u'[ա-ֆԱ-Ֆևև]+[' + Punct.all(linear=True) + ']{1,3}'), #հեյ~(հե~յ)
    (13, u'[ա-ֆԱ-Ֆևև]+'), #simple word
    (14, u'[a-zA-Z]+'), #english word 
    (15, u'[а-яА-ЯЁё]+'), #russian word
    (16, u'\.{3,4}'), #.... , ...
    (17, u'([' + Punct.all() + ']{1})'), #all punctuations
    (18, u'([' + Punct.all(linear=True) + ']{1})'), #all linear punctuations
  ]
  
  SPECIAL_RULES = {
    'segment': [
      ( '__all__', False, u'[' + Punct(1).regex() + ']\s*[Ա-ՖևA-ZА-ЯЁ]{1}[A-zА-яЁёԱ-ֆևև\s։]+[^' + Punct(2).regex() + ']$' ), #<<bla bla: bla>> is not a segment
      #( [4], False, u'[0-9]{1}թ$' ), #1999թ.-ին is not a segment
    ],
    'token': [
      ( [4], True, u'[0-9]{1}$' ),
    ]
  }
  
  PURIFICATION_RULES = [
    ('<<', '«'),
    ('>>', '»'),
    ('(?P<w_beg>[ա-ֆԱ-Ֆևև]+)(?P<symbol>[' + Punct.all(linear=True) + ']){1}(?P<w_end>[ա-ֆԱ-Ֆևև]*)', '\g<w_beg>\g<w_end>\g<symbol>'), #LINEAR_PUNCTUATION
    ('(?P<day>[0-9]{1,4})(?P<symbol1>[' + Punct(['dot', 6, 16]).regex() + '])(?P<month>[0-9]{1,4})(?P<symbol2>[' + Punct(['dot', 6, 16]).regex() + '])(?P<year>[0-9]{1,4})',
      '\g<day> \g<symbol1> \g<month> \g<symbol2> \g<year>'), #Ամսաթվեր 20.12.2015
  ]
  
  MULTIWORD_TOKENS = [
    {
      'parent_rule': 20,
      'regex': u'^[ա-ֆԱ-Ֆևև]+[' + Punct.all(linear=True) + ']{1,3}$',
      'seperator': [ u'[ա-ֆԱ-Ֆևև]+', u'[' + Punct.all(linear=True) + ']{1}' ],
    }, # հեյ~ => 1-2.հեյ~ 1.հեյ 2.~
  ]
    
  def __init__(self, text):
    self.text = text
    self.text_length = len(text)
    self.segments = []
   
  def __str__(self):
    return self.print_()
    
  def print_(self):
    output = ''
    for s in self.segments:
      output += '{num}. {string}\n{line}\n'.format(num=s['id'], string=s['segment'], line='-' * 50)
      for t in s['tokens']:
        output += '{token}\n'.format(token=t)
      
      output += '\n'
    return output
    
  def output(self):
    return self.segments
  
  @classmethod
  def is_segment(cls, text, pointer):
    for index, r, len in cls.SEGMENTATION_RULES:
      if re.match(r, text[pointer:]):
        for s_r in cls.SPECIAL_RULES['segment']:
          if (isinstance(s_r[0], list) and index in s_r[0] ) or s_r[0] == '__all__':
            if not (( re.findall(s_r[2], text[:pointer]) and s_r[1] ) or ( not re.findall(s_r[2], text[:pointer]) and not s_r[1] )):
              return False
        return [r, len]
    return False

  @classmethod
  def find_token(cls, text, pointer):
    for index, r in cls.TOKENIZATION_RULES:
      token = re.match(r, text[pointer:])
      if token:
        for t_r in cls.SPECIAL_RULES['token']:
          if (isinstance(t_r[0], list) and index in t_r[0] ) or t_r[0] == '__all__':
            if not (( re.findall(t_r[2], text[:pointer]) and t_r[1] ) or ( not re.findall(t_r[2], text[:pointer]) and not t_r[1] )):
              return False
        return token
    return False
  
  @classmethod
  def multitoken(cls, initial_token):
    word = initial_token
    for r in cls.MULTIWORD_TOKENS:
      token = re.match(r['regex'], word)
      if token:
        multitoken = []
        for s in r['seperator']:
          split_part = re.match(s, word)
          if split_part:
            multitoken.append(split_part.group(0))
            word = word[split_part.end():]
        return multitoken
    return False
    
  def purification(self):
    for r in self.PURIFICATION_RULES:
      self.text = re.sub(r[0], r[1], self.text)
      
    self.text_length = len(self.text)
    return self
    
  def segmentation(self):
    self.purification()
    checkpoint = 0
    l = 0
    
    while(l < self.text_length):
      seg = self.is_segment(self.text[checkpoint:], l-checkpoint)
      if seg:
        punct_len = seg[-1]
        new_segment = self.text[checkpoint:(l + punct_len)]
        clean_segment = new_segment.rstrip().lstrip()
        self.segments.append({
          'segment': clean_segment,
          'id': len(self.segments)+1,
          'tokens': []
        })
        
        checkpoint = l + punct_len
        l += punct_len
      else:
        l += 1
    return self

  def tokenization(self):
    AbbreviationsDictionary = Dictionary('abbreviations.xml')
    for s in self.segments:
      l = 0
      index = 1
      
      while l < len(s['segment']):
        #Try to find the word in abbreviations dictionary
        dict_word = ''
        try:
          dict = AbbreviationsDictionary
          dict_word = dict.get_word(s['segment'][l:])
        except Exception:
          pass
        if 'exist' in dict_word and dict_word['exist'] == True:
          s['tokens'].append(( index, dict_word['word']))
          index += 1
          l += len(dict_word['word'])
        else:
          #Try to find a static rule
          token = self.find_token(s['segment'], l)
          if token:
            l += token.end()
            new_token = token.group(0)
            clean_token = new_token.rstrip().lstrip()
            
            multi = self.multitoken(clean_token)
            if multi:
              start_p = index
              end_p = start_p + len(multi) - 1
              s['tokens'].append( ('{s}-{e}'.format(s=start_p, e=end_p), clean_token) )
              for t in multi:
                s['tokens'].append( (index, t) )
                index += 1
            else:
              s['tokens'].append(( index, clean_token ))
              index += 1
          else:
            l += 1
    return self