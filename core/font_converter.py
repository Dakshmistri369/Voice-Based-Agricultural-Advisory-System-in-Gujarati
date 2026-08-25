"""
Gujarati Legacy Font (Bharati / Gopika / LMG / Shree / Krishna) to Unicode Converter.
Converts non-Unicode 8-bit encoded Gujarati PDF text into standard Gujarati Unicode (U+0A80 to U+0AFF).
"""

import re
from typing import List, Tuple

# Multi-character conjunct mappings (longest matches first)
_CONJUNCT_MAP: List[Tuple[str, str]] = [
    # Full words / Common patterns
    ("þw»f", "શુષ્ક"),
    ("{wÏÞíðu", "મુખ્યત્વે"),
    ("sYrhÞkŒ", "જરૂરિયાત"),
    ("sYrhÞkŒk", "જરૂરિયાત"),
    ("sYh", "જરૂર"),
    ("Ÿzk", "ઊંડા"),
    ("Ÿzwt", "ઊંડું"),
    ("ŸzkR", "ઊંડાઈ"),
    ("«MíkkðLkk", "પ્રસ્તાવના"),
    ("«MŒkð™k", "પ્રસ્તાવના"),
    ("y™w¢{rýfk", "અનુક્રમણિકા"),
    ("rðøkík", "વિગત"),
    ("ÃkkLkk", "પાના"),
    ("rðMŒkhku{kt", "વિસ્તારોમાં"),
    ("rðMŒkh{kt", "વિસ્તારમાં"),
    ("rðMŒkh", "વિસ્તાર"),
    ("ƒk„kÞŒe", "બાગાયતી"),
    ("ƒk„kÞŒ", "બાગાયત"),
    ("…kfku™e", "પાકોની"),
    ("…kfku", "પાકો"),
    ("…kf™e", "પાકની"),
    ("…kf", "પાક"),
    ("¾uŒe{k", "ખેતીમાં"),
    ("¾uŒe", "ખેતી"),
    ("‚eŒkV¤", "સીતાફળ"),
    ("‚h„ðku", "સરગવો"),
    ("‚h„ðk", "સરગવા"),
    ("yktƒ÷e", "આંબલી"),
    ("Vk÷‚k", "ફાલસા"),
    ("ƒe÷e", "બીલી"),
    ("òtƒw", "જાંબુ"),
    ("ytSh", "અંજીર"),
    ("„wtËk", "ગુંદા"),
    ("fh{Ëk", "કરમદા"),
    ("yk{¤k", "આમળા"),
    ("ƒkuh", "બોર"),
    ("r™Þk{f™e", "નિયામકની"),
    ("r™Þk{f", "નિયામક"),
    ("f[uhe", "કચેરી"),
    ("÷kûkrýfŒk", "લાક્ષણિકતા"),
    ("rMÚkrŒ{kt", "સ્થિતિમાં"),
    ("rMÚkrŒ", "સ્થિતિ"),
    ("yðfkþ", "અવકાશ"),
    ("yðhkuÄku", "અવરોધો"),
    ("…ÞokðhýeÞ", "પર્યાવરણીય"),
    ("ykŠÚkf", "આર્થિક"),
    ("hksMÚkk™", "રાજસ્થાન"),
    ("„wshkŒ™k", "ગુજરાતના"),
    ("„wshkŒ", "ગુજરાત"),
    ("nrhÞkýk", "હરિયાણા"),
    ("fýokxf", "કર્ણાટક"),
    ("yktÄú«Ëuþ", "આંધ્રપ્રદેશ"),
    ("r{r÷Þ™", "મિલિયન"),
    ("nuõxh{kt", "હેક્ટરમાં"),
    ("nuõxh", "હેક્ટર"),
    ("Vu÷kÞu÷ku", "ફેલાયેલો"),
    ("Vu÷kÞu÷", "ફેલાયેલ"),
    ("rðrðÄ", "વિવિધ"),
    ("hkßÞku™k", "રાજ્યોના"),
    ("hkßÞku", "રાજ્યો"),
    ("hkßÞ", "રાજ્ય"),
    ("…ht…hk„Œ", "પરંપરાગત"),
    ("ykíÞtrŒf", "આંત્યંતિક"),
    ("‚qfk", "સૂકા"),
    ("‚qhŒ", "સુરત"),
    ("‚khe", "સારી"),
    ("‚khk", "સારા"),
    ("¾kíkw", "ખાતું"),
    ("¾kŒh", "ખાતર"),
    ("s{e™", "જમીન"),
    ("ðkðuŒh", "વાવેતર"),
    ("hkusøkkhe", "રોજગારી"),
    ("WíÃkkËLk", "ઉત્પાદન"),
    ("WíÃkkËfíkk", "ઉત્પાદકતા"),

    # Vowels
    ("ykt", "આં"),
    ("ykuh", "ઔ"),
    ("yku", "ઓ"),
    ("yk", "આ"),
    ("yu", "એ"),
    ("y@", "ઐ"),
    ("y%", "ઔ"),
    ("y{kt", "અમ"),
    ("y", "અ"),
    ("Eü", "ઈ"),
    ("E", "ઇ"),
    ("W", "ઉ"),
    ("T", "ઊ"),
    ("R", "ઈ"),

    # Conjuncts & Ligatures
    ("«", "પ્ર"),
    ("¢", "ક્ર"),
    ("¿", "જ્ઞ"),
    ("Nu", "ક્ષે"),
    ("ûkuh", "ક્ષૌ"),
    ("ûku", "ક્ષો"),
    ("ûk", "ક્ષા"),
    ("û", "ક્ષ"),
    ("ºkuh", "ત્રૌ"),
    ("ºku", "ત્રો"),
    ("ºk", "ત્રા"),
    ("º", "ત્ર"),
    ("æ", "ધ્ય"),
    ("ã", "દ્ય"),
    ("ï", "શ્વ"),
    ("õx", "ક્ટ"),
    ("õ", "ક્"),
    ("MŒ", "સ્ત"),
    ("MÚk", "સ્થા"),
    ("MÚ", "સ્થ"),
    ("Míkk", "સ્તા"),
    ("Mí", "સ્ત"),
    ("M…", "સ્પ"),
    ("M™", "સ્ન"),
    ("Mð", "સ્વ"),
    ("MÞ", "સ્ય"),
    ("M¾", "સ્ખ"),
    ("ÕÞ", "લ્ય"),
    ("Õ…", "લ્પ"),
    ("ÕÃ", "લ્પ"),
    ("Õx", "લ્ટ"),
    ("Õz", "લ્ડ"),
    ("Õf", "લ્ક"),
    ("Õ„", "લ્ગ"),
    ("ÕŒ", "લ્ત"),
    ("Ãx", "પ્ટ"),
    ("ÃŒ", "પ્ત"),
    ("Ã‚", "પ્સ"),
    ("ÃÞ", "પ્ય"),
    ("Ã™", "પ્ન"),
    ("Ã÷", "પ્લ"),
    ("Ãh", "પ્ર"),
    ("Õh", "ર્લ"),
    ("fŒ", "ક્ત"),
    ("f÷", "ક્લ"),
    ("fð", "ક્વ"),
    ("fÞ", "ક્ય"),
    ("f»", "ક્ષ"),
    ("„úk", "ગ્રા"),
    ("„ú", "ગ્ર"),
    ("„™", "ગ્ન"),
    ("„Þ", "ગ્ય"),
    ("„÷", "ગ્લ"),
    ("„ð", "ગ્વ"),
    ("„{", "ગ્મ"),
    ("Äú", "ધ્ર"),
    ("Äúk", "ધ્રા"),
    ("½ú", "ઘ્ર"),
    ("ºú", "ત્ર"),
    ("å", "ઠ્ઠ"),
    ("ë", "દ્દ"),
    ("ì", "દ્વિ"),
    ("íkk", "તા"),
    ("í", "ત"),
    ("ß", "જ્ય"),
    ("Ï", "ખ્ય"),
    ("è", "ધ્"),
    ("é", "દ્ર"),
    ("Š", "ર્"),
    ("çk", "બા"),
    ("ç", "બ"),
]

