"""
Normalisation maps built from the values actually found in the AOP 2027 workbook.
Raw values are always kept next to the normalised ones.
"""
import re

# ---- activity type -> standard category ----------------------------------
ACTIVITY_CATEGORY = {
    "Meeting / workshop": ["ກອງປະຊຸມ", "ປະຊຸມ", "workshop", "meeting", "ປະຊຸມເຊີງປະຕິບັດ", "consultation",
                           "ປະຊຸມ ເພື່ອລາຍງານຜົນຂອງການກວດກາ"],
    "Training": ["ຝຶກອົບຮົມ", "ອົບຮົມ", "ການຝຶກອົບຮົມ", "ຝຶກອົບຮົມຢູ່ສະຖານທີ່", "training/implementation",
                 "ຝຶກອົບຮົມວຽກງານກວດກາ"],
    "Monitoring & supervision": ["ລົງຕິດຕາມຊຸກຍູ້", "ລົງຕິດຕາມ", "ຕິດຕາມຊຸມຍູ້", "ຕິດຕາມຊຸກຍູ້", "ຊຸກຍູ້ຕິດຕາມ",
                                 "ຕິດຕາມ", "m&e", "monitoring and suport", "s&m",
                                 "ຊຸກຍູ້ຕິດຕາມ ແລະ ອົບຮົມກັບທີ່"],
    "Administration & operating costs": ["ບໍລິຫານ", "operation", "admin", "ບໍລິຫານ/ປະຕິບັດການ",
                                         "ຄ່າໃຊ້ຈ່າຍໃນການບໍລິຫານ", "ບັດເຕີມໂທລະສັບ"],
    "Field implementation": ["ປະຕິບັດການ"],
    "Procurement (goods)": ["ຈັດຊື້", "ການຈັດຊື້", "procurement", "ຊື້ເຄື່ອງໃຊ້ຫ້ອງການ (it equipments)",
                            "ການຈັດສົ່ງສິນຄ້າ"],
    "Contracting / technical assistance": ["ຈັດຈ້າງ", "ta - local", "ການຈັດຊື້ (ta)"],
    "Systems & tools development": ["system development", "ການພັດທະນາເຄື່ອງມື", "ການດັດແກ້ຄູ່ມືແນະນໍາ",
                                    "ປັບປຸງຄູ່ມື ການກວດສອບພາຍໃນ ຂົງເຂດສາທາລະນະສຸກ"],
    "Personnel / salaries": ["ບຸກຄະລາກອນ"],
    "Incentives & subsidies": ["ເງິນອຸດໜູນ/ເງິນຈູງໃຈ", "ເງິນລາງວັນ"],
    "Patient support": ["ອຸດໜູນຄົນເຈັບ", "patient support", "ການຊ່ວຍເຫຼືອຄົນເຈັບ"],
    "Performance payments (QPS)": ["ການຈ່າຍເງິນ qps", "ການຈ່າຍເງິນ gets-c"],
    "Assessment & evaluation": ["ປະເມີນ qps", "ການປະເມີນ", "ການປະເມີນ qps"],
    "Audit & inspection": ["ການກວດສອບ"],
    "Printing / IEC": ["printing", "ເຜີຍແຜ່"],
    "Data collection": ["ການເກັບກໍາຂໍ້ມູນ"],
}
_ACT_LOOKUP = {v.lower(): k for k, vs in ACTIVITY_CATEGORY.items() for v in vs}
PROGRAMME_TAGS = {"gesi"}  # programme names typed where an activity type belongs

