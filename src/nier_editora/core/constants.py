# =============================================================================
# Save file Sizes and Layout Adjustments
# =============================================================================
PC_SAVE_SIZE = 0x399CC
CONSOLE_SAVE_SIZE = 0x39990
CONSOLE_HEADER_SIZE = 12

# =============================================================================
# Offsets (Pc Layout)
# =============================================================================
# Header
OFF_HEADER_ID   = 0x00004
LEN_HEADER_ID   = 12

# Player stats
OFF_PLAYTIME    = 0x00024
OFF_CHAPTER     = 0x0002C
OFF_PLAYER_NAME = 0x00034
LEN_PLAYER_NAME = 70
OFF_GAMEWORLD_STATE = 0x0007C

# Currency & XP
OFF_MONEY       = 0x3056C
OFF_EXPERIENCE  = 0x3871C

# Inventory regions
OFF_INVENTORY   = 0x30570
OFF_CORPSE_INV  = 0x31170
OFF_WEAPONS     = 0x31D70
OFF_CHIPS       = 0x324BC

# =============================================================================
# Counts & Record Sizes
# =============================================================================
# Number of slots per category
INVENTORY_ITEM_COUNT = 256
CORPSE_INVENTORY_ITEM_COUNT = 256
INVENTORY_WEAPON_COUNT = 39
INVENTORY_CHIPS_COUNT = 256

# Bytes per record (int32 = 4bytes)
CHIP_PADDING = bytes([
    0xFF, 0xFF, 0xFF, 0xFF,     0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF,     0x00, 0x00, 0x00, 0x00,
])
CHIP_SIZE = 12 * 0x4      # baseCode, baseID, chipType, level, weight, slotA, slotB, slotC
CHIP_SIZE_WITHOUT_PADDING = CHIP_SIZE - len(CHIP_PADDING)
ITEM_SIZE = 3 * 0x4       # ID, status, quantity
WEAPON_SIZE = 5 * 0x4     # ID level, newItem, newStory, enemiesDefeated

# =============================================================================
# XP Table (https://nierautomata.wiki.fextralife.com/EXP)
# =============================================================================
EXPERIENCE_TABLE = {
    1: 0,            2: 48,          3: 139,         4: 294,         5: 525,
    6: 843,          7: 1259,        8: 1782,        9: 2421,       10: 3184,
    11: 4080,       12: 5116,       13: 6300,       14: 7638,       15: 9139,
    16: 10809,      17: 12654,      18: 14682,      19: 16898,      20: 19309,
    21: 21920,      22: 24739,      23: 27770,      24: 31019,      25: 34493,
    26: 38196,      27: 42134,      28: 46312,      29: 50736,      30: 55412,
    31: 60343,      32: 65536,      33: 70994,      34: 76724,      35: 82730,
    36: 89017,      37: 95590,      38: 102453,     39: 109611,     40: 117070,
    41: 124832,     42: 132904,     43: 141288,     44: 149991,     45: 159016,
    46: 168368,     47: 178051,     48: 188068,     49: 198426,     50: 209127,
    51: 220177,     52: 231578,     53: 243336,     54: 255454,     55: 267937,
    56: 280788,     57: 294011,     58: 307611,     59: 321591,     60: 335956,
    61: 350709,     62: 365854,     63: 381395,     64: 397336,     65: 413680,
    66: 430431,     67: 447594,     68: 465171,     69: 483167,     70: 501585,
    71: 520429,     72: 539702,     73: 559408,     74: 579552,     75: 600135,
    76: 621162,     77: 642637,     78: 664562,     79: 686942,     80: 709780,
    81: 733079,     82: 756843,     83: 781075,     84: 805779,     85: 830958,
    86: 856615,     87: 882754,     88: 909379,     89: 936491,     90: 964096,
    91: 992196,     92: 1020794,    93: 1049894,    94: 1079499,    95: 1109612,
    96: 1140237,    97: 1171376,    98: 1203033,    99: 1235211,
}