# Character mappings for single consonants and vowels
_CHAR_MAP: List[Tuple[str, str]] = [
    # Full Consonants with vowel combinations
    ("òt", "જાં"), ("òk", "જા"), ("ò", "જા"),
    ("su", "જે"), ("s", "જ"), ("S", "જી"),
    ("™t", "નં"), ("™kuh", "નૌ"), ("™ku", "નો"), ("™k", "ના"), ("™u", "ને"), ("™", "ન"),
    ("…t", "પં"), ("…kuh", "પૌ"), ("…ku", "પો"), ("…k", "પા"), ("…u", "પે"), ("…", "પ"),
    ("ƒt", "બં"), ("ƒkuh", "બૌ"), ("ƒku", "બો"), ("ƒk", "બા"), ("ƒu", "બે"), ("ƒ", "બ"),
    ("¼t", "ભં"), ("¼kuh", "ભૌ"), ("¼ku", "ભો"), ("¼k", "ભા"), ("¼u", "ભે"), ("¼", "ભ"),
    ("‚t", "સં"), ("‚kuh", "સૌ"), ("‚ku", "સો"), ("‚k", "સા"), ("‚u", "સે"), ("‚", "સ"),
    ("¾t", "ખં"), ("¾kuh", "ખૌ"), ("¾ku", "ખો"), ("¾k", "ખા"), ("¾u", "ખે"), ("¾", "ખ"),
    ("„t", "ગં"), ("„kuh", "ગૌ"), ("„ku", "ગો"), ("„k", "ગા"), ("„u", "ગે"), ("„", "ગ"),
    ("½t", "ઘં"), ("½kuh", "ઘૌ"), ("½ku", "ઘો"), ("½k", "ઘા"), ("½u", "ઘે"), ("½", "ઘ"),
    ("÷t", "લં"), ("÷kuh", "લૌ"), ("÷ku", "લો"), ("÷k", "લા"), ("÷u", "લે"), ("÷", "લ"),
    ("ðt", "વં"), ("ðkuh", "વૌ"), ("ðku", "વો"), ("ðk", "વા"), ("ðu", "વે"), ("ð", "વ"),
    ("þt", "શં"), ("þkuh", "શૌ"), ("þku", "શો"), ("þk", "શા"), ("þu", "શે"), ("þ", "શ"),
    ("»t", "ષં"), ("»kuh", "ષૌ"), ("»ku", "ષો"), ("»k", "ષા"), ("»u", "ષે"), ("»", "ષ"),
    ("nt", "હં"), ("nkuh", "હૌ"), ("nku", "હો"), ("nk", "હા"), ("nu", "હે"), ("n", "હ"),
    ("¤t", "ળં"), ("¤kuh", "ળૌ"), ("¤ku", "ળો"), ("¤k", "ળા"), ("¤u", "ળે"), ("¤", "ળ"),
    ("ýt", "ણં"), ("ýkuh", "ણૌ"), ("ýku", "ણો"), ("ýk", "ણા"), ("ýu", "ણે"), ("ý", "ણ"),
    ("Út", "થં"), ("Úkuh", "થૌ"), ("Úku", "થો"), ("Úk", "થા"), ("Úu", "થે"), ("Ú", "થ"),
    ("Ët", "દં"), ("Ëkuh", "દૌ"), ("Ëku", "દો"), ("Ëk", "દા"), ("Ëu", "દે"), ("Ë", "દ"),
    ("Ät", "ધં"), ("Äkuh", "ધૌ"), ("Äku", "ધો"), ("Äk", "ધા"), ("Äu", "ધે"), ("Ä", "ધ"),
    ("xt", "ટં"), ("xkuh", "ટૌ"), ("xku", "ટો"), ("xk", "ટા"), ("xu", "ટે"), ("x", "ટ"),
    ("Xt", "ઠં"), ("Xkuh", "ઠૌ"), ("Xku", "ઠો"), ("Xk", "ઠા"), ("Xu", "ઠે"), ("X", "ઠ"),
    ("zt", "ડં"), ("zkuh", "ડૌ"), ("zku", "ડો"), ("zk", "ડા"), ("zu", "ડે"), ("z", "ડ"),
    ("Zt", "ઢં"), ("Zkuh", "ઢૌ"), ("Zku", "ઢો"), ("Zk", "ઢા"), ("Zu", "ઢે"), ("Z", "ઢ"),
    ("ft", "કં"), ("fkuh", "કૌ"), ("fku", "કો"), ("fk", "કા"), ("fu", "કે"), ("f", "ક"),
    ("Vt", "ફં"), ("Vkuh", "ફૌ"), ("Vku", "ફો"), ("Vk", "ફા"), ("Vu", "ફે"), ("V", "ફ"),
    ("Þt", "યં"), ("Þkuh", "યૌ"), ("Þku", "યો"), ("Þk", "યા"), ("Þu", "યે"), ("Þ", "ય"),
    ("ht", "રં"), ("hkuh", "રૌ"), ("hku", "રો"), ("hk", "રા"), ("hu", "રે"), ("h", "ર"),
    ("At", "છં"), ("Akuh", "છૌ"), ("Aku", "છો"), ("Ak", "છા"), ("Au", "છે"), ("A", "છ"),
    ("[t", "ચં"), ("[kuh", "ચૌ"), ("[ku", "ચો"), ("[k", "ચા"), ("[u", "ચે"), ("[", "ચ"),
    ("Ít", "ઝં"), ("Íkuh", "ઝૌ"), ("Íku", "ઝો"), ("Ík", "ઝા"), ("Íu", "ઝે"), ("Í", "ઝ"),
    ("Œt", "તં"), ("Œkuh", "તૌ"), ("Œku", "તો"), ("Œk", "તા"), ("Œu", "તે"), ("Œ", "ત"),
    ("{kt", "માં"), ("{t", "મં"), ("{kuh", "મૌ"), ("{ku", "મો"), ("{k", "મા"), ("{u", "મે"), ("{", "મ"),
    ("Lkt", "નં"), ("Lkk", "ના"), ("Lku", "ને"), ("Lk", "ન"),
    ("Ãkk", "પા"), ("Ãku", "પે"), ("Ãk", "પ"),

    # Standalone Vowel Marks
    ("kuh", "ૌ"), ("ku", "ો"), ("k", "ા"), ("u", "ે"), ("@", "ૈ"),
    ("w", "ુ"), ("q", "ૂ"), ("e", "ી"), ("]", "ૃ"),
    ("t", "ં"),
]