# keywords used to infer a category from the activity NAME when the type is missing/unusable
NAME_KEYWORDS = [
    ("Performance payments (QPS)", ["ຕາມຜົນຄະແນນ", "ສະໜອງງົບປະມານໃຫ້ສຸກສາລາ"]),
    ("Assessment & evaluation", ["ປະເມີນ", "assessment", "evaluation", "survey"]),
    ("Audit & inspection", ["ກວດສອບ", "audit", "inspection", "verification"]),
    ("Procurement (goods)", ["ຈັດຊື້", "procure", "purchase", "drugs", "vaccine", "test kit", "equipment",
                             "ອຸປະກອນ", "laptop", "computer", "vitamin", "medicine"]),
    ("Training", ["ອົບຮົມ", "training", "tot ", "refresher"]),
    ("Meeting / workshop", ["ກອງປະຊຸມ", "ປະຊຸມ", "meeting", "workshop", "consultation", "conference"]),
    ("Monitoring & supervision", ["ຕິດຕາມ", "ຊຸກຍູ້", "monitor", "supervis", "follow"]),
    ("Contracting / technical assistance", ["ຈັດຈ້າງ", "consultant", "ທີ່ປຶກສາ", "contract", "ສັນຍາ"]),
    ("Personnel / salaries", ["ເງິນເດືອນ", "salary", "allowance", "ພະນັກງານສັນຍາ"]),
    ("Incentives & subsidies", ["ຈູງໃຈ", "incentive", "ອຸດໜູນ", "subsid"]),
    ("Patient support", ["ຄົນເຈັບ", "patient", "transportation fee", "delivery"]),
    ("Printing / IEC", ["ພິມ", "print", "radio", "spot", "iec", "ເຜີຍແຜ່", "card"]),
    ("Administration & operating costs", ["ບໍລິຫານ", "administ", "office", "ເຄື່ອງໃຊ້ຫ້ອງການ", "insurance",
                                          "ປະກັນໄພ", "ນ້ຳມັນ", "fuel", "ສ້ອມແປງ"]),
    ("Systems & tools development", ["ພັດທະນາ", "develop", "system", "dhis2", "server", "software", "ລະບົບ"]),
    ("Transfers to sub-national level", ["ໂອນ", "transfer"]),
]


def activity_category(raw_type, name, name_alt=None):
    """Return (category, source, flag) where source in {given, inferred, unknown}."""
    t = (raw_type or "").strip().lower()
    if t and t in _ACT_LOOKUP:
        return _ACT_LOOKUP[t], "given", None
    flag = None
    if t in PROGRAMME_TAGS:
        flag = "programme tag used as activity type"
    elif t:
        flag = "free-text activity type"
    text = " ".join(x for x in (name, name_alt, raw_type) if x).lower()
    for cat, kws in NAME_KEYWORDS:
        if any(k in text for k in kws):
            return cat, "inferred from name", flag
    return "Unclassified", "unknown", flag


# ---- implementing agency -------------------------------------------------
PROVINCES = {
    "Phongsaly": ["phongsaly", "ຜົ້ງສາລີ"], "Luang Namtha": ["luangnamtha", "lnt", "ຫຼວງນ້ຳທາ"],
    "Oudomxay": ["odomsay", "oudomxay", "ອຸດົມໄຊ"], "Bokeo": ["bokeo", "bk", "ບໍ່ແກ້ວ"],
    "Luang Prabang": ["luangprabang", "lpb", "ຫຼວງພະບາງ"], "Houaphanh": ["huaphan", "houaphanh", "ຫົວພັນ"],
    "Xayaboury": ["xayabouly", "xayaboury", "ໄຊຍະບູລີ"], "Xiengkhouang": ["xiengkhouang", "xkh", "xk", "ຊຽງຂວາງ"],
    "Vientiane Province": ["vientiane", "ວຽງຈັນ"], "Bolikhamxay": ["bolikhamsay", "blkx", "ບໍລິຄຳໄຊ"],
    "Khammouane": ["khammouan", "khammouane", "ຄຳມ່ວນ"], "Savannakhet": ["savannakhet", "ສະຫວັນນະເຂດ"],
    "Salavan": ["salavan", "ສາລະວັນ"], "Sekong": ["sekong", "ເຊກອງ"], "Champasak": ["champasack", "champasak", "ຈຳປາສັກ"],
    "Attapeu": ["attapeu", "atp", "ອັດຕະປື"], "Xaysomboun": ["xaysomboun", "ssb", "ໄຊສົມບູນ"],
    "Vientiane Capital": ["vientianecapital", "vientiane capital", "ນະຄອນຫຼວງ"],
}
_PROV_LOOKUP = {a: k for k, al in PROVINCES.items() for a in al}