# =============================================================================
# Item List (https://bitbucket.org/Xutax_Kamay/nierautomata/src/da5adadd9f0f0637a7969ba3ea354f7cbdce17e2/ItemList.txt)
# =============================================================================
ITEM_LIST: dict[int, str] = {
      0: 'item_rec_S',                            1: 'item_rec_M',                    2: 'item_rec_L',
      3: 'item_rec_All',                         50: 'item_recSt_Elc',               60: 'item_recSt_Drk',
     70: 'item_recSt_Hrg',                       75: 'item_recSt_Ctrl',              80: 'item_recSt_All',
     90: 'item_recAll',                         100: 'item_stUp_pAtk_S',            102: 'item_stUp_pAtk_M',
    110: 'item_stUp_sAtk_S',                    112: 'item_stUp_sAtk_M',            120: 'item_stUp_pDef_S',
    122: 'item_stUp_pDef_M',                    130: 'item_stUp_sDef_S',            132: 'item_stUp_sDef_M',
    140: 'item_enCostDown_S',                   142: 'item_enCostDown_M',           150: 'item_sprAmr_S',
    152: 'item_sprAmr_M',                       160: 'item_sprDash_S',              162: 'item_sprDash_M',
    170: 'item_liquor',                         300: 'item_feed_S',                 330: 'item_goldUp_S',
    332: 'item_goldUp_M',                       400: 'item_dragA',                  410: 'item_fruits',
    510: 'item_mt_fell',                        515: 'item_mt_meat_boar',           516: 'item_mt_meat_deer',
    517: 'item_mt_meat_Aboar',                  518: 'item_mt_meat_Adeer',          520: 'item_mt_screw_S',
    521: 'item_mt_screw_M',                     525: 'item_mt_gear_S',              526: 'item_mt_gear_M',
    530: 'item_mt_mass_S',                      531: 'item_mt_mass_M',              535: 'item_mt_alloy_S',
    536: 'item_mt_alloy_M',                     540: 'item_mt_mainspring_S',        545: 'item_mt_battery_S',
    546: 'item_mt_battery_M',                   550: 'item_mt_cable_S',             551: 'item_mt_cable_M',
    555: 'item_mt_bolt_M',                      560: 'item_mt_nats_M',              570: 'item_mt_roboArm',
    571: 'item_mt_roboLeg',                     572: 'item_mt_roboBody',            573: 'item_mt_roboHead',
    580: 'item_mt_machine_S',                   581: 'item_mt_machine_M',           582: 'item_mt_machine_L',
    583: 'item_mt_refine_S',                    584: 'item_mt_refine_M',            585: 'item_mt_refine_L',
    600: 'item_mt_ore_S',                       601: 'item_mt_ore_M',               602: 'item_mt_ore_L',
    603: 'item_mt_ore_LL',                      610: 'item_mt_plate_S',             621: 'item_mt_seed',
    622: 'item_mt_sap',                         623: 'item_mt_water',               624: 'item_mt_nuts',
    625: 'item_mt_rose',                        626: 'item_mt_mushroom',            627: 'item_mt_book',
    628: 'item_mt_oil',                         629: 'item_mt_tanningAgent',        630: 'item_mt_fillerMetal',
    631: 'item_mt_dye',                         632: 'item_mt_pyrite',              633: 'item_mt_amber',
    634: 'item_mt_rubber',                      635: 'item_mt_bolt_S',              636: 'item_mt_nats_S',
    637: 'item_mt_bigEgg',                      638: 'item_mt_eagleEgg',            639: 'item_mt_blackPearl',
    640: 'item_mt_earrings',                    641: 'item_mt_bracelet',            642: 'item_mt_socket_M',
    643: 'item_mt_wire_S',                      644: 'item_mt_coil_S',              645: 'item_mt_socket_S',
    646: 'item_mt_circuit_S',                   680: 'item_mt_crystal',             681: 'item_mt_choker',
    682: 'item_mt_mask',                        683: 'item_mt_pierce',              684: 'item_mt_technicalBook',
    685: 'item_mt_dictionary',                  686: 'item_mt_pearl',               687: 'item_mt_moldavite',
    688: 'item_mt_meteorite',                   690: 'item_mt_blackBox',            691: 'item_mt_blackBox_pascal',
    692: 'item_mt_blackBox_children',           693: 'item_mt_pascalBook',          700: 'item_uq_q020_letter',
    701: 'item_uq_q020_glass',                  702: 'item_uq_q020_fossil',         703: 'item_uq_sartre_letter',
    715: 'item_uq_q140_memoryChip',             716: 'item_uq_q140_diary',          720: 'item_uq_q123_dataChip_A',
    721: 'item_uq_q123_dataChip_B',             722: 'item_uq_q123_dataChip_C',     723: 'item_uq_q123_dataChip_D',
    724: 'item_uq_q123_dataChip_E',             740: 'item_uq_q720_memento_A',      741: 'item_uq_q720_memento_B',
    742: 'item_uq_q720_memento_C',              743: 'item_uq_q720_memento_D',      750: 'item_uq_q121_musicBox',
    760: 'item_uq_q340_photo_1',                761: 'item_uq_q340_photo_2',        762: 'item_uq_q340_photo_3',
    775: 'item_uq_q650_q651_importantThing',    780: 'item_uq_q181_to21O_1',        781: 'item_uq_q181_to21O_2',
    782: 'item_uq_q181_to21O_3',                790: 'item_uq_q290_3colorCable_A',  791: 'item_uq_q291_3colorCable_B',
    792: 'item_uq_q292_3colorCable_C',          793: 'item_uq_q071_sundryGoods_1',  794: 'item_uq_q071_sundryGoods_2',
    795: 'item_uq_q071_sundryGoods_3',          796: 'item_uq_q071_sundryGoods_4',  797: 'item_uq_q071_sundryGoods_5',
    820: 'item_uq_accessKey_1',                 821: 'item_uq_accessKey_2',         822: 'item_uq_accessKey_3',
    832: 'item_uq_q440_roboParts',              833: 'item_uq_q660_stamp',          834: 'item_uq_q660_stampCard',
    835: 'item_uq_q590_heritage_1',             836: 'item_uq_q590_heritage_2',     837: 'item_uq_q590_heritage_3',
    838: 'item_uq_q590_heritage_4',             839: 'item_uq_q221_pascalReq_1',    840: 'item_uq_q222_pascalReq_2',
    841: 'item_uq_q640_confidentialInfo',       842: 'item_uq_pascalReq_3',         843: 'item_uq_memberCard',
    844: 'item_uq_resiBag',                     845: 'item_uq_mallKey',             850: 'item_uq_philosophyBook',
    851: 'item_uq_filter',                      852: 'item_uq_oil',                 870: 'item_uq_valveHead4',
    871: 'item_uq_noGoggles',                   872: 'item_uq_wig',                 873: 'item_uq_ribbon1',
    874: 'item_uq_ribbon2',                     875: 'item_uq_ExSand',              876: 'item_uq_ExForest',
    877: 'item_uq_matsudaMask',                 878: 'item_uq_satoMask',            880: 'item_uq_hairSpray_A',
    881: 'item_uq_hairSpray_B',                 882: 'item_uq_hairSpray_C',         883: 'item_uq_hairSpray_D',
    884: 'item_uq_hairSpray_E',                 885: 'item_uq_hairSpray_F',         886: 'item_uq_hairSpray_G',
    887: 'item_uq_hairSpray_H',                 888: 'item_uq_hairSpray_I',         889: 'item_uq_hairSpray_J',
    890: 'item_uq_hairSpray_K',                 891: 'item_uq_hairSpray_L',         892: 'item_uq_hairSpray_M',
    893: 'item_uq_hairSpray_N',                 894: 'item_uq_hairSpray_O',         895: 'item_uq_hairSpray_P',
    896: 'item_uq_hairSpray_Q',                 897: 'item_uq_hairSpray_R',         898: 'item_uq_hairSpray_S',
    920: 'item_uq_sachet_S',                    921: 'item_uq_sachet_M',            922: 'item_uq_sachet_L',
    930: 'item_uq_music_1',                     931: 'item_uq_music_2',             932: 'item_uq_music_3',
    933: 'item_uq_music_4',                     934: 'item_uq_music_5',             935: 'item_uq_music_6',
    936: 'item_uq_music_7',                     950: 'item_uq_podSkin1',            951: 'item_uq_podSkin2',
    952: 'item_uq_podSkin3',                    953: 'item_uq_podSkin4',            954: 'item_uq_podSkin5',
    955: 'item_uq_podSkin6',                    956: 'item_uq_podSkin7',            957: 'item_uq_podSkin8',
    958: 'item_uq_podSkin9',                    959: 'item_uq_podSkin10',           960: 'item_uq_gunSkin1',
    961: 'item_uq_gunSkin2',                    980: 'item_uq_changeCloth',         981: 'item_uq_changeArmour1',
    982: 'item_uq_changeArmour2',               983: 'item_uq_dlcCloth1',           984: 'item_uq_dlcCloth2',
    985: 'item_uq_dlcCloth3',                   990: 'item_uq_headdress_enemy',     991: 'item_uq_headdress_emile',
    992: 'item_uq_floralDecoration',            993: 'item_uq_emileMask',           994: 'item_uq_kingMask',
    995: 'item_uq_adamGlasses',                 996: 'item_uq_alienMask',           997: 'item_uq_valveHead1',
    998: 'item_uq_valveHead2',                  999: 'item_uq_valveHead3',

    1003: 'weapon_japanese_sword',      1013: 'weapon_pipe',                    1020: 'weapon_beastbain',
    1030: 'weapon_ancient_overload',    1040: 'weapon_phoenix_dagger',          1050: 'weapon_sf_sword',
    1060: 'weapon_uncouth_sword',       1070: 'weapon_white_sword',             1071: 'weapon_black_sword',
    1080: 'weapon_yoruha_sword',        1090: 'weapon_robo_sword',              1203: 'weapon_iron_will',
    1213: 'weapon_fang_of_the_twins',   1220: 'weapon_beastlord',               1230: 'weapon_phoenix_sword',
    1240: 'weapon_sf_large_sword',      1250: 'weapon_uncouth_large_sword',     1260: 'weapon_white_large_sword',
    1261: 'weapon_black_large_sword',   1270: 'weapon_robo_axe',                1400: 'weapon_phoenix_spear',
    1420: 'weapon_beastcurse',          1430: 'weapon_dragon_lance',            1440: 'weapon_spear_of_the_usurper',
    1450: 'weapon_sf_lance',            1460: 'weapon_uncouth_lance',           1470: 'weapon_white_lance',
    1471: 'weapon_black_lance',         1480: 'weapon_robo_lance',              1600: 'weapon_uncouth_combat',
    1610: 'weapon_sf_combat',           1620: 'weapon_white_combat',            1621: 'weapon_black_combat',
    1630: 'weapon_devil_combat',        1640: 'weapon_angel_combat',            1650: 'weapon_robo_arm',
    1875: 'weapon_ff_sword',            1876: 'weapon_dq_sword',                1877: 'weapon_dlc_combat',

    2001: 'skill_act_spear',            2002: 'skill_act_illusion',         2003: 'skill_act_hand',
    2004: 'skill_act_dance',            2005: 'skill_act_execution',        2006: 'skill_act_gluttony',
    2007: 'skill_act_barrier',          2008: 'skill_act_lash',             2009: 'skill_act_wire',
    2010: 'skill_act_fixedBattery',     2011: 'skill_act_slowBomb',         2012: 'skill_act_repair',
    2015: 'skill_act_smallBomb',        2019: 'skill_act_gravityBomb',      2021: 'skill_act_hold',
    2022: 'skill_act_ride',             2024: 'skill_act_sonar',

    3001: 'skill_psv_atkUp_0',
    3002: 'skill_psv_atkUp_1',          3003: 'skill_psv_atkUp_2',          3004: 'skill_psv_atkUp_3',
    3005: 'skill_psv_atkUp_4',          3006: 'skill_psv_atkUp_5',          3007: 'skill_psv_atkUp_6',
    3008: 'skill_psv_atkUp_7',          3009: 'skill_psv_atkUp_8',          3010: 'skill_psv_downAtkUp_0',
    3011: 'skill_psv_downAtkUp_1',      3012: 'skill_psv_downAtkUp_2',      3013: 'skill_psv_downAtkUp_3',
    3014: 'skill_psv_downAtkUp_4',      3015: 'skill_psv_downAtkUp_5',      3016: 'skill_psv_downAtkUp_6',
    3017: 'skill_psv_downAtkUp_7',      3018: 'skill_psv_downAtkUp_8',      3019: 'skill_psv_criticalUp_0',
    3020: 'skill_psv_criticalUp_1',     3021: 'skill_psv_criticalUp_2',     3022: 'skill_psv_criticalUp_3',
    3023: 'skill_psv_criticalUp_4',     3024: 'skill_psv_criticalUp_5',     3025: 'skill_psv_criticalUp_6',
    3026: 'skill_psv_criticalUp_7',     3027: 'skill_psv_criticalUp_8',     3028: 'skill_psv_podAtkUp_0',
    3029: 'skill_psv_podAtkUp_1',       3030: 'skill_psv_podAtkUp_2',       3031: 'skill_psv_podAtkUp_3',
    3032: 'skill_psv_podAtkUp_4',       3033: 'skill_psv_podAtkUp_5',       3034: 'skill_psv_podAtkUp_6',
    3035: 'skill_psv_podAtkUp_7',       3036: 'skill_psv_podAtkUp_8',       3037: 'skill_psv_coolTimeDown_0',
    3038: 'skill_psv_coolTimeDown_1',   3039: 'skill_psv_coolTimeDown_2',   3040: 'skill_psv_coolTimeDown_3',
    3041: 'skill_psv_coolTimeDown_4',   3042: 'skill_psv_coolTimeDown_5',   3043: 'skill_psv_coolTimeDown_6',
    3044: 'skill_psv_coolTimeDown_7',   3045: 'skill_psv_coolTimeDown_8',   3046: 'skill_psv_stDefUp_0',
    3047: 'skill_psv_stDefUp_1',        3048: 'skill_psv_stDefUp_2',        3049: 'skill_psv_stDefUp_3',
    3050: 'skill_psv_stDefUp_4',        3051: 'skill_psv_stDefUp_5',        3052: 'skill_psv_stDefUp_6',
    3053: 'skill_psv_stDefUp_7',        3054: 'skill_psv_stDefUp_8',        3055: 'skill_psv_enDefUp_0',
    3056: 'skill_psv_enDefUp_1',        3057: 'skill_psv_enDefUp_2',        3058: 'skill_psv_enDefUp_3',
    3059: 'skill_psv_enDefUp_4',        3060: 'skill_psv_enDefUp_5',        3061: 'skill_psv_enDefUp_6',
    3062: 'skill_psv_enDefUp_7',        3063: 'skill_psv_enDefUp_8',        3064: 'skill_psv_damageInv_0',
    3065: 'skill_psv_damageInv_1',      3066: 'skill_psv_damageInv_2',      3067: 'skill_psv_damageInv_3',
    3068: 'skill_psv_damageInv_4',      3069: 'skill_psv_damageInv_5',      3070: 'skill_psv_damageInv_6',
    3071: 'skill_psv_damageInv_7',      3072: 'skill_psv_damageInv_8',      3073: 'skill_psv_hpUp_0',
    3074: 'skill_psv_hpUp_1',           3075: 'skill_psv_hpUp_2',           3076: 'skill_psv_hpUp_3',
    3077: 'skill_psv_hpUp_4',           3078: 'skill_psv_hpUp_5',           3079: 'skill_psv_hpUp_6',
    3080: 'skill_psv_hpUp_7',           3081: 'skill_psv_hpUp_8',           3082: 'skill_psv_atkDrain_0',
    3083: 'skill_psv_atkDrain_1',       3084: 'skill_psv_atkDrain_2',       3085: 'skill_psv_atkDrain_3',
    3086: 'skill_psv_atkDrain_4',       3087: 'skill_psv_atkDrain_5',       3088: 'skill_psv_atkDrain_6',
    3089: 'skill_psv_atkDrain_7',       3090: 'skill_psv_atkDrain_8',       3091: 'skill_psv_defeatDrain_0',
    3092: 'skill_psv_defeatDrain_1',    3093: 'skill_psv_defeatDrain_2',    3094: 'skill_psv_defeatDrain_3',
    3095: 'skill_psv_defeatDrain_4',    3096: 'skill_psv_defeatDrain_5',    3097: 'skill_psv_defeatDrain_6',
    3098: 'skill_psv_defeatDrain_7',    3099: 'skill_psv_defeatDrain_8',    3100: 'skill_psv_autoRec_0',
    3101: 'skill_psv_autoRec_1',        3102: 'skill_psv_autoRec_2',        3103: 'skill_psv_autoRec_3',
    3104: 'skill_psv_autoRec_4',        3105: 'skill_psv_autoRec_5',        3106: 'skill_psv_autoRec_6',
    3107: 'skill_psv_autoRec_7',        3108: 'skill_psv_autoRec_8',        3109: 'skill_psv_avoidLenUp_0',
    3110: 'skill_psv_avoidLenUp_1',     3111: 'skill_psv_avoidLenUp_2',     3112: 'skill_psv_avoidLenUp_3',
    3113: 'skill_psv_avoidLenUp_4',     3114: 'skill_psv_avoidLenUp_5',     3115: 'skill_psv_avoidLenUp_6',
    3116: 'skill_psv_avoidLenUp_7',     3117: 'skill_psv_avoidLenUp_8',     3118: 'skill_psv_moveSpdUp_0',
    3119: 'skill_psv_moveSpdUp_1',      3120: 'skill_psv_moveSpdUp_2',      3121: 'skill_psv_moveSpdUp_3',
    3122: 'skill_psv_moveSpdUp_4',      3123: 'skill_psv_moveSpdUp_5',      3124: 'skill_psv_moveSpdUp_6',
    3125: 'skill_psv_moveSpdUp_7',      3126: 'skill_psv_moveSpdUp_8',      3127: 'skill_psv_itemDropUp_0',
    3128: 'skill_psv_itemDropUp_1',     3129: 'skill_psv_itemDropUp_2',     3130: 'skill_psv_itemDropUp_3',
    3131: 'skill_psv_itemDropUp_4',     3132: 'skill_psv_itemDropUp_5',     3133: 'skill_psv_itemDropUp_6',
    3134: 'skill_psv_itemDropUp_7',     3135: 'skill_psv_itemDropUp_8',     3136: 'skill_psv_expUp_0',
    3137: 'skill_psv_expUp_1',          3138: 'skill_psv_expUp_2',          3139: 'skill_psv_expUp_3',
    3140: 'skill_psv_expUp_4',          3141: 'skill_psv_expUp_5',          3142: 'skill_psv_expUp_6',
    3143: 'skill_psv_expUp_7',          3144: 'skill_psv_expUp_8',          3145: 'skill_psv_atkEffect_0',
    3146: 'skill_psv_atkEffect_1',      3147: 'skill_psv_atkEffect_2',      3148: 'skill_psv_atkEffect_3',
    3149: 'skill_psv_atkEffect_4',      3150: 'skill_psv_atkEffect_5',      3151: 'skill_psv_atkEffect_6',
    3152: 'skill_psv_atkEffect_7',      3153: 'skill_psv_atkEffect_8',      3154: 'skill_psv_berserk_0',
    3155: 'skill_psv_berserk_1',        3156: 'skill_psv_berserk_2',        3157: 'skill_psv_berserk_3',
    3158: 'skill_psv_berserk_4',        3159: 'skill_psv_berserk_5',        3160: 'skill_psv_berserk_6',
    3161: 'skill_psv_berserk_7',        3162: 'skill_psv_berserk_8',        3163: 'skill_psv_damageDrain_0',
    3164: 'skill_psv_damageDrain_1',    3165: 'skill_psv_damageDrain_2',    3166: 'skill_psv_damageDrain_3',
    3167: 'skill_psv_damageDrain_4',    3168: 'skill_psv_damageDrain_5',    3169: 'skill_psv_damageDrain_6',
    3170: 'skill_psv_damageDrain_7',    3171: 'skill_psv_damageDrain_8',    3172: 'skill_psv_autoReflect_0',
    3173: 'skill_psv_autoReflect_1',    3174: 'skill_psv_autoReflect_2',    3175: 'skill_psv_autoReflect_3',
    3176: 'skill_psv_autoReflect_4',    3177: 'skill_psv_autoReflect_5',    3178: 'skill_psv_autoReflect_6',
    3179: 'skill_psv_autoReflect_7',    3180: 'skill_psv_autoReflect_8',    3181: 'skill_psv_guts_0',
    3182: 'skill_psv_guts_1',           3183: 'skill_psv_guts_2',           3184: 'skill_psv_guts_3',
    3185: 'skill_psv_guts_4',           3186: 'skill_psv_guts_5',           3187: 'skill_psv_guts_6',
    3188: 'skill_psv_guts_7',           3189: 'skill_psv_guts_8',           3190: 'skill_psv_witchTime_0',
    3191: 'skill_psv_witchTime_1',      3192: 'skill_psv_witchTime_2',      3193: 'skill_psv_witchTime_3',
    3194: 'skill_psv_witchTime_4',      3195: 'skill_psv_witchTime_5',      3196: 'skill_psv_witchTime_6',
    3197: 'skill_psv_witchTime_7',      3198: 'skill_psv_witchTime_8',      3199: 'skill_psv_superArmour_0',
    3200: 'skill_psv_superArmour_1',    3201: 'skill_psv_superArmour_2',    3202: 'skill_psv_superArmour_3',
    3203: 'skill_psv_superArmour_4',    3204: 'skill_psv_superArmour_5',    3205: 'skill_psv_superArmour_6',
    3206: 'skill_psv_superArmour_7',    3207: 'skill_psv_superArmour_8',    3208: 'skill_psv_HUD_itemScan',
    3217: 'skill_psv_counterAction_0',  3218: 'skill_psv_counterAction_1',  3219: 'skill_psv_counterAction_2',
    3220: 'skill_psv_counterAction_3',  3221: 'skill_psv_counterAction_4',  3222: 'skill_psv_counterAction_5',
    3223: 'skill_psv_counterAction_6',  3224: 'skill_psv_counterAction_7',  3225: 'skill_psv_counterAction_8',
    3226: 'skill_psv_holdAction_0',     3227: 'skill_psv_holdAction_1',     3228: 'skill_psv_holdAction_2',
    3229: 'skill_psv_holdAction_3',     3230: 'skill_psv_holdAction_4',     3231: 'skill_psv_holdAction_5',
    3232: 'skill_psv_holdAction_6',     3233: 'skill_psv_holdAction_7',     3234: 'skill_psv_holdAction_8',
    3235: 'skill_psv_chargeAtk_0',      3236: 'skill_psv_chargeAtk_1',      3237: 'skill_psv_chargeAtk_2',
    3238: 'skill_psv_chargeAtk_3',      3239: 'skill_psv_chargeAtk_4',      3240: 'skill_psv_chargeAtk_5',
    3241: 'skill_psv_chargeAtk_6',      3242: 'skill_psv_chargeAtk_7',      3243: 'skill_psv_chargeAtk_8',
    3244: 'skill_psv_autoItem_0',       3245: 'skill_psv_autoItem_1',       3246: 'skill_psv_autoItem_2',
    3247: 'skill_psv_autoItem_3',       3248: 'skill_psv_autoItem_4',       3249: 'skill_psv_autoItem_5',
    3250: 'skill_psv_autoItem_6',       3251: 'skill_psv_autoItem_7',       3252: 'skill_psv_autoItem_8',
    3262: 'skill_psv_ctrlTimeUp_0',     3263: 'skill_psv_ctrlTimeUp_1',     3264: 'skill_psv_ctrlTimeUp_2',
    3265: 'skill_psv_ctrlTimeUp_3',     3266: 'skill_psv_ctrlTimeUp_4',     3267: 'skill_psv_ctrlTimeUp_5',
    3268: 'skill_psv_ctrlTimeUp_6',     3269: 'skill_psv_ctrlTimeUp_7',     3270: 'skill_psv_ctrlTimeUp_8',
    3289: 'skill_psv_stan_0',           3290: 'skill_psv_stan_1',           3291: 'skill_psv_stan_2',
    3292: 'skill_psv_stan_3',           3293: 'skill_psv_stan_4',           3294: 'skill_psv_stan_5',
    3295: 'skill_psv_stan_6',           3296: 'skill_psv_stan_7',           3297: 'skill_psv_stan_8',
    3298: 'skill_psv_burst_0',          3299: 'skill_psv_burst_1',          3300: 'skill_psv_burst_2',
    3301: 'skill_psv_burst_3',          3302: 'skill_psv_burst_4',          3303: 'skill_psv_burst_5',
    3304: 'skill_psv_burst_6',          3305: 'skill_psv_burst_7',          3306: 'skill_psv_burst_8',
    3325: 'skill_psv_dropRecUp_0',      3326: 'skill_psv_dropRecUp_1',      3327: 'skill_psv_dropRecUp_2',
    3328: 'skill_psv_dropRecUp_3',      3329: 'skill_psv_dropRecUp_4',      3330: 'skill_psv_dropRecUp_5',
    3331: 'skill_psv_dropRecUp_6',      3332: 'skill_psv_dropRecUp_7',      3333: 'skill_psv_dropRecUp_8',
    3334: 'skill_psv_deathAgony',       3335: 'skill_psv_baseHUD',          3336: 'skill_psv_soundIndicator',
    3337: 'skill_psv_enemyInfo',        3338: 'skill_psv_OS',               3339: 'skill_psv_bulletSlow',
    3340: 'skill_psv_comboContinue',    3341: 'skill_psv_bombExplosion',    3342: 'skill_psv_itemAdsorption',
    3343: 'skill_psv_HUD_skillGauge',   3344: 'skill_psv_HUD_log',          3345: 'skill_psv_HUD_miniMap',
    3346: 'skill_psv_HUD_expGauge',     3347: 'skill_psv_HUD_saveIcon',     3348: 'skill_psv_HUD_damage',
    3349: 'skill_psv_HUD_destination',  3350: 'skill_psv_HUD_automatic',    3353: 'skill_psv_HUD_fishZone',
    3354: 'skill_psv_auto_atk',         3355: 'skill_psv_auto_shoot',       3356: 'skill_psv_auto_avoid',
    3357: 'skill_psv_auto_pod',         3358: 'skill_psv_auto_weapon',      4001: 'capacity_1',
    4002: 'capacity_2',                 4003: 'capacity_3',                 4004: 'capacity_4',
    4006: 'capacity_6',                 4007: 'capacity_7',                 4008: 'capacity_8',

    5020: 'achievement_20', 5021: 'achievement_21', 5023: 'achievement_23', 5024: 'achievement_24',
    5025: 'achievement_25', 5026: 'achievement_26', 5027: 'achievement_27', 5028: 'achievement_28',
    5029: 'achievement_29', 5030: 'achievement_30', 5032: 'achievement_32', 5033: 'achievement_33',
    5034: 'achievement_34', 5035: 'achievement_35', 5036: 'achievement_36', 5037: 'achievement_37',
    5038: 'achievement_38', 5039: 'achievement_39', 5040: 'achievement_40', 5041: 'achievement_41',
    5042: 'achievement_42', 5043: 'achievement_43', 5044: 'achievement_44', 5045: 'achievement_45',
    5046: 'achievement_46', 5047: 'achievement_47',

    6001: 'composition_pod1', 6002: 'composition_pod2', 6003: 'composition_pod3',

    7001: 'picEvent_1', 7002: 'picEvent_2', 7003: 'picEvent_3', 7004: 'picEvent_4',  7005: 'picEvent_5',
    7006: 'picEvent_6', 7007: 'picEvent_7', 7008: 'picEvent_8', 7011: 'picEvent_11', 7012: 'picEvent_12',
    7013: 'picEvent_13',

    8001: 'fish_1',  8002: 'fish_2',  8003: 'fish_3',  8004: 'fish_4',  8005: 'fish_5',  8006: 'fish_6',
    8007: 'fish_7',  8008: 'fish_8',  8009: 'fish_9',  8010: 'fish_10', 8011: 'fish_11', 8012: 'fish_12',
    8013: 'fish_13', 8014: 'fish_14', 8015: 'fish_15', 8016: 'fish_16', 8017: 'fish_17', 8018: 'fish_18',
    8019: 'fish_19', 8020: 'fish_20', 8021: 'fish_21', 8022: 'fish_22', 8023: 'fish_23', 8024: 'fish_24',
    8025: 'fish_25', 8026: 'fish_26', 8027: 'fish_27', 8028: 'fish_28', 8029: 'fish_29', 8030: 'fish_30',
    8031: 'fish_31', 8032: 'fish_32', 8033: 'fish_33', 8034: 'fish_34', 8035: 'fish_35', 8036: 'fish_36',
    8037: 'fish_37', 8038: 'fish_38', 8039: 'fish_39', 8040: 'fish_40', 8041: 'fish_41',

    1020010: 'file_pearlHarbor_1',          1020020: 'file_pearlHarbor_2',          1020030: 'file_pearlHarbor_3',
    1020040: 'file_pearlHarbor_4',          1020050: 'file_pearlHarbor_5',          1020060: 'file_pearlHarbor_6',
    1020070: 'file_pearlHarbor_7',          1030010: 'file_memory_1',               1030020: 'file_memory_2',
    1030030: 'file_memory_3',               1040010: 'file_h_letter',               1050010: 'file_h_11BDesertion',
    1080010: 'file_h_bombRecipe',           1090010: 'file_robo_1',                 1090020: 'file_robo_2',
    1090030: 'file_robo_3',                 1090040: 'file_robo_4',                 1090060: 'file_robo_6',
    1090070: 'file_robo_7',                 1090080: 'file_robo_8',                 1100010: 'file_h_flyer_kj',
    1120010: 'file_eng_1',                  1120020: 'file_eng_2',                  1120030: 'file_eng_3',
    1130010: 'file_h_childMemory',          1140010: 'file_server_1',               1140020: 'file_server_2',
    1140030: 'file_server_3',               1150010: 'file_h_testament',            1160010: 'file_h_animalRoboMemory',
    1161050: 'file_h_robo_5',               1170010: 'file_lostInfo_factory_1',     1170020: 'file_lostInfo_factory_2',
    1170030: 'file_lostInfo_submerge_1',    1170040: 'file_lostInfo_park_1',        1170050: 'file_lostInfo_park_2',
    1170060: 'file_lostInfo_castle_1',      1170070: 'file_lostInfo_woods_1',       1170080: 'file_lostInfo_desert_1',
    1170090: 'file_lostInfo_ruins_1',       1170100: 'file_lostInfo_ruins_2',       1170105: 'file_lostInfo_ruins_3',
    1170110: 'file_lostInfo_ruins_4',       1170112: 'file_mysteryStone1',          1170114: 'file_mysteryStone2',
    1170116: 'file_mysteryStone3',          1170118: 'file_mysteryStone4',          1170120: 'file_report_1',
    1170130: 'file_report_2',               1170140: 'file_report_3',               1170150: 'file_report_4',
    1170160: 'file_report_5',               1170170: 'file_report_6',               1170180: 'file_report_7',
    1170190: 'file_report_8',               1170200: 'file_report_9',               1170210: 'file_report_10',
    1170220: 'file_report_11',              1180010: 'file_h_roboReport'
}