class GujaratiFontConverter:
    """Detects legacy 8-bit Gujarati font text and converts it to Unicode Gujarati."""

    @staticmethod
    def is_legacy_encoded(text: str) -> bool:
        """Determines whether a text block is likely encoded in a legacy Gujarati 8-bit font."""
        if not text or len(text.strip()) < 10:
            return False

        # Count characteristic legacy Gujarati markers
        legacy_markers = ["rð", "ƒk", "…k", "¾u", "Œe", "‚e", "Au", "y™u", "rMÚ", "Nu", "MŒ", "r{", "ýk", "þw", "»f"]
        match_count = sum(text.count(marker) for marker in legacy_markers)
        return match_count >= 3

    @classmethod
    def convert_to_unicode(cls, text: str) -> str:
        """Converts legacy font text to Unicode Gujarati."""
        if not text:
            return ""

        # Step 1: Pre-process 'r' for short-i ('િ')
        # In legacy fonts, 'r' appears before the consonant or conjunct.
        # e.g., 'rð' -> 'વિ', 'rMÚkrŒ' -> 'સ્થિતિ', 'r{r÷Þ™' -> 'મિલિયન', 'rðrðÄ' -> 'વિવિધ'
        
        converted = text
        for old, new in _CONJUNCT_MAP:
            converted = converted.replace(old, new)

        for old, new in _CHAR_MAP:
            converted = converted.replace(old, new)

        # Step 2: Handle remaining 'r' prefixes for short 'િ'
        # Match 'r' followed by a Gujarati consonant (U+0A95 to U+0AB9)
        converted = re.sub(r"r([\u0A95-\u0AB9\u0AE0])", r"\1િ", converted)
        
        # Step 3: Handle reph ('o' or '°' representing preceding 'ર્')
        # e.g., 'પયોાવરણ' -> 'પર્યાવરણ', 'કણોાટક' -> 'કર્ણાટક', 'અધો' -> 'અર્ધ'
        converted = re.sub(r"([\u0A95-\u0AB9])o", r"ર્\1", converted)
        converted = re.sub(r"([\u0A95-\u0AB9])°", r"ર્\1", converted)

        # Step 4: Clean up any duplicate matras or anomalies
        converted = re.sub(r"ાે", "ો", converted)
        converted = re.sub(r"ાૌ", "ૌ", converted)
        converted = re.sub(r"િિ+", "િ", converted)
        converted = re.sub(r"ીી+", "ી", converted)

        return converted


font_converter = GujaratiFontConverter()