AGENCIES = {
    # canonical: (level, aliases)
    "NCLE (Lab & Epidemiology Centre)": ("Central", ["ncle"]),
    "DCDC (Communicable Disease Control)": ("Central", ["dcdc"]),
    "CHAS (HIV/AIDS & STI Centre)": ("Central", ["chas"]),
    "NTC (National TB Centre)": ("Central", ["ntc"]),
    "NHIB (Health Insurance Bureau)": ("Central", ["nhib"]),
    "DHR (Healthcare & Rehabilitation)": ("Central", ["dhr"]),
    "DHHP (Hygiene & Health Promotion)": ("Central", ["ກົມອະນາໄມ ແລະ ສົ່ງເສີມສຸຂະພາບ", "dhhp"]),
    "Cabinet (MoH)": ("Central", ["cabinet", "central"]),
    "DO (Organisation & Personnel)": ("Central", ["do"]),
    "DIO (Inspection)": ("Central", ["dio"]),
    "MCHC (Mother & Child Health Centre)": ("Central", ["ສູນແມ່ແລະເດັກ", "mchc"]),
    "CHIS (Health Statistics & Information)": ("Central", ["ສູນສະຖິຕິ ແລະ ຂ່າວສານສາທາລະນະສຸກ"]),
    "CN (Centre of Nutrition)": ("Central", ["cn", "ສູນໂພຊະນາການ", "nc"]),
    "FDD (Food & Drug Department)": ("Central", ["fdd"]),
    "DPF (Planning & Finance)": ("Central", ["dpf", "ກົມແຜນການ ແລະ ການເງິນ", "ພະແນກສະຖິຕິ ແລະ ດິຈິຕອນ (ກມຜ)"]),
    "MPSC (Medical Products Supply Centre)": ("Central", ["mpsc"]),
    "NPCO (Project Coordination Office)": ("Central", ["npco"]),
    "Consultant firm / DPF": ("Central", ["ບໍລິສັດທີ່ປຶກສາ / ກມຜ"]),
    "PHO (Provincial Health Office)": ("Province", ["pho"]),
    "DHO (District Health Office)": ("District", ["dho"]),
    "DHO / Health centres": ("District", ["dho/hc"]),
    "CHIAs (civil society)": ("Civil society", ["chias"]),
    "PEDA (civil society)": ("Civil society", ["peda"]),
    "APL+ (civil society)": ("Civil society", ["apl+"]),
    "APDWL (civil society)": ("Civil society", ["apdwl"]),
}
_AG_LOOKUP = {a: (k, lvl) for k, (lvl, al) in AGENCIES.items() for a in al}


def implementing_agency(raw, level_col=None):
    """Return (agency, level, flag)."""
    if not raw:
        return None, level_col, None
    s = raw.strip()
    key = s.lower()
    if key in _AG_LOOKUP:
        ag, lvl = _AG_LOOKUP[key]
        return ag, level_col or lvl, None
    if key.replace(" ", "") in _PROV_LOOKUP or key in _PROV_LOOKUP:
        prov = _PROV_LOOKUP.get(key, _PROV_LOOKUP.get(key.replace(" ", "")))
        return f"PHO – {prov}", "Province", None
    if len(s) > 60:
        return None, level_col, "note/sentence typed in the implementing-agency field"
    if re.search(r"[,/&+]| and ", s) or "(" in s:
        return "Multiple agencies: " + s, level_col or "Multiple", None
    return s, level_col, "agency not in reference list"


# ---- unit ------------------------------------------------------------------
UNITS = {
    "time / event": ["ຄັ້ງ", "time", "ຄັ້້ງ"],
    "quarter": ["ໄຕມາດ", "quarter", "quartely"],
    "month": ["ເດືອນ"],
    "year": ["ປີ", "annum", "year"],
    "person": ["ຄົນ", "member"],
    "province": ["ແຂວງ"],
    "district": ["ເມືອງ"],
    "health centre": ["ສຸກສາລາ"],
    "trip": ["ຖ້ຽວ"],
    "site": ["ແຫ່ງ"],
    "set": ["ຊຸດ"],
    "contract": ["ສັນຍາ"],
    "USD (lump sum)": ["ໂດລາ"],
}
_UNIT_LOOKUP = {a: k for k, al in UNITS.items() for a in al}


def unit(raw):
    """Return (unit, flag)."""
    if not raw:
        return None, None
    s = str(raw).strip()
    key = s.lower()
    if key in _UNIT_LOOKUP:
        flag = None
        if s == "ຄັ້້ງ":
            flag = "misspelt unit (duplicated vowel mark)"
        elif s == "ໂດລາ":
            flag = "currency used as unit of measure"
        return _UNIT_LOOKUP[key], flag
    m = re.match(r"^(\d+)\s*(.+)$", s)
    if m and m.group(2).lower() in _UNIT_LOOKUP:
        return _UNIT_LOOKUP[m.group(2).lower()], f"quantity '{m.group(1)}' typed into the unit field"
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return None, "number typed into the unit field"
    return s, "unit not in reference list"
